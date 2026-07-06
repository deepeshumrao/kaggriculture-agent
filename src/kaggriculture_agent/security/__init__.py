"""Security & Guardrail Monitor.

Defends the agent against four threat classes:
  1. Prompt injection / hijacking   -> injection.py
  2. Secret leakage                 -> scrubber.py
  3. Data poisoning / manipulation  -> validation.py
  4. Denial of wallet (unbounded)   -> budget.py

`SecurityMonitor` (monitor.py) orchestrates all four.
"""

from .budget import BudgetMonitor
from .injection import detect_injection, is_injection
from .monitor import SecurityMonitor
from .scrubber import scrub, SecretScrubbingFilter
from .validation import sanitize_state
from .violations import SecurityViolation, ThreatType

__all__ = [
    "SecurityMonitor",
    "BudgetMonitor",
    "detect_injection",
    "is_injection",
    "scrub",
    "SecretScrubbingFilter",
    "sanitize_state",
    "SecurityViolation",
    "ThreatType",
]
