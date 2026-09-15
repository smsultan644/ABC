"""
Forex Mastery System
====================

A structured, evidence-first forex education, risk-management, journaling and
analytics toolkit built around one principle:

    "Identify favourable probabilistic situations, define invalidation,
     control risk, execute consistently, collect sufficient data, analyse
     results, and continuously improve."

Design principles
-----------------
1. ``forex_mastery.core`` is **pure standard library**. Financial maths must
   never depend on a heavy third-party package to be correct or testable.
2. Nothing here predicts the market. The toolkit measures, sizes and audits.
3. Every formula has: a docstring, a plain-English explanation, and a unit test
   with a hand-checkable numerical example.
4. No guaranteed returns, no martingale, no grid "recovery", no signals.
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
