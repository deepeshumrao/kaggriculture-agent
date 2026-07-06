"""Per-episode working memory (a 'session').

Tracks what has happened this game so the strategy can reason about recent
prices, weather, and its own actions without re-deriving them each turn.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..types import Action, GameState, Weather


@dataclass
class EpisodeState:
    price_history: dict[str, list[float]] = field(default_factory=dict)
    weather_history: list[Weather] = field(default_factory=list)
    actions_taken: list[str] = field(default_factory=list)
    total_reward: float = 0.0

    def observe(self, state: GameState) -> None:
        for crop, price in state.market_prices.items():
            self.price_history.setdefault(crop, []).append(price)
        self.weather_history.append(state.weather)

    def record_action(self, action: Action, reward: float) -> None:
        self.actions_taken.append(str(action))
        self.total_reward += reward

    def price_percentile(self, crop: str, price: float) -> float:
        """Where does `price` rank within this crop's observed history (0..1)?"""
        history = self.price_history.get(crop, [])
        if not history:
            return 0.5
        below = sum(1 for p in history if p <= price)
        return below / len(history)
