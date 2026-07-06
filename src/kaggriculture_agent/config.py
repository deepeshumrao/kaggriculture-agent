"""Central configuration and tunable knobs.

Reads from environment (via .env if present) with safe defaults so the project
runs with zero setup.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

try:  # optional dependency; project works without it
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional
    pass


@dataclass(frozen=True)
class Config:
    # --- policy selection ---
    policy: str = os.getenv("KAGGRICULTURE_POLICY", "heuristic")  # "heuristic" | "llm"

    # --- LLM (only used if policy == "llm") ---
    model: str = os.getenv("KAGGRICULTURE_MODEL", "gemini-2.5-flash")
    api_key: str = os.getenv("GOOGLE_API_KEY", "")

    # --- strategy thresholds (tunable) ---
    min_cash_reserve: float = 5.0     # never spend below this
    sell_price_percentile: float = 0.6  # sell when price is in the top 40%
    plant_when_days_left: int = 3     # don't plant if too little time to mature

    # --- run settings ---
    default_episodes: int = 50
    default_seed: int = 0

    # --- SECURITY CAPS (Denial-of-Wallet / unbounded execution) ---
    max_turns: int = 500            # hard cap on steps per episode
    max_llm_calls: int = 200        # hard cap on API calls per episode
    max_llm_response_chars: int = 20_000  # reject oversized model responses

    # --- SECURITY: data-poisoning sanity bounds ---
    price_sanity_min: float = 0.0
    price_sanity_max: float = 1_000_000.0
    cash_sanity_max: float = 1_000_000_000.0


CONFIG = Config()
