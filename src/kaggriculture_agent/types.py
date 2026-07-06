"""Core data types shared across the agent.

These are deliberately simulation-agnostic. When the real Kaggle sim arrives,
we map its observations into these structures once, and the rest of the agent
(strategy, guardrails, memory) keeps working unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ActionType(str, Enum):
    """Every move the agent can attempt in a turn."""

    PLANT = "plant"
    WATER = "water"
    FERTILIZE = "fertilize"
    HARVEST = "harvest"
    SELL = "sell"
    WAIT = "wait"  # do nothing this turn (always legal)


class Weather(str, Enum):
    SUNNY = "sunny"
    RAINY = "rainy"
    DROUGHT = "drought"
    STORM = "storm"


@dataclass(frozen=True)
class Crop:
    """Static definition of a crop type."""

    name: str
    seed_cost: float
    days_to_mature: int
    base_yield: float          # units produced when harvested healthy
    water_need: int            # waterings needed before maturity
    drought_penalty: float     # yield multiplier lost per drought day (0..1)


@dataclass
class Plot:
    """A single field plot the agent farms."""

    index: int
    crop: Optional[str] = None      # crop name, or None if empty
    age: int = 0                    # days since planted
    water_level: int = 0            # accumulated waterings
    fertilized: bool = False
    health: float = 1.0             # 0..1 yield multiplier
    ready: bool = False             # matured and harvestable


@dataclass
class GameState:
    """A full snapshot of the world at the start of a turn."""

    day: int
    max_days: int
    cash: float
    weather: Weather
    forecast: list[Weather]                 # upcoming weather (may be empty)
    market_prices: dict[str, float]         # crop name -> price per unit
    plots: list[Plot]
    inventory: dict[str, float] = field(default_factory=dict)  # harvested, unsold
    done: bool = False

    @property
    def days_left(self) -> int:
        return max(0, self.max_days - self.day)


@dataclass
class Action:
    """An action the agent decides to take this turn."""

    type: ActionType
    plot_index: Optional[int] = None
    crop: Optional[str] = None       # for PLANT
    amount: Optional[float] = None   # for SELL (units); None = sell all of crop

    def __str__(self) -> str:
        parts = [self.type.value]
        if self.plot_index is not None:
            parts.append(f"plot={self.plot_index}")
        if self.crop:
            parts.append(f"crop={self.crop}")
        if self.amount is not None:
            parts.append(f"amount={self.amount}")
        return " ".join(parts)


@dataclass
class StepResult:
    """What the sim returns after applying an action."""

    state: GameState
    reward: float          # score change from this step
    message: str = ""      # human-readable note (e.g. "planted wheat")
    ok: bool = True        # False if the action was rejected by the sim
