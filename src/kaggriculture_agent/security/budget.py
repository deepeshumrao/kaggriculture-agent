"""Threat 4 — Denial of Wallet (unbounded execution) enforcement.

Tracks turns and LLM API calls against the hard caps in config.py. When a cap is
exceeded, raises SecurityViolation so the run halts before it can rack up cost.
"""

from __future__ import annotations

from ..config import CONFIG
from .violations import SecurityViolation, ThreatType


class BudgetMonitor:
    def __init__(
        self,
        max_turns: int | None = None,
        max_llm_calls: int | None = None,
    ) -> None:
        self.max_turns = max_turns if max_turns is not None else CONFIG.max_turns
        self.max_llm_calls = (
            max_llm_calls if max_llm_calls is not None else CONFIG.max_llm_calls
        )
        self.turns = 0
        self.llm_calls = 0

    def reset(self) -> None:
        """Clear per-run counters. The turn / LLM-call caps are per-episode
        safety limits, so a reused monitor must reset between games."""
        self.turns = 0
        self.llm_calls = 0

    def tick_turn(self) -> None:
        self.turns += 1
        if self.turns > self.max_turns:
            raise SecurityViolation(
                ThreatType.DENIAL_OF_WALLET,
                f"turn limit exceeded ({self.turns} > {self.max_turns}); halting.",
            )

    def tick_llm_call(self) -> None:
        self.llm_calls += 1
        if self.llm_calls > self.max_llm_calls:
            raise SecurityViolation(
                ThreatType.DENIAL_OF_WALLET,
                f"LLM call limit exceeded ({self.llm_calls} > {self.max_llm_calls}); halting.",
            )

    def snapshot(self) -> dict:
        return {
            "turns": self.turns,
            "max_turns": self.max_turns,
            "llm_calls": self.llm_calls,
            "max_llm_calls": self.max_llm_calls,
        }
