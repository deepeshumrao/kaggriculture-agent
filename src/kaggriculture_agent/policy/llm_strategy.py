"""Optional Gemini-powered strategy.

Falls back gracefully to the heuristic strategy if the SDK or API key is missing,
or if the model returns something unparseable. This keeps the project runnable
with zero cost/setup while allowing an LLM brain when desired.
"""

from __future__ import annotations

import json
import time

from ..config import CONFIG
from ..logging_setup import get_logger
from ..memory.knowledge import Knowledge
from ..memory.state import EpisodeState
from ..security.violations import SecurityViolation
from ..types import Action, ActionType, GameState
from . import prompts
from .strategy import HeuristicStrategy, Strategy

_log = get_logger()

# After this many consecutive LLM failures we stop calling the API for the rest
# of the run and use the heuristic — avoids hammering an exhausted quota.
_MAX_CONSECUTIVE_FAILURES = 3
_MAX_RETRIES = 2          # per-turn retries on transient errors
_BACKOFF_SECONDS = 1.0    # base backoff, doubled each retry


class LLMStrategy(Strategy):
    def __init__(self) -> None:
        self._fallback = HeuristicStrategy()
        self._client = None
        self._consecutive_failures = 0
        self._disabled = False  # trip after too many failures
        self._security = None   # set via attach_security()
        self._init_client()

    def attach_security(self, monitor) -> None:
        """Wire the SecurityMonitor so the LLM path is fully guarded."""
        self._security = monitor

    def _init_client(self) -> None:
        if not CONFIG.api_key:
            _log.info("No API key set; LLM policy will use the heuristic fallback.")
            return
        try:  # import lazily so the project runs without the SDK installed
            from google import genai

            self._client = genai.Client(api_key=CONFIG.api_key)
            _log.info("Gemini client initialized (model=%s).", CONFIG.model)
        except Exception as exc:  # SDK missing or client init failed
            _log.warning("Could not init Gemini client (%s); using heuristic.", exc)
            self._client = None

    def decide(
        self, state: GameState, episode: EpisodeState, knowledge: Knowledge
    ) -> Action:
        if self._client is None or self._disabled:
            return self._fallback.decide(state, episode, knowledge)
        try:
            action = self._ask_llm_with_retries(state, knowledge)
            if action is not None:
                self._consecutive_failures = 0
                return action
            _log.debug("LLM returned no usable action; using heuristic this turn.")
        except SecurityViolation:
            # Security halts (e.g. denial-of-wallet) must propagate, not fall back.
            raise
        except Exception as exc:  # last-resort guard: never break the game loop
            _log.warning("LLM decide() failed (%s); using heuristic this turn.", exc)

        self._register_failure()
        return self._fallback.decide(state, episode, knowledge)

    def _register_failure(self) -> None:
        self._consecutive_failures += 1
        if self._consecutive_failures >= _MAX_CONSECUTIVE_FAILURES:
            self._disabled = True
            _log.warning(
                "Disabling LLM after %d consecutive failures; running on heuristic "
                "for the rest of this run.",
                self._consecutive_failures,
            )

    def _ask_llm_with_retries(
        self, state: GameState, knowledge: Knowledge
    ) -> Action | None:
        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRIES + 1):
            try:
                return self._ask_llm(state, knowledge)
            except Exception as exc:
                last_exc = exc
                if not _is_transient(exc) or attempt == _MAX_RETRIES:
                    raise
                wait = _BACKOFF_SECONDS * (2 ** attempt)
                _log.info(
                    "Transient LLM error (%s); retry %d/%d in %.1fs.",
                    type(exc).__name__, attempt + 1, _MAX_RETRIES, wait,
                )
                time.sleep(wait)
        if last_exc:
            raise last_exc
        return None

    def _ask_llm(self, state: GameState, knowledge: Knowledge) -> Action | None:
        state_json = json.dumps(_state_to_dict(state), default=str)
        best = knowledge.best_known_crop()
        note = f"Historically most profitable crop: {best}" if best else "No history yet."
        user = prompts.build_user_prompt(state_json, note)

        # Threat 1: scan the outbound prompt for injected instructions
        # (data poisoning that reached the prompt via crop names / messages).
        if self._security is not None:
            self._security.check_llm_prompt(user)
            # Threat 4: count the call against the wallet budget BEFORE spending.
            self._security.register_llm_call()

        resp = self._client.models.generate_content(
            model=CONFIG.model,
            contents=[prompts.SYSTEM_PROMPT, user],
        )
        text = (resp.text or "").strip()

        # Threat 1+2: block hijacking attempts / scrub secrets in the response.
        if self._security is not None:
            text = self._security.check_llm_response(text)

        return _parse_action(text)


def _is_transient(exc: Exception) -> bool:
    """True for errors worth retrying (rate limits, timeouts, 5xx)."""
    msg = str(exc).lower()
    transient_markers = ("429", "resource_exhausted", "rate", "timeout",
                         "503", "500", "unavailable", "deadline")
    return any(m in msg for m in transient_markers)


def _state_to_dict(state: GameState) -> dict:
    return {
        "day": state.day,
        "days_left": state.days_left,
        "cash": state.cash,
        "weather": state.weather.value,
        "forecast": [w.value for w in state.forecast],
        "market_prices": state.market_prices,
        "inventory": state.inventory,
        "plots": [
            {
                "index": p.index,
                "crop": p.crop,
                "age": p.age,
                "water_level": p.water_level,
                "fertilized": p.fertilized,
                "health": p.health,
                "ready": p.ready,
            }
            for p in state.plots
        ],
    }


def _parse_action(text: str) -> Action | None:
    # Strip code fences if present.
    if "```" in text:
        text = text.split("```")[1].replace("json", "", 1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    try:
        return Action(
            type=ActionType(data["type"]),
            plot_index=data.get("plot_index"),
            crop=data.get("crop"),
            amount=data.get("amount"),
        )
    except (KeyError, ValueError):
        return None
