"""The simulation interface every backend must implement.

This is the ONE seam between our agent and the outside world. The mock sim and
(later) the real Kaggle client both implement it, so the agent never changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..types import Action, GameState, StepResult


class SimClient(ABC):
    """Contract for a farming simulation backend."""

    @abstractmethod
    def reset(self) -> GameState:
        """Start a new episode and return the initial state."""

    @abstractmethod
    def step(self, action: Action) -> StepResult:
        """Apply one action and advance the world by (at most) one turn."""

    @abstractmethod
    def state(self) -> GameState:
        """Return the current state without changing anything."""
