"""A naive baseline agent to measure our real agent against.

Strategy: plant the cheapest crop on any empty plot, harvest when ready, sell
immediately at whatever price. No watering, no fertilizing, no market timing.
This is the bar the real agent must clear.
"""

from __future__ import annotations

from .memory.knowledge import Knowledge
from .memory.state import EpisodeState
from .policy.guardrails import sanitize
from .policy.strategy import Strategy
from .sim.crops import CROPS
from .types import Action, ActionType, GameState


class NaiveStrategy(Strategy):
    def decide(
        self, state: GameState, episode: EpisodeState, knowledge: Knowledge
    ) -> Action:
        # Sell everything immediately.
        for crop, units in state.inventory.items():
            if units > 0:
                return Action(ActionType.SELL, crop=crop)
        # Harvest anything ready.
        for plot in state.plots:
            if plot.crop is not None and plot.ready:
                return Action(ActionType.HARVEST, plot_index=plot.index)
        # Plant the cheapest crop that can still mature.
        cheapest = min(CROPS.values(), key=lambda c: c.seed_cost)
        if cheapest.days_to_mature <= state.days_left and state.cash >= cheapest.seed_cost:
            for plot in state.plots:
                if plot.crop is None:
                    return Action(
                        ActionType.PLANT, plot_index=plot.index, crop=cheapest.name
                    )
        return Action(ActionType.WAIT)
