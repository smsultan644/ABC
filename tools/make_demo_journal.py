"""Build a SYNTHETIC journal so the analytics pipeline can be smoke-tested.

THIS IS FABRICATED PRACTICE DATA. It exists only to exercise the code paths in
``analytics/``, ``reports/`` and the CLI. It is not market data, it is not a
backtest, and it must never be presented as evidence about any strategy.
"""

from __future__ import annotations

import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from forex_mastery.core.instruments import get_instrument  # noqa: E402
from forex_mastery.core.pip import pip_value_per_lot  # noqa: E402
from forex_mastery.journal.model import TradeRecord  # noqa: E402
from forex_mastery.journal.storage import JournalStore  # noqa: E402

SETUPS = ["trend_pullback", "range_reversal", "breakout_retest", "session_open"]
SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]  # deliberately conservative (demo only)
SESSIONS = ["London", "New York", "London-New York overlap"]
TIMEFRAMES = ["H1", "H4"]
EMOTIONS = ["calm", "neutral", "anxious", "confident"]


def build(target: Path, trades: int = 52, seed: int = 7) -> Path:
    rng = random.Random(seed)
    if target.exists():
        target.unlink()          # rebuild from scratch so re-runs do not duplicate rows
    store = JournalStore(target)
    equity = 250.0
    start = date(2026, 6, 1)
    day_cursor = start

    for index in range(1, trades + 1):
        symbol = rng.choice(SYMBOLS)
        spec = get_instrument(symbol)
        direction = rng.choice(["long", "short"])
        sign = 1 if direction == "long" else -1

        # Price levels: arbitrary but plausible-looking practice levels.
        if symbol == "USDJPY":
            entry = 150.0 + rng.uniform(-3.0, 3.0)
        elif symbol == "XAUUSD":
            entry = 2400.0 + rng.uniform(-80.0, 80.0)
        else:
            entry = 1.10 + rng.uniform(-0.05, 0.05)

        stop_pips = rng.choice([25.0, 35.0, 50.0, 70.0])
        stop = entry - sign * stop_pips * spec.pip_size
        rr_planned = rng.choice([1.5, 2.0, 2.5])
        tp = entry + sign * stop_pips * rr_planned * spec.pip_size

        risk_percent = 0.25
        prices = {"USDJPY": entry} if symbol == "USDJPY" else {}
        pip_value = pip_value_per_lot(symbol, "USD", lots=1.0, prices=prices)
        lots_raw = equity * risk_percent / 100.0 / (stop_pips * pip_value)
        lots = max(0.01, round(lots_raw, 2))

        won = rng.random() < 0.44
        if rng.random() < 0.06:  # breakeven / manual exit
            result_pips = rng.uniform(-8.0, 8.0)
        elif won:
            result_pips = stop_pips * rr_planned * rng.uniform(0.85, 1.0)
        else:
            result_pips = -stop_pips * rng.uniform(0.9, 1.05)

        exit_price = entry + sign * result_pips * spec.pip_size
        commission = 0.0
        swap = 0.0
        pnl = round(result_pips * pip_value * lots - commission - swap, 2)

        day_cursor = day_cursor + timedelta(days=rng.choice([1, 1, 2, 3]))
        if day_cursor.weekday() == 5:
            day_cursor += timedelta(days=2)
        entry_dt = datetime(day_cursor.year, day_cursor.month, day_cursor.day,
                            rng.choice([8, 9, 13, 14]), rng.choice([5, 17, 30, 45]))
        exit_dt = entry_dt + timedelta(hours=rng.choice([1, 2, 4, 6]))

        rules_followed = rng.random() > 0.12
        violations = "" if rules_followed else rng.choice(
            ["entered before the candle closed", "stop widened after entry",
             "took a second trade after a loss"]
        )
        record = TradeRecord(
            trade_id=f"T-{index:04d}",
            date=day_cursor.isoformat(),
            entry_time=entry_dt.strftime("%H:%M"),
            exit_time=exit_dt.strftime("%H:%M"),
            symbol=symbol,
            direction=direction,
            session=rng.choice(SESSIONS),
            timeframe=rng.choice(TIMEFRAMES),
            setup=rng.choice(SETUPS),
            setup_quality=rng.choice(["A", "B", "B", "C"]),
            entry=round(entry, 5),
            stop_loss=round(stop, 5),
            take_profit=round(tp, 5),
            lots=lots,
            account_equity_at_entry=round(equity, 2),
            risk_percent=risk_percent,
            planned_rr=rr_planned,
            exit_price=round(exit_price, 5),
            pnl=pnl,
            spread_at_entry_pips=round(rng.uniform(0.6, 2.4), 1),
            reason_for_entry="Practice record: setup matched the written plan conditions.",
            invalidation="Practice record: thesis invalidated if structure breaks against it.",
            reason_for_exit="Practice record: target or stop reached per plan.",
            thesis_valid=won,
            rules_followed=rules_followed,
            rule_violations=violations,
            emotional_state=rng.choice(EMOTIONS),
            mistakes="" if rules_followed else violations,
            lesson=rng.choice([
                "Waited for the close - the entry was cleaner.",
                "Position size correct; the loss was inside plan.",
                "Exited early out of fear; the plan said hold to target.",
                "Should have checked the calendar before entering.",
            ]),
            screenshot_before=f"shots/{'T-%04d' % index}_before.png",
            screenshot_after=f"shots/{'T-%04d' % index}_after.png",
        )
        store.add(record)
        equity = round(equity + pnl, 2)
    return target


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "outputs" / "demo_journal.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    build(out)
    store = JournalStore(out)
    summary = store.summary()
    print(f"wrote {out}")
    print(f"  trades={summary['total_records']} closed={summary['closed']} "
          f"net={summary['net_pnl']:.2f} win_rate={summary['win_rate']:.1f}%")
    print("  SYNTHETIC practice data - not market data, not evidence of an edge.")
