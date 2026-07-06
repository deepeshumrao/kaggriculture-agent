"""Security violation exception + threat taxonomy."""

from __future__ import annotations

from enum import Enum

from ..errors import KaggricultureError


class ThreatType(str, Enum):
    PROMPT_INJECTION = "PROMPT_INJECTION"
    SECRET_LEAKAGE = "SECRET_LEAKAGE"
    DATA_POISONING = "DATA_POISONING"
    DENIAL_OF_WALLET = "DENIAL_OF_WALLET"


class SecurityViolation(KaggricultureError):
    """Raised when a security threat forces execution to halt.

    Carries the threat type so callers/logs can react precisely.
    """

    def __init__(self, threat: ThreatType, detail: str) -> None:
        self.threat = threat
        self.detail = detail
        super().__init__(f"[{threat.value}] {detail}")
