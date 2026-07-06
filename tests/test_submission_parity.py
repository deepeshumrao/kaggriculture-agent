"""The shipped single-file submission must behave identically to the package.

`deliverables/kaggriculture_submission.py` is a flattened copy of the tested
`real/` package. This test drives a full local game and asserts the standalone
`agent(obs)` returns the exact same action as the package brain for every
observation — so the copy can never silently drift from the tested source.
"""

import importlib.util
import os

from kaggriculture_agent.real import FarmBrain, LocalKaggricultureEnv
from kaggriculture_agent.real import protocol as P

_HERE = os.path.dirname(__file__)
_SUB_PATH = os.path.normpath(
    os.path.join(_HERE, "..", "deliverables", "kaggriculture_submission.py")
)


def _load_submission():
    spec = importlib.util.spec_from_file_location("kaggriculture_submission", _SUB_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_standalone_matches_package_over_full_game():
    sub = _load_submission()
    package = FarmBrain()
    env = LocalKaggricultureEnv(seed=3, n_players=2)

    compared = 0
    while not env.done:
        obs = env.observe(0)
        assert sub.agent(obs) == package.decide(obs)
        compared += 1
        # Drive the game with the package agent; opponent idles.
        env.step([package.decide(obs), P.pass_action()])
    assert compared > 100  # actually exercised a real game, not a stub


def test_standalone_agent_accepts_config_arg():
    sub = _load_submission()
    env = LocalKaggricultureEnv(seed=0, n_players=2)
    obs = env.observe(0)
    assert sub.agent(obs) == sub.agent(obs, config={"x": 1})
