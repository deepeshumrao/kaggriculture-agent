"""Manually exercise the Gemini (LLM) policy against the mock sim.

Requires GOOGLE_API_KEY (free key from https://aistudio.google.com/apikey) and
the google-genai SDK. Without them, it prints a clear notice and exits — no crash.

Usage:
    # set your key first (Windows PowerShell):  $env:GOOGLE_API_KEY="..."
    python scripts/test_llm.py [--seed N] [--days N]
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

from kaggriculture_agent.config import CONFIG
from kaggriculture_agent.errors import KaggricultureError
from kaggriculture_agent.logging_setup import enable_logging
from kaggriculture_agent.memory.knowledge import Knowledge
from kaggriculture_agent.policy.llm_strategy import LLMStrategy
from kaggriculture_agent.agent import Agent
from kaggriculture_agent.sim import MockSim


def main() -> int:
    parser = argparse.ArgumentParser(description="Test the Gemini LLM policy.")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--days", type=int, default=12)
    args = parser.parse_args()

    enable_logging("INFO")  # so you can see retries / fallbacks live

    if not CONFIG.api_key:
        print(
            "No GOOGLE_API_KEY found. The LLM policy would fall back to the "
            "heuristic.\nSet a key to test real Gemini calls:\n"
            "  PowerShell:  $env:GOOGLE_API_KEY=\"your_key\"\n"
            "  bash:        export GOOGLE_API_KEY=your_key\n"
        )

    strat = LLMStrategy()
    using_llm = strat._client is not None
    print(f"Model      : {CONFIG.model}")
    print(f"Using LLM  : {using_llm}  ({'Gemini' if using_llm else 'heuristic fallback'})\n")

    try:
        agent = Agent(strategy=strat, knowledge=Knowledge(), verbose=True)
        result = agent.play_episode(MockSim(seed=args.seed, max_days=args.days))
        print(f"\nFINAL SCORE: {result.score}")
        return 0
    except KaggricultureError as exc:
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n[interrupted]", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
