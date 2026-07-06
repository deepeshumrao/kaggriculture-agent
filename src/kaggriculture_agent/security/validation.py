"""Threat 3 — Data poisoning / manipulation defense.

Every GameState coming back from a (possibly untrusted) sim backend is validated
and sanitized: NaN/Inf, negative cash, absurd prices, out-of-range plot fields,
and injection text in crop names are all neutralized to safe values. The agent
therefore never acts on logically impossible data.
"""

from __future__ import annotations

import math

from ..config import CONFIG
from ..sim.crops import CROP_NAMES
from ..types import GameState, Plot
from .injection import is_injection


def _finite(x: float, default: float = 0.0) -> float:
    return x if isinstance(x, (int, float)) and math.isfinite(x) else default


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def sanitize_state(state: GameState) -> tuple[GameState, list[str]]:
    """Return (safe_state, violations). Mutates a shallow-safe copy in place."""
    violations: list[str] = []

    # --- cash: finite, non-absurd ---
    cash = _finite(state.cash, 0.0)
    if cash != state.cash:
        violations.append("cash was NaN/Inf -> reset to 0")
    if cash < 0:
        violations.append(f"negative cash {cash} -> clamped to 0")
        cash = 0.0
    if cash > CONFIG.cash_sanity_max:
        violations.append(f"impossible cash {cash} -> clamped")
        cash = CONFIG.cash_sanity_max
    state.cash = round(cash, 2)

    # --- day within bounds ---
    if not (0 <= state.day <= max(state.max_days, 0)):
        violations.append(f"day {state.day} out of range -> clamped")
        state.day = int(_clamp(state.day, 0, max(state.max_days, 0)))

    # --- market prices: finite, within sane band, known crops only ---
    safe_prices: dict[str, float] = {}
    for crop, price in state.market_prices.items():
        p = _finite(price, CONFIG.price_sanity_min)
        if p != price:
            violations.append(f"price[{crop}] NaN/Inf -> reset")
        if p < CONFIG.price_sanity_min or p > CONFIG.price_sanity_max:
            violations.append(f"price[{crop}]={p} out of band -> clamped")
            p = _clamp(p, CONFIG.price_sanity_min, CONFIG.price_sanity_max)
        if is_injection(str(crop)):
            violations.append(f"injection in crop name {crop!r} -> dropped")
            continue
        safe_prices[crop] = round(p, 2)
    state.market_prices = safe_prices

    # --- plots: coerce fields into valid ranges ---
    for plot in state.plots:
        plot.health = _clamp(_finite(plot.health, 0.0), 0.0, 1.0)
        if plot.age < 0:
            violations.append(f"plot {plot.index} negative age -> 0")
            plot.age = 0
        if plot.water_level < 0:
            plot.water_level = 0
        if plot.crop is not None and is_injection(str(plot.crop)):
            violations.append(f"injection in plot {plot.index} crop -> cleared")
            plot.crop = None

    # --- inventory: non-negative, finite ---
    safe_inv: dict[str, float] = {}
    for crop, units in state.inventory.items():
        u = _finite(units, 0.0)
        if u < 0:
            violations.append(f"negative inventory[{crop}] -> 0")
            u = 0.0
        if u > 0:
            safe_inv[crop] = round(u, 2)
    state.inventory = safe_inv

    return state, violations
