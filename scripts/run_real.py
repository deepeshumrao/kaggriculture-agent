"""Run the real-protocol agent in the local Kaggriculture simulator.

Plays a full game (2 players: our brain vs a do-nothing opponent) and prints a
summary. This exercises the exact obs/action contract the real Kaggle env uses.

Usage:
    python scripts/run_real.py [--seed N] [--verbose]
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

from kaggriculture_agent.real import FarmBrain, LocalKaggricultureEnv
from kaggriculture_agent.real import protocol as P


def _idle_opponent(obs: dict) -> dict:
    return P.pass_action()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the real-protocol agent locally.")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    env = LocalKaggricultureEnv(seed=args.seed, n_players=2)
    brain = FarmBrain()

    harvests = 0
    while not env.done:
        me = brain.decide(env.observe(0))
        opp = _idle_opponent(env.observe(1))
        if me["farmer"] and me["farmer"][0] == P.HARVEST:
            harvests += 1
        if args.verbose and env.turn % 24 == 0:
            farm = env.farms[0]
            print(
                f"day {env.day:>2} | money {farm['money']:8.2f} "
                f"| seeds {farm['seeds']} | shed {farm['shed']}"
            )
        env.step([me, opp])

    print(f"\n=== FINAL (seed {args.seed}) ===")
    print(f"Our score       : {env.score(0):8.2f}")
    print(f"Opponent score  : {env.score(1):8.2f}")
    print(f"Harvests worked : {harvests}")
    print(f"Turns played    : {env.turn} (over {env.mech.max_days} days)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"\n[ERROR] run_real failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
