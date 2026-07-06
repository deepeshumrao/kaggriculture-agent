"""Lightweight, opt-in logging.

Silent by default (library-friendly: attaches a NullHandler). Call
`enable_logging()` from a script to see warnings/info on the console.
Set the KAGGRICULTURE_LOG env var (e.g. DEBUG/INFO/WARNING) to control level.
"""

from __future__ import annotations

import logging
import os

_LOGGER_NAME = "kaggriculture"


def get_logger() -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    if not logger.handlers:
        logger.addHandler(logging.NullHandler())  # no output unless enabled
    return logger


def enable_logging(level: str | int | None = None) -> logging.Logger:
    """Attach a console handler. Level from arg, else env, else INFO."""
    logger = logging.getLogger(_LOGGER_NAME)
    # Remove the NullHandler / avoid duplicate console handlers.
    logger.handlers = [
        h for h in logger.handlers if not isinstance(h, logging.NullHandler)
    ]
    resolved = level or os.getenv("KAGGRICULTURE_LOG", "INFO")
    logger.setLevel(resolved)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(levelname)-7s %(name)s: %(message)s")
        )
        logger.addHandler(handler)
    _attach_scrubber(logger)
    return logger


def _attach_scrubber(logger: logging.Logger) -> None:
    """Ensure the secret-scrubbing filter is attached (Threat 2: no leaks)."""
    # Imported here to avoid a circular import at module load.
    from .security.scrubber import SecretScrubbingFilter

    if not any(isinstance(f, SecretScrubbingFilter) for f in logger.filters):
        logger.addFilter(SecretScrubbingFilter())
