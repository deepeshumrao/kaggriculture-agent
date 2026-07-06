"""Cross-episode knowledge (long-term memory).

Accumulates average realized profit per crop across many games so the agent can
prefer historically profitable crops. Kept in-memory here; can be persisted to
JSON later for true cross-run learning.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Knowledge:
    _profit_sum: dict[str, float] = field(default_factory=dict)
    _profit_count: dict[str, int] = field(default_factory=dict)

    def record_crop_profit(self, crop: str, profit: float) -> None:
        self._profit_sum[crop] = self._profit_sum.get(crop, 0.0) + profit
        self._profit_count[crop] = self._profit_count.get(crop, 0) + 1

    def avg_profit(self, crop: str) -> float:
        n = self._profit_count.get(crop, 0)
        if n == 0:
            return 0.0
        return self._profit_sum[crop] / n

    def best_known_crop(self) -> str | None:
        if not self._profit_count:
            return None
        return max(self._profit_count, key=lambda c: self.avg_profit(c))
