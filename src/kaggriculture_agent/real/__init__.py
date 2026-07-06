"""Real Kaggriculture protocol layer.

Everything under `real/` speaks the ACTUAL Kaggle environment contract decoded
from the competition's `agent(obs)` (spatial, 2-player, movement-based) — as
opposed to the abstract single-player model in the rest of the package.

- `protocol`  — constants + helpers for the real obs/action shape.
- `local_env` — a local simulator that reproduces the real contract so we can
                develop and test without the Kaggle package.
- `brain`     — the decision policy (returns real action dicts).
- `submission`— the top-level `agent(obs)` entrypoint Kaggle calls.
"""

from .brain import FarmBrain
from .local_env import LocalKaggricultureEnv, Mechanics

__all__ = ["FarmBrain", "LocalKaggricultureEnv", "Mechanics"]
