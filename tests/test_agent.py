"""End-to-end: the agent completes games and beats the naive baseline."""

from kaggriculture_agent.agent import Agent
from kaggriculture_agent.baseline import NaiveStrategy
from kaggriculture_agent.memory.knowledge import Knowledge
from kaggriculture_agent.sim import MockSim


def test_agent_completes_episode():
    agent = Agent()
    result = agent.play_episode(MockSim(seed=0, max_days=20))
    assert result.days == 20
    assert isinstance(result.score, float)


def test_agent_never_goes_negative():
    agent = Agent()
    result = agent.play_episode(MockSim(seed=7, max_days=20))
    assert result.score >= 0


def test_agent_beats_baseline_on_average():
    smart = Agent(knowledge=Knowledge())
    naive = Agent(strategy=NaiveStrategy())

    smart_total = 0.0
    naive_total = 0.0
    n = 20
    for seed in range(n):
        smart_total += smart.play_episode(MockSim(seed=seed, max_days=20)).score
        naive_total += naive.play_episode(MockSim(seed=seed, max_days=20)).score

    assert smart_total > naive_total, (
        f"smart {smart_total:.1f} should beat naive {naive_total:.1f}"
    )
