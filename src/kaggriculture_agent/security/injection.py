"""Threat 1 — Prompt injection / hijacking detection.

External data that flows into an LLM prompt (e.g. simulated market/weather text,
crop names, messages) is UNTRUSTED. This module scans such text for attempts to
override the agent's instructions or hijack its goal.
"""

from __future__ import annotations

import re

# Phrases commonly used to hijack an LLM. Case-insensitive substring / regex.
_INJECTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?i)ignore\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions|directives|prompts)"),
    re.compile(r"(?i)disregard\s+(all\s+)?(previous|prior|your)\s+\w+"),
    re.compile(r"(?i)forget\s+(everything|all|your\s+instructions)"),
    re.compile(r"(?i)you\s+are\s+now\s+(a|an|the)\b"),
    re.compile(r"(?i)new\s+(instructions|task|system\s+prompt|directive)\s*[:>-]"),
    re.compile(r"(?i)(system|developer)\s*(prompt|message)\s*[:>]"),
    re.compile(r"(?i)override\s+(your|the|all)\s+(goal|instructions|rules)"),
    re.compile(r"(?i)act\s+as\s+(if|a|an)\b"),
    re.compile(r"(?i)reveal|print|show|output.*(api[_-]?key|secret|password|env|credentials?)"),
    re.compile(r"(?i)sell\s+everything.*(immediately|now).*(zero|0|free|any\s+price)"),
    re.compile(r"(?i)transfer|send.*(cash|money|funds).*to"),
    re.compile(r"<\s*/?\s*(system|assistant|user|im_start|im_end)\s*>"),  # role tags
]


def detect_injection(text: str) -> list[str]:
    """Return a list of matched injection patterns (empty = clean)."""
    if not text:
        return []
    hits: list[str] = []
    for pat in _INJECTION_PATTERNS:
        m = pat.search(text)
        if m:
            hits.append(m.group(0))
    return hits


def is_injection(text: str) -> bool:
    return bool(detect_injection(text))
