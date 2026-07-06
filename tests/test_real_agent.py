"""FarmBrain — the real-protocol decision policy + its Kaggle entrypoint."""

from kaggriculture_agent.real import FarmBrain, LocalKaggricultureEnv
from kaggriculture_agent.real import protocol as P
from kaggriculture_agent.real.submission import agent


def _obs(
    farmer=(0, 0),
    money=100.0,
    tiles=None,
    seeds=None,
    shed=None,
    day=1,
):
    size = 5
    grid = tiles or [[None] * size for _ in range(size)]
    return {
        "player": 0,
        "day": day,
        "farms": [
            {"farmer": list(farmer), "money": money, "tiles": grid},
            {"farmer": [0, 0], "money": money, "tiles": [[None] * size for _ in range(size)]},
        ],
        "private": {"seeds": seeds or {"WHEAT": 4}, "shed": shed or {}},
    }


# --- action shape ----------------------------------------------------------- #
def test_decide_returns_well_formed_action():
    act = FarmBrain().decide(_obs())
    assert set(act) == {"farmer", "hands", "market"}
    assert isinstance(act["farmer"], list) and act["farmer"]
    assert isinstance(act["market"], list)


def test_submission_agent_accepts_optional_config():
    # Some Kaggle envs call agent(obs, config); ours must tolerate both.
    assert agent(_obs()) == agent(_obs(), config={"anything": 1})


# --- market behavior -------------------------------------------------------- #
def test_buys_seed_when_low():
    obs = _obs(seeds={"WHEAT": 0})
    act = FarmBrain().decide(obs)
    assert [P.BUY_SEED, "WHEAT", 4] in act["market"]


def test_sells_shed_contents():
    obs = _obs(shed={"WHEAT": 5})
    act = FarmBrain().decide(obs)
    assert [P.SELL, "WHEAT", 5] in act["market"]


def test_no_selling_when_shed_empty():
    act = FarmBrain().decide(_obs(shed={}))
    assert all(op[0] != P.SELL for op in act["market"])


# --- tile targeting / movement --------------------------------------------- #
def test_plants_on_empty_tile_when_standing_on_it():
    # All-empty board, farmer at (0,0), has seed, nothing higher priority.
    act = FarmBrain().decide(_obs(farmer=(0, 0)))
    assert act["farmer"] == [P.PLANT, "WHEAT"]


def test_harvest_takes_priority_and_agent_walks_to_it():
    grid = [[None] * 5 for _ in range(5)]
    # A mature crop at (2,0): planted day 1, now day 5 -> age 4 >= 2.
    grid[0][2] = {"kind": P.KIND_PLANT, "planted_day": 1, "watered_today": True}
    act = FarmBrain().decide(_obs(farmer=(0, 0), tiles=grid, day=5))
    # Farmer at (0,0) must move EAST toward the harvest target at x=2.
    assert act["farmer"] == [P.EAST]


def test_waters_unwatered_crop_before_planting_more():
    grid = [[None] * 5 for _ in range(5)]
    grid[0][0] = {"kind": P.KIND_PLANT, "planted_day": 1, "watered_today": False}
    act = FarmBrain().decide(_obs(farmer=(0, 0), tiles=grid, day=1))
    assert act["farmer"] == [P.WATER]


def test_digs_weed():
    grid = [[None] * 5 for _ in range(5)]
    grid[0][0] = {"kind": P.KIND_WEED}
    act = FarmBrain().decide(_obs(farmer=(0, 0), tiles=grid, seeds={"WHEAT": 0}))
    assert act["farmer"] == [P.DIG]


def test_passes_when_nothing_to_do_and_no_seed():
    # Full board of weeds is out of scope here: empty board, no seeds -> PASS.
    act = FarmBrain().decide(_obs(seeds={"WHEAT": 0}, shed={}, money=0))
    assert act["farmer"] == [P.PASS]


# --- integration: beats an idle opponent ----------------------------------- #
def test_brain_grows_money_over_a_full_game():
    env = LocalKaggricultureEnv(seed=1, n_players=2)
    brain = FarmBrain()
    start = env.farms[0]["money"]
    while not env.done:
        env.step([brain.decide(env.observe(0)), P.pass_action()])
    assert env.score(0) > start          # actually farmed a profit
    assert env.score(0) > env.score(1)   # beat the do-nothing opponent
