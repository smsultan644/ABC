"""
Test configuration.

Adds the repository root to ``sys.path`` so the test suite runs from a fresh
clone without an editable install:

    python -m pytest
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
