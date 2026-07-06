"""Custom exception hierarchy for the Kaggriculture agent.

Using specific exception types (instead of bare asserts / generic Exceptions)
makes failures explicit, catchable, and safe under `python -O` (which strips
asserts).
"""

from __future__ import annotations


class KaggricultureError(Exception):
    """Base class for all errors raised by this project."""


class SimNotStartedError(KaggricultureError):
    """A sim method was called before reset()."""


class SimError(KaggricultureError):
    """The simulation backend failed while stepping/observing."""


class PolicyError(KaggricultureError):
    """A decision policy failed to produce a usable action."""


class LLMError(KaggricultureError):
    """The LLM backend failed (network, quota, or bad response)."""
