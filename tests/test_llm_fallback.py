"""The LLM strategy must degrade gracefully when there is no key/SDK.

These tests never make a network call — they verify the safety behavior that
keeps the project runnable and free by default.
"""

from kaggriculture_agent.memory.knowledge import Knowledge
from kaggriculture_agent.memory.state import EpisodeState
from kaggriculture_agent.policy.llm_strategy import LLMStrategy, _parse_action
from kaggriculture_agent.sim import MockSim
from kaggriculture_agent.types import ActionType


def test_llm_without_client_falls_back_to_heuristic():
    strat = LLMStrategy()
    strat._client = None  # simulate no key / no SDK
    state = MockSim(seed=0).reset()
    action = strat.decide(state, EpisodeState(), Knowledge())
    # It should still return a valid, usable action (from the heuristic).
    assert action.type in set(ActionType)


def test_parse_action_handles_plain_json():
    a = _parse_action('{"type": "plant", "plot_index": 1, "crop": "corn"}')
    assert a is not None
    assert a.type == ActionType.PLANT
    assert a.plot_index == 1
    assert a.crop == "corn"


def test_parse_action_handles_code_fences():
    a = _parse_action('```json\n{"type": "wait"}\n```')
    assert a is not None
    assert a.type == ActionType.WAIT


def test_parse_action_rejects_garbage():
    assert _parse_action("I think you should plant wheat!") is None
    assert _parse_action('{"type": "teleport"}') is None
