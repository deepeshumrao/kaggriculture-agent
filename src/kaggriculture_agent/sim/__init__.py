"""Simulation layer: the interface + a mock implementation.

Swap `MockSim` for a real Kaggle client that implements `SimClient`.
"""

from .base import SimClient
from .mock_sim import MockSim

__all__ = ["SimClient", "MockSim"]
