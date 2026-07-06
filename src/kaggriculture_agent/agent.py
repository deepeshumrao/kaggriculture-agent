"""The Kaggriculture agent: ties sim + policy + guardrails + memory together.

`Agent.play_episode()` runs one full game and returns the final score plus a
trace. This is the entrypoint used by scripts and tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .config import CONFIG
from .errors import SimError
from .logging_setup import get_logger
from .memory.knowledge import Knowledge
from .memory.state import EpisodeState
from .policy.guardrails import sanitize
from .policy.strategy import HeuristicStrategy, Strategy
from .security.violations import SecurityViolation
from .sim.base import SimClient
from .types import Action, ActionType

_log = get_logger()


@dataclass
class EpisodeResult:
    score: float
    days: int
    trace: list[str] = field(default_factory=list)


def build_strategy() -> Strategy:
    """Pick the policy from config; LLM falls back to heuristic automatically."""
    if CONFIG.policy == "llm":
        from .policy.llm_strategy import LLMStrategy

        return LLMStrategy()
    return HeuristicStrategy()


class Agent:
    def __init__(
        self,
        strategy: Strategy | None = None,
        knowledge: Knowledge | None = None,
        verbose: bool = False,
        security: "SecurityMonitor | None" = None,
    ) -> None:
        from .security import SecurityMonitor

        self.strategy = strategy or build_strategy()
        self.knowledge = knowledge or Knowledge()
        self.verbose = verbose
        self.security = security or SecurityMonitor()
        # Give the policy access to the same monitor (used by the LLM policy).
        if hasattr(self.strategy, "attach_security"):
            self.strategy.attach_security(self.security)

    def play_episode(self, sim: SimClient, max_steps: int = 1000) -> EpisodeResult:
        state = sim.reset()
        episode = EpisodeState()
        trace: list[str] = []

        # Per-game safety caps reset each episode (long-term Knowledge persists).
        self.security.begin_episode()

        steps = 0
        while not state.done and steps < max_steps:
            # Threat 4: hard turn cap (halts on runaway loops).
            self.security.before_turn()
            # Threat 3: sanitize possibly-poisoned data from the sim.
            state = self.security.check_state(state)

            episode.observe(state)

            # Policy failures must never crash the game: fall back to WAIT.
            # EXCEPT security halts (denial-of-wallet, hijack) which must stop.
            try:
                raw = self.strategy.decide(state, episode, self.knowledge)
            except SecurityViolation:
                raise
            except Exception as exc:
                _log.warning("Strategy raised (%s); defaulting to WAIT.", exc)
                raw = Action(ActionType.WAIT)

            action = sanitize(raw, state)  # never let an illegal action through

            # A sim backend error ends the episode gracefully with the score so far.
            try:
                result = sim.step(action)
            except Exception as exc:
                _log.error("Sim.step failed (%s); ending episode early.", exc)
                raise SimError(f"simulation failed on step {steps}: {exc}") from exc

            episode.record_action(action, result.reward)

            if action.type == ActionType.SELL and action.crop:
                self.knowledge.record_crop_profit(action.crop, result.reward)

            if self.verbose:
                line = (
                    f"day {state.day:>2} | {str(action):<28} "
                    f"| cash {result.state.cash:>8.2f} | {result.message}"
                )
                trace.append(line)
                print(line)

            state = result.state
            steps += 1

        score = round(state.cash, 2)
        return EpisodeResult(score=score, days=state.day, trace=trace)
