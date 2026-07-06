"""A self-contained, deterministic-by-seed mock farming simulation.

It implements `SimClient` so the whole agent runs end-to-end with no external
dependencies. Mechanics are simple but non-trivial: crops grow over days, need
water, suffer in drought, die in storms if unfertilized, and sell at fluctuating
market prices. Score = final cash (+ unsold inventory valued at last price).
"""

from __future__ import annotations

import random

from ..errors import SimNotStartedError
from ..types import (
    Action,
    ActionType,
    GameState,
    Plot,
    StepResult,
    Weather,
)
from .base import SimClient
from .crops import CROPS, CROP_NAMES

_WEATHER_WEIGHTS = {
    Weather.SUNNY: 0.45,
    Weather.RAINY: 0.30,
    Weather.DROUGHT: 0.15,
    Weather.STORM: 0.10,
}


class MockSim(SimClient):
    """A deterministic (given a seed) farming game."""

    def __init__(
        self,
        seed: int = 0,
        num_plots: int = 4,
        max_days: int = 20,
        starting_cash: float = 100.0,
    ) -> None:
        self.seed = seed
        self.num_plots = num_plots
        self.max_days = max_days
        self.starting_cash = starting_cash
        self._rng = random.Random(seed)
        self._state: GameState | None = None

    # ------------------------------------------------------------------ #
    # SimClient interface
    # ------------------------------------------------------------------ #
    def reset(self) -> GameState:
        self._rng = random.Random(self.seed)
        self._state = GameState(
            day=0,
            max_days=self.max_days,
            cash=self.starting_cash,
            weather=self._roll_weather(),
            forecast=[self._roll_weather() for _ in range(3)],
            market_prices=self._roll_prices(),
            plots=[Plot(index=i) for i in range(self.num_plots)],
            inventory={},
            done=False,
        )
        return self._clone_state()

    def state(self) -> GameState:
        if self._state is None:
            raise SimNotStartedError("call reset() before state()")
        return self._clone_state()

    def step(self, action: Action) -> StepResult:
        if self._state is None:
            raise SimNotStartedError("call reset() before step()")
        s = self._state
        if s.done:
            return StepResult(self._clone_state(), 0.0, "game over", ok=False)

        reward = 0.0
        msg = ""
        ok = True

        if action.type == ActionType.PLANT:
            reward, msg, ok = self._do_plant(action)
        elif action.type == ActionType.WATER:
            msg, ok = self._do_water(action)
        elif action.type == ActionType.FERTILIZE:
            reward, msg, ok = self._do_fertilize(action)
        elif action.type == ActionType.HARVEST:
            msg, ok = self._do_harvest(action)
        elif action.type == ActionType.SELL:
            reward, msg, ok = self._do_sell(action)
        elif action.type == ActionType.WAIT:
            msg = "waited"
        else:
            return StepResult(self._clone_state(), 0.0, "unknown action", ok=False)

        # Advance the world by one day after each action.
        self._advance_day()

        if s.day >= s.max_days:
            s.done = True
            reward += self._final_settlement()
            msg = (msg + " | game complete").strip(" |")

        return StepResult(self._clone_state(), reward, msg, ok=ok)

    # ------------------------------------------------------------------ #
    # Action handlers
    # ------------------------------------------------------------------ #
    def _do_plant(self, action: Action) -> tuple[float, str, bool]:
        s = self._state
        plot = self._get_plot(action.plot_index)
        if plot is None:
            return 0.0, "invalid plot", False
        if plot.crop is not None:
            return 0.0, "plot occupied", False
        if action.crop not in CROPS:
            return 0.0, "unknown crop", False
        crop = CROPS[action.crop]
        if s.cash < crop.seed_cost:
            return 0.0, "not enough cash to plant", False
        s.cash -= crop.seed_cost
        plot.crop = crop.name
        plot.age = 0
        plot.water_level = 0
        plot.fertilized = False
        plot.health = 1.0
        plot.ready = False
        return -crop.seed_cost, f"planted {crop.name} on plot {plot.index}", True

    def _do_water(self, action: Action) -> tuple[str, bool]:
        plot = self._get_plot(action.plot_index)
        if plot is None or plot.crop is None:
            return "nothing to water", False
        plot.water_level += 1
        return f"watered plot {plot.index}", True

    def _do_fertilize(self, action: Action) -> tuple[float, str, bool]:
        s = self._state
        plot = self._get_plot(action.plot_index)
        if plot is None or plot.crop is None:
            return 0.0, "nothing to fertilize", False
        cost = 8.0
        if s.cash < cost:
            return 0.0, "not enough cash to fertilize", False
        if plot.fertilized:
            return 0.0, "already fertilized", False
        s.cash -= cost
        plot.fertilized = True
        plot.health = min(1.0, plot.health + 0.15)
        return -cost, f"fertilized plot {plot.index}", True

    def _do_harvest(self, action: Action) -> tuple[str, bool]:
        s = self._state
        plot = self._get_plot(action.plot_index)
        if plot is None or plot.crop is None:
            return "nothing to harvest", False
        if not plot.ready:
            return "crop not ready", False
        crop = CROPS[plot.crop]
        yield_units = round(crop.base_yield * max(0.0, plot.health), 2)
        s.inventory[plot.crop] = s.inventory.get(plot.crop, 0.0) + yield_units
        name = plot.crop
        # clear the plot
        plot.crop = None
        plot.age = 0
        plot.water_level = 0
        plot.fertilized = False
        plot.health = 1.0
        plot.ready = False
        return f"harvested {yield_units} {name}", True

    def _do_sell(self, action: Action) -> tuple[float, str, bool]:
        s = self._state
        crop = action.crop
        if crop is None or crop not in s.inventory or s.inventory[crop] <= 0:
            return 0.0, "nothing to sell", False
        available = s.inventory[crop]
        amount = available if action.amount is None else min(action.amount, available)
        if amount <= 0:
            return 0.0, "nothing to sell", False
        price = s.market_prices.get(crop, 0.0)
        revenue = round(amount * price, 2)
        s.cash += revenue
        s.inventory[crop] = round(available - amount, 2)
        if s.inventory[crop] <= 0:
            del s.inventory[crop]
        return revenue, f"sold {amount} {crop} for {revenue}", True

    # ------------------------------------------------------------------ #
    # World evolution
    # ------------------------------------------------------------------ #
    def _advance_day(self) -> None:
        s = self._state
        weather = s.weather
        for plot in s.plots:
            if plot.crop is None:
                continue
            crop = CROPS[plot.crop]
            plot.age += 1

            # Rain provides free water; drought/storm harm crops.
            if weather == Weather.RAINY:
                plot.water_level += 1
            elif weather == Weather.DROUGHT:
                plot.health = max(0.0, plot.health - crop.drought_penalty)
            elif weather == Weather.STORM:
                if not plot.fertilized:
                    plot.health = max(0.0, plot.health - 0.3)

            # Under-watering hurts health as the crop matures.
            if plot.age >= crop.days_to_mature and plot.water_level < crop.water_need:
                deficit = crop.water_need - plot.water_level
                plot.health = max(0.0, plot.health - 0.1 * deficit)

            if plot.age >= crop.days_to_mature:
                plot.ready = True

        # Advance calendar, weather, forecast, and market.
        s.day += 1
        s.weather = s.forecast.pop(0) if s.forecast else self._roll_weather()
        s.forecast.append(self._roll_weather())
        s.market_prices = self._roll_prices(previous=s.market_prices)

    def _final_settlement(self) -> float:
        """Value any unsold inventory at current prices and add to cash."""
        s = self._state
        bonus = 0.0
        for crop, units in list(s.inventory.items()):
            price = s.market_prices.get(crop, 0.0)
            bonus += units * price
            s.cash += units * price
        s.inventory.clear()
        return round(bonus, 2)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _roll_weather(self) -> Weather:
        r = self._rng.random()
        cumulative = 0.0
        for weather, weight in _WEATHER_WEIGHTS.items():
            cumulative += weight
            if r <= cumulative:
                return weather
        return Weather.SUNNY

    def _roll_prices(self, previous: dict[str, float] | None = None) -> dict[str, float]:
        prices: dict[str, float] = {}
        for name in CROP_NAMES:
            if previous and name in previous:
                # random walk around the previous price
                drift = self._rng.uniform(-0.15, 0.15)
                prices[name] = round(max(1.0, previous[name] * (1 + drift)), 2)
            else:
                base = CROPS[name].seed_cost * self._rng.uniform(1.5, 3.0)
                prices[name] = round(base, 2)
        return prices

    def _get_plot(self, index: int | None) -> Plot | None:
        s = self._state
        if index is None or index < 0 or index >= len(s.plots):
            return None
        return s.plots[index]

    def _clone_state(self) -> GameState:
        s = self._state
        return GameState(
            day=s.day,
            max_days=s.max_days,
            cash=round(s.cash, 2),
            weather=s.weather,
            forecast=list(s.forecast),
            market_prices=dict(s.market_prices),
            plots=[
                Plot(
                    index=p.index,
                    crop=p.crop,
                    age=p.age,
                    water_level=p.water_level,
                    fertilized=p.fertilized,
                    health=round(p.health, 3),
                    ready=p.ready,
                )
                for p in s.plots
            ],
            inventory=dict(s.inventory),
            done=s.done,
        )
