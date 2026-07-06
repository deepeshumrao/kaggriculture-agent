"""Guardrails reject illegal actions and never crash the sim."""

from kaggriculture_agent.policy.guardrails import is_legal, sanitize
from kaggriculture_agent.sim import MockSim
from kaggriculture_agent.types import Action, ActionType


def test_wait_always_legal():
    state = MockSim(seed=0).reset()
    ok, _ = is_legal(Action(ActionType.WAIT), state)
    assert ok


def test_harvest_unready_is_illegal():
    state = MockSim(seed=0).reset()
    sim = MockSim(seed=0)
    sim.reset()
    sim.step(Action(ActionType.PLANT, plot_index=0, crop="wheat"))
    state = sim.state()
    ok, reason = is_legal(Action(ActionType.HARVEST, plot_index=0), state)
    assert not ok
    assert reason == "crop not ready"


def test_sanitize_downgrades_illegal_to_wait():
    state = MockSim(seed=0).reset()
    bad = Action(ActionType.HARVEST, plot_index=99)
    safe = sanitize(bad, state)
    assert safe.type == ActionType.WAIT


def test_invalid_plot_rejected():
    state = MockSim(seed=0).reset()
    ok, _ = is_legal(Action(ActionType.PLANT, plot_index=999, crop="wheat"), state)
    assert not ok


def test_plant_unknown_crop_rejected():
    state = MockSim(seed=0).reset()
    ok, _ = is_legal(Action(ActionType.PLANT, plot_index=0, crop="banana"), state)
    assert not ok
