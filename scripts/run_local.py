"""Run a single game locally with a full turn-by-turn trace.

Usage:
    python scripts/run_local.py [--seed N] [--days N]
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401  (sets up import path)

from kaggriculture_agent.agent import Agent
from kaggriculture_agent.errors import KaggricultureError
from kaggriculture_agent.logging_setup import enable_logging
from kaggriculture_agent.sim import MockSim


def main() -> int:
    parser = argparse.ArgumentParser(description="Play one Kaggriculture game.")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--days", type=int, default=20)
    parser.add_argument("--plots", type=int, default=4)
    parser.add_argument("--verbose-logs", action="store_true", help="show agent logs")
    args = parser.parse_args()

    if args.verbose_logs:
        enable_logging("DEBUG")

    try:
        sim = MockSim(seed=args.seed, max_days=args.days, num_plots=args.plots)
        agent = Agent(verbose=True)
        print(f"\n=== Kaggriculture - seed {args.seed}, {args.days} days ===\n")
        result = agent.play_episode(sim)
        print(f"\n=== FINAL SCORE: {result.score} (over {result.days} days) ===\n")
        return 0
    except KaggricultureError as exc:
        print(f"\n[ERROR] Game could not complete: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n[interrupted]", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
