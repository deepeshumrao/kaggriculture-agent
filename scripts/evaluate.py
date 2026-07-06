"""Evaluate the agent vs the naive baseline over many seeded games.

Usage:
    python scripts/evaluate.py [--episodes N]
"""

from __future__ import annotations

import argparse

import _bootstrap  # noqa: F401

from kaggriculture_agent.agent import Agent
from kaggriculture_agent.baseline import NaiveStrategy
from kaggriculture_agent.memory.knowledge import Knowledge
from kaggriculture_agent.sim import MockSim


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate agent vs baseline.")
    parser.add_argument("--episodes", type=int, default=50)
    parser.add_argument("--days", type=int, default=20)
    args = parser.parse_args()

    # Shared long-term memory across episodes for the smart agent.
    knowledge = Knowledge()
    smart = Agent(knowledge=knowledge)
    naive = Agent(strategy=NaiveStrategy())

    smart_scores: list[float] = []
    naive_scores: list[float] = []
    wins = 0

    for seed in range(args.episodes):
        smart_scores.append(
            smart.play_episode(MockSim(seed=seed, max_days=args.days)).score
        )
        naive_scores.append(
            naive.play_episode(MockSim(seed=seed, max_days=args.days)).score
        )
        if smart_scores[-1] >= naive_scores[-1]:
            wins += 1

    smart_avg = _mean(smart_scores)
    naive_avg = _mean(naive_scores)
    lift = (smart_avg - naive_avg) / naive_avg * 100 if naive_avg else float("inf")

    print(f"\n=== Evaluation over {args.episodes} games ({args.days} days each) ===")
    print(f"Smart agent  avg score : {smart_avg:8.2f}")
    print(f"Naive baseline avg     : {naive_avg:8.2f}")
    print(f"Improvement over baseline: {lift:6.1f}%")
    print(f"Win rate vs baseline     : {wins}/{args.episodes} "
          f"({wins / args.episodes * 100:.0f}%)")
    print(f"Best known crop (learned): {knowledge.best_known_crop()}\n")
    return 0


if __name__ == "__main__":
    import sys

    from kaggriculture_agent.errors import KaggricultureError

    try:
        raise SystemExit(main())
    except KaggricultureError as exc:
        print(f"\n[ERROR] Evaluation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
