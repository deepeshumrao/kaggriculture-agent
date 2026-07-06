"""Decision policies.

`HeuristicStrategy` is the default: fast, free, deterministic, and already a
strong player. It follows a priority order each turn:

  1. SELL harvested inventory when the price is relatively high.
  2. HARVEST any ready crop.
  3. FERTILIZE a valuable crop if a storm is forecast.
  4. WATER a crop that is behind on its water need.
  5. PLANT the most profitable crop on an empty plot (if time allows).
  6. WAIT otherwise.

The LLM strategy lives in `llm_strategy.py` and is optional.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..config import CONFIG
from ..memory.knowledge import Knowledge
from ..memory.state import EpisodeState
from ..sim.crops import CROPS
from ..types import Action, ActionType, GameState, Weather


class Strategy(ABC):
    @abstractmethod
    def decide(
        self, state: GameState, episode: EpisodeState, knowledge: Knowledge
    ) -> Action:
        ...


class HeuristicStrategy(Strategy):
    """A strong, explainable rule-based farmer."""

    def decide(
        self, state: GameState, episode: EpisodeState, knowledge: Knowledge
    ) -> Action:
        # 1. Sell inventory when the price looks high.
        sell = self._maybe_sell(state, episode)
        if sell:
            return sell

        # 2. Harvest anything ready.
        for plot in state.plots:
            if plot.crop is not None and plot.ready:
                return Action(ActionType.HARVEST, plot_index=plot.index)

        # 3. Fertilize a valuable, unprotected crop if a storm is coming.
        if Weather.STORM in state.forecast[:1]:
            for plot in state.plots:
                if (
                    plot.crop is not None
                    and not plot.fertilized
                    and not plot.ready
                    and state.cash >= CONFIG.min_cash_reserve + 8.0
                ):
                    return Action(ActionType.FERTILIZE, plot_index=plot.index)

        # 4. Water a crop that is behind on water.
        for plot in state.plots:
            if plot.crop is not None and not plot.ready:
                crop = CROPS[plot.crop]
                if plot.water_level < crop.water_need:
                    return Action(ActionType.WATER, plot_index=plot.index)

        # 5. Plant on an empty plot if there is time to mature.
        plant = self._maybe_plant(state, knowledge)
        if plant:
            return plant

        # 6. Nothing useful to do.
        return Action(ActionType.WAIT)

    # ------------------------------------------------------------------ #
    def _maybe_sell(self, state: GameState, episode: EpisodeState) -> Action | None:
        best: tuple[float, str] | None = None
        for crop, units in state.inventory.items():
            if units <= 0:
                continue
            price = state.market_prices.get(crop, 0.0)
            pct = episode.price_percentile(crop, price)
            # Sell if price is high, or if the game is almost over (avoid waste).
            if pct >= CONFIG.sell_price_percentile or state.days_left <= 1:
                score = price * units
                if best is None or score > best[0]:
                    best = (score, crop)
        if best:
            return Action(ActionType.SELL, crop=best[1])
        return None

    def _maybe_plant(self, state: GameState, knowledge: Knowledge) -> Action | None:
        empty = [p for p in state.plots if p.crop is None]
        if not empty:
            return None

        # Rank crops by expected profit given current prices and time left.
        best_crop: str | None = None
        best_value = float("-inf")
        for name, crop in CROPS.items():
            if crop.days_to_mature > state.days_left:
                continue  # won't mature in time
            if state.cash < crop.seed_cost + CONFIG.min_cash_reserve:
                continue  # can't afford while keeping reserve
            price = state.market_prices.get(name, 0.0)
            expected_revenue = crop.base_yield * price
            expected_profit = expected_revenue - crop.seed_cost
            # Nudge by long-term knowledge of what has paid off before.
            expected_profit += 0.25 * knowledge.avg_profit(name)
            if expected_profit > best_value:
                best_value = expected_profit
                best_crop = name

        if best_crop and best_value > 0:
            return Action(ActionType.PLANT, plot_index=empty[0].index, crop=best_crop)
        return None
