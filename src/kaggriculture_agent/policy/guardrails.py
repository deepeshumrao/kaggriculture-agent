"""Guardrails: reject illegal, wasteful, or over-budget actions BEFORE they run.

This is the safety layer required by 'Agent Quality & Security'. It guarantees
the agent never attempts an invalid move — critical when an LLM might hallucinate
an action.
"""

from __future__ import annotations

from ..sim.crops import CROPS
from ..types import Action, ActionType, GameState

WAIT = Action(type=ActionType.WAIT)


def is_legal(action: Action, state: GameState) -> tuple[bool, str]:
    """Return (legal?, reason). WAIT is always legal."""
    t = action.type

    if t == ActionType.WAIT:
        return True, "ok"

    if t == ActionType.PLANT:
        if action.plot_index is None or not _valid_plot(action.plot_index, state):
            return False, "invalid plot index"
        if state.plots[action.plot_index].crop is not None:
            return False, "plot already occupied"
        if action.crop not in CROPS:
            return False, "unknown crop"
        if state.cash < CROPS[action.crop].seed_cost:
            return False, "cannot afford seed"
        return True, "ok"

    if t in (ActionType.WATER, ActionType.HARVEST):
        if action.plot_index is None or not _valid_plot(action.plot_index, state):
            return False, "invalid plot index"
        if state.plots[action.plot_index].crop is None:
            return False, "no crop on plot"
        if t == ActionType.HARVEST and not state.plots[action.plot_index].ready:
            return False, "crop not ready"
        return True, "ok"

    if t == ActionType.FERTILIZE:
        if action.plot_index is None or not _valid_plot(action.plot_index, state):
            return False, "invalid plot index"
        plot = state.plots[action.plot_index]
        if plot.crop is None:
            return False, "no crop on plot"
        if plot.fertilized:
            return False, "already fertilized"
        if state.cash < 8.0:
            return False, "cannot afford fertilizer"
        return True, "ok"

    if t == ActionType.SELL:
        if not action.crop or state.inventory.get(action.crop, 0.0) <= 0:
            return False, "nothing to sell"
        return True, "ok"

    return False, "unknown action type"


def sanitize(action: Action, state: GameState) -> Action:
    """Return the action if legal, else a safe WAIT. The agent can never crash
    the sim by proposing something invalid."""
    legal, _ = is_legal(action, state)
    return action if legal else WAIT


def _valid_plot(index: int, state: GameState) -> bool:
    return 0 <= index < len(state.plots)
