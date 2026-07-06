"""Error & exception handling: failures are contained, not fatal."""

import pytest

from kaggriculture_agent.agent import Agent
from kaggriculture_agent.errors import SimError, SimNotStartedError
from kaggriculture_agent.memory.knowledge import Knowledge
from kaggriculture_agent.memory.state import EpisodeState
from kaggriculture_agent.policy.strategy import Strategy
from kaggriculture_agent.sim import MockSim
from kaggriculture_agent.sim.base import SimClient
from kaggriculture_agent.types import Action, ActionType, GameState, StepResult


# --- Sim raises a clear, catchable error instead of a bare assert ----------- #
def test_sim_step_before_reset_raises_typed_error():
    sim = MockSim(seed=0)
    with pytest.raises(SimNotStartedError):
        sim.step(Action(ActionType.WAIT))


def test_sim_state_before_reset_raises_typed_error():
    sim = MockSim(seed=0)
    with pytest.raises(SimNotStartedError):
        sim.state()


# --- A crashing strategy must NOT crash the game ---------------------------- #
class ExplodingStrategy(Strategy):
    def decide(self, state, episode, knowledge):
        raise RuntimeError("boom")


def test_agent_survives_strategy_exception():
    agent = Agent(strategy=ExplodingStrategy())
    result = agent.play_episode(MockSim(seed=0, max_days=5))
    # It falls back to WAIT every turn and still finishes with a valid score.
    assert result.days == 5
    assert result.score >= 0


# --- A crashing sim ends the episode as a typed SimError -------------------- #
class BrokenSim(SimClient):
    def __init__(self):
        self._real = MockSim(seed=0, max_days=5)

    def reset(self) -> GameState:
        return self._real.reset()

    def state(self) -> GameState:
        return self._real.state()

    def step(self, action: Action) -> StepResult:
        raise ValueError("backend exploded")


def test_agent_wraps_sim_failure_as_simerror():
    agent = Agent()
    with pytest.raises(SimError):
        agent.play_episode(BrokenSim())


# --- LLM transient-error classifier ----------------------------------------- #
def test_transient_error_detection():
    from kaggriculture_agent.policy.llm_strategy import _is_transient

    assert _is_transient(Exception("429 RESOURCE_EXHAUSTED"))
    assert _is_transient(Exception("deadline exceeded / timeout"))
    assert not _is_transient(Exception("401 invalid api key"))


# --- LLM disables itself after repeated failures (no infinite hammering) ----- #
def test_llm_disables_after_repeated_failures():
    from kaggriculture_agent.policy.llm_strategy import LLMStrategy

    strat = LLMStrategy()

    # Pretend a client exists but every call fails non-transiently.
    class _Boom:
        class models:
            @staticmethod
            def generate_content(*a, **k):
                raise ValueError("permanent failure")

    strat._client = _Boom()
    state = MockSim(seed=0).reset()
    ep, kn = EpisodeState(), Knowledge()

    for _ in range(3):
        action = strat.decide(state, ep, kn)  # each falls back to heuristic
        assert action.type in set(ActionType)

    assert strat._disabled is True
