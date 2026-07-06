"""Local Kaggriculture simulator — reproduces the real obs/action contract."""

from kaggriculture_agent.real import LocalKaggricultureEnv, Mechanics
from kaggriculture_agent.real import protocol as P


def _env(**kw):
    e = LocalKaggricultureEnv(seed=0, n_players=2, **kw)
    return e


# --- shape / observation ---------------------------------------------------- #
def test_reset_initial_state():
    e = _env()
    assert e.day == 1 and e.turn == 0
    assert len(e.farms) == 2
    obs = e.observe(0)
    assert obs["player"] == 0
    assert set(obs) == {"player", "day", "farms", "private"}
    assert set(obs["private"]) == {"seeds", "shed"}
    tiles = obs["farms"][0]["tiles"]
    assert len(tiles) == 5 and len(tiles[0]) == 5


def test_observe_hides_internal_tile_fields():
    e = _env()
    # Plant on (0,0): farmer starts there and begins with WHEAT seeds.
    e.step([P.build_action([P.PLANT, "WHEAT"]), None])
    tile = e.observe(0)["farms"][0]["tiles"][0][0]
    assert tile["kind"] == P.KIND_PLANT
    # Only the real, public keys are exposed — no crop/_waterings leak.
    assert set(tile) == {"kind", "planted_day", "watered_today"}


# --- core mechanics --------------------------------------------------------- #
def test_plant_consumes_seed_and_marks_tile():
    e = _env()
    before = e.observe(0)["private"]["seeds"]["WHEAT"]
    e.step([P.build_action([P.PLANT, "WHEAT"]), None])
    after = e.observe(0)["private"]["seeds"]["WHEAT"]
    assert after == before - 1
    assert e.farms[0]["tiles"][0][0]["kind"] == P.KIND_PLANT


def test_water_sets_watered_today():
    e = _env()
    e.step([P.build_action([P.PLANT, "WHEAT"]), None])
    e.step([P.build_action([P.WATER]), None])
    assert e.farms[0]["tiles"][0][0]["watered_today"] is True


def test_day_rolls_over_and_resets_watering():
    e = _env()
    e.step([P.build_action([P.PLANT, "WHEAT"]), None])
    e.step([P.build_action([P.WATER]), None])
    # Advance to the next day (24 turns/day).
    for _ in range(e.mech.turns_per_day - 2):
        e.step([P.pass_action(), None])
    assert e.day == 2
    assert e.farms[0]["tiles"][0][0]["watered_today"] is False


def test_harvest_after_maturity_fills_shed():
    e = _env()
    e.step([P.build_action([P.PLANT, "WHEAT"]), None])
    # Water each day, then advance two full days so age >= mature_days.
    for _ in range(2 * e.mech.turns_per_day):
        e.step([P.build_action([P.WATER]), None])
    assert e.day >= 3
    e.step([P.build_action([P.HARVEST]), None])
    assert e.farms[0]["shed"].get("WHEAT", 0) > 0
    assert e.farms[0]["tiles"][0][0] is None  # tile cleared after harvest


def test_market_buy_and_sell_move_money():
    e = _env()
    m0 = e.farms[0]["money"]
    e.step([P.build_action([P.PASS], market=[[P.BUY_SEED, "WHEAT", 2]]), None])
    spec = e.mech.crops["WHEAT"]
    assert e.farms[0]["money"] == m0 - 2 * spec.seed_cost
    assert e.observe(0)["private"]["seeds"]["WHEAT"] == 6  # 4 start + 2

    # Seed the shed directly, then sell it.
    e.farms[0]["shed"]["WHEAT"] = 3
    m1 = e.farms[0]["money"]
    e.step([P.build_action([P.PASS], market=[[P.SELL, "WHEAT", 3]]), None])
    assert e.farms[0]["money"] == m1 + 3 * spec.sell_price
    assert e.farms[0]["shed"]["WHEAT"] == 0


def test_cannot_oversell_or_overspend():
    e = _env()
    e.farms[0]["money"] = 5  # too poor for even one seed at cost 10
    e.step([P.build_action([P.PASS], market=[[P.BUY_SEED, "WHEAT", 1]]), None])
    assert e.farms[0]["money"] == 5  # purchase rejected
    e.farms[0]["shed"]["WHEAT"] = 1
    e.step([P.build_action([P.PASS], market=[[P.SELL, "WHEAT", 999]]), None])
    assert e.farms[0]["shed"]["WHEAT"] == 0  # only what we had was sold


def test_movement_and_clamp():
    e = _env()
    e.step([P.build_action([P.EAST]), None])
    assert e.farms[0]["farmer"] == [1, 0]
    e.step([P.build_action([P.SOUTH]), None])
    assert e.farms[0]["farmer"] == [1, 1]
    # Clamp at the west/north edge.
    for _ in range(10):
        e.step([P.build_action([P.WEST]), None])
        e.step([P.build_action([P.NORTH]), None])
    assert e.farms[0]["farmer"] == [0, 0]


def test_dig_removes_weed():
    e = _env()
    e.farms[0]["tiles"][0][0] = {"kind": P.KIND_WEED}
    e.step([P.build_action([P.DIG]), None])
    assert e.farms[0]["tiles"][0][0] is None


def test_game_ends_at_turn_limit():
    e = _env()
    while not e.done:
        e.step([P.pass_action(), P.pass_action()])
    assert e.turn == e.max_turns == e.mech.turns_per_day * e.mech.max_days


def test_deterministic_by_seed():
    a = LocalKaggricultureEnv(seed=7, n_players=1)
    b = LocalKaggricultureEnv(seed=7, n_players=1)
    for _ in range(200):
        a.step([P.pass_action()])
        b.step([P.pass_action()])
    # Same seed -> identical weed placement -> identical public state.
    assert a.observe(0)["farms"] == b.observe(0)["farms"]
