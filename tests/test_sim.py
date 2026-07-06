"""The mock sim behaves correctly and deterministically."""

from kaggriculture_agent.sim import MockSim
from kaggriculture_agent.types import Action, ActionType


def test_reset_returns_initial_state():
    sim = MockSim(seed=1, max_days=10, num_plots=3)
    state = sim.reset()
    assert state.day == 0
    assert state.cash == 100.0
    assert len(state.plots) == 3
    assert all(p.crop is None for p in state.plots)
    assert set(state.market_prices) == {"wheat", "corn", "tomato", "potato"}


def test_determinism_same_seed():
    a = MockSim(seed=42).reset()
    b = MockSim(seed=42).reset()
    assert a.weather == b.weather
    assert a.market_prices == b.market_prices


def test_planting_costs_cash_and_occupies_plot():
    sim = MockSim(seed=0)
    state = sim.reset()
    result = sim.step(Action(ActionType.PLANT, plot_index=0, crop="wheat"))
    assert result.ok
    assert result.state.plots[0].crop == "wheat"
    assert result.state.cash < state.cash


def test_game_ends_after_max_days():
    sim = MockSim(seed=0, max_days=5)
    sim.reset()
    done = False
    for _ in range(5):
        done = sim.step(Action(ActionType.WAIT)).state.done
    assert done


def test_cannot_plant_without_cash():
    sim = MockSim(seed=0, starting_cash=1.0)
    sim.reset()
    result = sim.step(Action(ActionType.PLANT, plot_index=0, crop="tomato"))
    assert not result.ok
