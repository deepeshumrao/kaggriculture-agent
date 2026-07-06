"""SecurityMonitor — orchestrates all four threat defenses.

Usage in the agent loop:
    monitor = SecurityMonitor()
    monitor.before_turn()                      # threat 4: turn cap
    state, _ = monitor.check_state(state)      # threat 3: poisoning
    monitor.check_llm_prompt(prompt)           # threat 1: injection (pre-call)
    monitor.register_llm_call()                # threat 4: call cap
    monitor.check_llm_response(text)           # threat 1+2: injection/secret/size

Every block raises SecurityViolation and logs a "SECURITY VIOLATION" line.
Secret scrubbing is applied to everything logged.
"""

from __future__ import annotations

from ..config import CONFIG
from ..logging_setup import get_logger
from ..types import GameState
from .budget import BudgetMonitor
from .injection import detect_injection
from .scrubber import scrub
from .validation import sanitize_state
from .violations import SecurityViolation, ThreatType

_log = get_logger()


class SecurityMonitor:
    def __init__(
        self,
        budget: BudgetMonitor | None = None,
        block_on_injection: bool = True,
    ) -> None:
        self.budget = budget or BudgetMonitor()
        self.block_on_injection = block_on_injection
        self.violations: list[str] = []

    # ---- logging helper ---------------------------------------------------- #
    def _record(self, threat: ThreatType, detail: str, *, halt: bool) -> None:
        line = f"SECURITY VIOLATION [{threat.value}] {detail}"
        self.violations.append(scrub(line))
        _log.warning(scrub(line))
        if halt:
            raise SecurityViolation(threat, detail)

    # ---- per-episode lifecycle -------------------------------------------- #
    def begin_episode(self) -> None:
        """Reset per-run budget counters at the start of each game so the
        turn / LLM-call caps do not accumulate across a multi-game evaluation."""
        self.budget.reset()

    # ---- Threat 4: unbounded execution ------------------------------------ #
    def before_turn(self) -> None:
        self.budget.tick_turn()

    def register_llm_call(self) -> None:
        self.budget.tick_llm_call()

    # ---- Threat 3: data poisoning ----------------------------------------- #
    def check_state(self, state: GameState) -> GameState:
        safe, issues = sanitize_state(state)
        for issue in issues:
            # Poisoned data is sanitized (not fatal) but logged as a violation.
            self._record(ThreatType.DATA_POISONING, issue, halt=False)
        return safe

    # ---- Threat 1: injection in an outgoing prompt ------------------------- #
    def check_llm_prompt(self, prompt: str) -> None:
        hits = detect_injection(prompt)
        if hits:
            self._record(
                ThreatType.PROMPT_INJECTION,
                f"injection detected in outbound prompt: {hits[:3]}",
                halt=self.block_on_injection,
            )

    # ---- Threat 1+2+size: the model's response ---------------------------- #
    def check_llm_response(self, text: str) -> str:
        if text is None:
            return ""
        if len(text) > CONFIG.max_llm_response_chars:
            self._record(
                ThreatType.DENIAL_OF_WALLET,
                f"oversized LLM response ({len(text)} chars) -> rejected",
                halt=True,
            )
        hits = detect_injection(text)
        if hits:
            self._record(
                ThreatType.PROMPT_INJECTION,
                f"injection detected in LLM response: {hits[:3]}",
                halt=self.block_on_injection,
            )
        # Never let a secret pass through from a model echo.
        return scrub(text)

    # ---- summary ---------------------------------------------------------- #
    def summary(self) -> dict:
        return {
            "violations": len(self.violations),
            "budget": self.budget.snapshot(),
        }
