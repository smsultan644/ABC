"""
Core calculation engine (pure standard library).

Modules
-------
instruments   : instrument specifications (pip size, contract size, lot rules)
pip           : pip/pipette/point conversion and pip value
position_size : risk-based position sizing (the most important calculation)
margin        : required margin, free margin, margin level, stop-out distance
risk          : R-multiples, risk/reward, drawdown maths, expectancy helpers
metrics       : performance statistics from a list of closed trades
risk_of_ruin  : gambler's-ruin maths + Monte Carlo risk-of-ruin simulation
compounding   : growth/decay projection used for scenario planning
sessions      : market-session logic in UTC (DST-correct via zoneinfo)
rule_engine   : configurable IF-THEN trading rule evaluation (Level 26)
validation    : shared input validation + typed warning/error reporting
"""

from __future__ import annotations

__all__: list[str] = []
