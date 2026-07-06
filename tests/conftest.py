"""Pytest setup: make `src/` importable and keep tests hermetic.

We force the heuristic policy so the suite never makes live LLM/network calls,
regardless of any `.env` on the machine. LLM behavior is covered separately by
`test_llm_fallback.py` (which stubs the client).
"""

import os
import sys

os.environ["KAGGRICULTURE_POLICY"] = "heuristic"
os.environ.pop("GOOGLE_API_KEY", None)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
