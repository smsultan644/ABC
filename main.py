#!/usr/bin/env python3
"""
Forex Mastery System - entry point.

Run from the project root in VS Code's terminal (or any terminal):

    python main.py --help
    python main.py doctor
    python main.py position --symbol EURUSD --balance 250 --risk 0.25 \\
        --entry 1.1000 --stop 1.0950 --take-profit 1.1100 --leverage 100
    python main.py report --charts --pdf
    python main.py build all

The core calculation engine (`forex_mastery.core`) is pure standard library, so
most commands work on a fresh Python 3.10+ install with nothing else installed.
Optional features print the exact ``pip install`` command they need.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from forex_mastery.cli import main  # noqa: E402  (path setup must come first)

if __name__ == "__main__":
    raise SystemExit(main())
