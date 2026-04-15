"""Helpers for making the ``src/`` tree importable as top-level packages."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_PATH = _REPO_ROOT / "src"


def ensure_src_on_path() -> None:
    """Insert ``<repo>/src`` at the head of ``sys.path`` if not already present.

    The legacy layout exposes modules like ``utils`` and ``write`` at the top
    level, so they need to be reachable via ``sys.path`` rather than as a
    package.
    """
    src_str = str(_SRC_PATH)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
