"""Threat 2 — Secret leakage prevention.

`scrub()` redacts anything that looks like a credential from any string before
it is logged or written to disk. `SecretScrubbingFilter` attaches this to the
logging system so NO log record can leak a secret, even accidentally.
"""

from __future__ import annotations

import logging
import os
import re

_REDACTION = "***REDACTED***"

# Patterns for common secret shapes. Order matters (specific -> general).
_PATTERNS: list[re.Pattern] = [
    # Google AI Studio / GCP style keys: "AIza" + 35 chars
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    # OAuth-ish tokens like the one the user pasted: "AQ." + long blob
    re.compile(r"\bAQ\.[0-9A-Za-z\-_]{20,}"),
    # Bearer tokens
    re.compile(r"(?i)bearer\s+[0-9A-Za-z\-_\.=]{16,}"),
    # Generic "KEY=value" / "token: value" assignments in text
    re.compile(
        r"(?i)(api[_-]?key|secret|token|password|passwd|credential)"
        r"\s*[:=]\s*[^\s'\"]+"
    ),
    # Long high-entropy-ish blobs (40+ base64/hex chars)
    re.compile(r"\b[0-9A-Za-z\-_]{40,}\b"),
]


def scrub(text: str) -> str:
    """Return `text` with any secret-looking substrings redacted."""
    if not text:
        return text
    out = text
    # Redact known env-var secret VALUES explicitly (exact-match, strongest).
    for name in ("GOOGLE_API_KEY", "GEMINI_API_KEY", "KAGGLE_KEY"):
        val = os.getenv(name)
        if val and len(val) >= 8:
            out = out.replace(val, _REDACTION)
    # Then apply structural patterns.
    for pat in _PATTERNS:
        out = pat.sub(_redact_match, out)
    return out


def _redact_match(m: re.Match) -> str:
    text = m.group(0)
    # For "key=value" style, keep the label, redact the value.
    if "=" in text or ":" in text:
        sep = "=" if "=" in text else ":"
        label = text.split(sep, 1)[0]
        return f"{label}{sep} {_REDACTION}"
    return _REDACTION


class SecretScrubbingFilter(logging.Filter):
    """Logging filter that scrubs every record's message + args."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            record.msg = scrub(str(record.getMessage()))
            record.args = ()  # message is now fully rendered + scrubbed
        except Exception:
            record.msg = _REDACTION
            record.args = ()
        return True
