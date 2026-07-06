"""Run the submission the way Kaggle does — with a local fallback.

If the real `kaggle_environments` package (and the Kaggriculture env) is
available, this drives our agent through it. Otherwise it transparently falls
back to our local simulator so the exact same command works offline.

Usage:
    python scripts/run_kaggle.py [--env NAME] [--seed N]

NOTE: the registered env NAME is not yet confirmed from the competition. Pass
--env with the real name once known (default guess: "kaggriculture").
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

# The submission we actually ship (single self-contained file).
sys.path.insert(0, "deliverables")
import kaggriculture_submission as sub  # noqa: E402


def _run_real(env_name: str) -> int:
    from kaggle_environments import make  # type: ignore

    env = make(env_name, debug=True)
    # Our agent vs a built-in / do-nothing opponent. Adjust once the real env's
    # agent slots are confirmed.
    env.run([sub.agent, "do_nothing"])
    print(env.render(mode="ansi"))
    print("\n[kaggle_environments] episode complete.")
    return 0


def _run_local(seed: int) -> int:
    from kaggriculture_agent.real import LocalKaggricultureEnv
    from kaggriculture_agent.real import protocol as P

    env = LocalKaggricultureEnv(seed=seed, n_players=2)
    while not env.done:
        env.step([sub.agent(env.observe(0)), P.pass_action()])
    print(f"[local fallback] our score {env.score(0):.2f} "
          f"vs idle {env.score(1):.2f} over {env.turn} turns")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Kaggriculture submission.")
    parser.add_argument("--env", default="kaggriculture",
                        help="registered kaggle_environments name (confirm from competition)")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    try:
        import kaggle_environments  # noqa: F401
    except ImportError:
        print("kaggle_environments not installed -> running LOCAL simulator.\n")
        return _run_local(args.seed)

    try:
        return _run_real(args.env)
    except Exception as exc:  # noqa: BLE001
        print(f"[kaggle_environments] could not run env '{args.env}': {exc}")
        print("Falling back to the LOCAL simulator.\n")
        return _run_local(args.seed)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
