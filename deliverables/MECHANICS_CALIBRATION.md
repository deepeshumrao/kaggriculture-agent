# Mechanics Calibration — reconciling the local sim with the real env

Our agent submits a top-level `agent(obs)` and **only reads the real `obs` and
returns real actions**. So on the Kaggle leaderboard the *real* environment
supplies all prices/yields/scoring — our local assumptions do **not** affect
leaderboard correctness. They only make our **offline practice scores** realistic.

This doc maps each assumed number to where the real value goes, so calibration
is a single edit in [`src/kaggriculture_agent/real/local_env.py`](../src/kaggriculture_agent/real/local_env.py)
(`Mechanics` dataclass).

## Confirmed from the reference `agent(obs)` (do not change)
| Fact | Value |
|------|-------|
| Grid addressing | `tiles[y][x]` |
| Coordinate convention | `x`=col (EAST=+x), `y`=row (SOUTH=+y) |
| Maturity | harvest when `day - planted_day >= 2` |
| Farmer commands/turn | exactly one (move OR act on current tile) |
| Seed economy | must `BUY_SEED` before `PLANT`; harvest → shed → `SELL` |
| Game length | 30 days = 720 turns (~24/turn per day) |

## `[ASSUMPTION]` values to confirm → where they live
| Assumption | Local default | Confirm from | `Mechanics` field |
|------------|---------------|--------------|-------------------|
| Crop list | WHEAT, CORN | env docs / obs market | `crops` keys |
| Seed cost | WHEAT 10, CORN 15 | market / buy price | `crops[c].seed_cost` |
| Sell price | WHEAT 15, CORN 26 | market / sell price | `crops[c].sell_price` |
| Harvest yield | 3 units | a harvested episode | `crops[c].base_yield` |
| Watering effect | dry = 0.5× yield | env rules | `dry_yield_factor` |
| Weed spawn | 0.30 /farm/day | observed weed rate | `weed_prob_per_day` |
| Starting money | 100 | initial `obs` | `start_money` |
| Starting seeds | WHEAT 4 | initial `obs` | `start_seeds` |
| Score formula | money + shed value | env `reward`/leaderboard | `LocalKaggricultureEnv.score` |

## Still-unknown contract questions (get from the env setup/run cells)
1. **Env creation** — `kaggle_environments.make("<name>")`? a `kagglehub` download?
   → set `--env <name>` in [`scripts/run_kaggle.py`](../scripts/run_kaggle.py).
2. **Run/submit** — `env.run([...])`, a `submission.py`, or a notebook that
   defines `agent`? → confirms how [`kaggriculture_submission.py`](kaggriculture_submission.py) is delivered.
3. **`hands`** — the action dict has a `hands` list, always empty in the
   reference. Likely carried items. If it drives an action we should use, add it
   to `FarmBrain`.
4. **Opponent slots** — how many players, and what the second `env.run` slot
   should be.

## How to calibrate once you have a real episode
1. Print one real initial `obs` → set `start_money`, `start_seeds`, `crops`.
2. Print the market → set `seed_cost` / `sell_price`.
3. Harvest one crop, read the shed delta → set `base_yield`.
4. Re-run `python scripts/run_real.py --verbose`; local scores now track reality.
   The **agent code does not change** — only `Mechanics`.
