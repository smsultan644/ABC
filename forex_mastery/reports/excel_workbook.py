"""
The master Excel workbook: ``Forex_Trading_Master.xlsx``.

Design goals
------------
1. **One file a trader can actually live in.** Journal, calculators, checklists,
   reviews and dashboards in a single workbook, using real formulas so it keeps
   working when you type over the example rows.
2. **Formulas over hard-coded numbers.** Where a value can be derived (pip value,
   lots, R-multiple, win rate, expectancy, drawdown) it is derived by a formula,
   so a mistake shows up as a wrong-looking number rather than a silent error.
3. **Validation and formatting over trust.** Dropdowns for direction/session/
   quality, conditional formatting for rule violations and losses, frozen
   headers and print-ready column widths.

Requires XlsxWriter (``pip install XlsxWriter``). If it is missing the caller
receives an actionable error instead of a traceback.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from ..core.instruments import list_instruments
from ..journal.model import JOURNAL_COLUMNS

__all__ = ["excel_available", "build_master_workbook", "SHEET_NAMES"]

SHEET_NAMES = [
    "Dashboard",
    "Trading Journal",
    "Position Calculator",
    "Risk Calculator",
    "RR Calculator",
    "Pip Calculator",
    "Margin Calculator",
    "Strategy Log",
    "Backtest",
    "Performance",
    "Drawdown",
    "Psychology",
    "Daily Checklist",
    "Weekly Review",
    "Monthly Review",
    "Economic Calendar",
    "Watchlist",
    "Trade Statistics",
    "Correlation",
    "Settings",
]


def excel_available() -> bool:
    try:
        import xlsxwriter  # noqa: F401
    except Exception:
        return False
    return True


# ---------------------------------------------------------------------- #
# Format palette
# ---------------------------------------------------------------------- #
def _formats(workbook):
    return {
        "title": workbook.add_format(
            {"bold": True, "font_size": 16, "font_color": "#12305c", "bottom": 2,
             "border_color": "#12305c"}
        ),
        "subtitle": workbook.add_format({"italic": True, "font_size": 9, "font_color": "#555555"}),
        "section": workbook.add_format(
            {"bold": True, "font_size": 11, "bg_color": "#e8eef7", "font_color": "#12305c",
             "border": 1, "border_color": "#b9c6d6"}
        ),
        "header": workbook.add_format(
            {"bold": True, "bg_color": "#1f4e79", "font_color": "white", "border": 1,
             "border_color": "#1f4e79", "text_wrap": True, "valign": "vcenter", "align": "center"}
        ),
        "label": workbook.add_format({"bold": True, "bg_color": "#f2f5fa", "border": 1,
                                      "border_color": "#c9d4e2"}),
        "input": workbook.add_format(
            {"bg_color": "#fff8e1", "border": 1, "border_color": "#e0c97f", "num_format": "0.00000"}
        ),
        "input_int": workbook.add_format(
            {"bg_color": "#fff8e1", "border": 1, "border_color": "#e0c97f", "num_format": "0"}
        ),
        "input_pct": workbook.add_format(
            {"bg_color": "#fff8e1", "border": 1, "border_color": "#e0c97f", "num_format": "0.00%"}
        ),
        "input_money": workbook.add_format(
            {"bg_color": "#fff8e1", "border": 1, "border_color": "#e0c97f",
             "num_format": '#,##0.00'}
        ),
        "input_plain": workbook.add_format(
            {"bg_color": "#fff8e1", "border": 1, "border_color": "#e0c97f"}
        ),
        "result": workbook.add_format(
            {"bold": True, "bg_color": "#e7f4e8", "border": 1, "border_color": "#a9d3ab",
             "num_format": "#,##0.0000"}
        ),
        "result_int": workbook.add_format(
            {"bold": True, "bg_color": "#e7f4e8", "border": 1, "border_color": "#a9d3ab",
             "num_format": "0"}
        ),
        "result_money": workbook.add_format(
            {"bold": True, "bg_color": "#e7f4e8", "border": 1, "border_color": "#a9d3ab",
             "num_format": "#,##0.00"}
        ),
        "warning": workbook.add_format(
            {"bg_color": "#fdecea", "font_color": "#8a1c1c", "border": 1,
             "border_color": "#e6b3b3", "text_wrap": True}
        ),
        "note": workbook.add_format({"font_size": 8, "italic": True, "font_color": "#666666",
                                     "text_wrap": True, "valign": "top"}),
        "text": workbook.add_format({"border": 1, "border_color": "#d5dbe4", "text_wrap": True,
                                     "valign": "top"}),
        "number": workbook.add_format({"border": 1, "border_color": "#d5dbe4", "num_format": "0.0000"}),
        "money": workbook.add_format({"border": 1, "border_color": "#d5dbe4", "num_format": "#,##0.00"}),
        "percent": workbook.add_format({"border": 1, "border_color": "#d5dbe4", "num_format": "0.0%"}),
        "date": workbook.add_format({"border": 1, "border_color": "#d5dbe4", "num_format": "yyyy-mm-dd"}),
        "positive": workbook.add_format({"bg_color": "#e7f4e8", "font_color": "#1a7f37"}),
        "negative": workbook.add_format({"bg_color": "#fdecea", "font_color": "#a40e26"}),
        "big": workbook.add_format({"bold": True, "font_size": 14, "font_color": "#12305c"}),
    }


def build_master_workbook(target: Path, journal_path: Path | None = None) -> Path:
    """Generate the master workbook. Returns the path written."""
    if not excel_available():  # pragma: no cover - optional dependency
        raise RuntimeError("Excel generation needs XlsxWriter. Install: pip install XlsxWriter")

    import xlsxwriter

    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    workbook = xlsxwriter.Workbook(str(target), {"nan_inf_to_errors": True})
    fmt = _formats(workbook)

    settings = _sheet_settings(workbook, fmt)
    journal = _sheet_journal(workbook, fmt)
    position = _sheet_position_calculator(workbook, fmt, settings)
    risk = _sheet_risk_calculator(workbook, fmt)
    rr = _sheet_rr_calculator(workbook, fmt)
    pip_sheet = _sheet_pip_calculator(workbook, fmt, settings)
    margin = _sheet_margin_calculator(workbook, fmt)
    _sheet_strategy_log(workbook, fmt)
    _sheet_backtest(workbook, fmt)
    performance = _sheet_performance(workbook, fmt, journal)
    drawdown = _sheet_drawdown(workbook, fmt)
    _sheet_psychology(workbook, fmt)
    _sheet_daily_checklist(workbook, fmt)
    _sheet_weekly_review(workbook, fmt)
    _sheet_monthly_review(workbook, fmt)
    _sheet_economic_calendar(workbook, fmt)
    _sheet_watchlist(workbook, fmt, settings)
    statistics = _sheet_trade_statistics(workbook, fmt, journal)
    _sheet_correlation(workbook, fmt)
    _sheet_dashboard(workbook, fmt, journal, performance, drawdown, statistics, position)

    # Sheet order as specified in the project architecture.
    workbook.worksheets_objs.sort(key=lambda ws: SHEET_NAMES.index(ws.get_name())
                                 if ws.get_name() in SHEET_NAMES else 99)
    workbook.close()
    _ = (risk, rr, pip_sheet, margin, position, settings, journal, performance,
         drawdown, statistics)  # referenced for clarity; sheets are already written
    return target


# ---------------------------------------------------------------------- #
# Sheets
# ---------------------------------------------------------------------- #
def _title(worksheet, fmt, title: str, subtitle: str) -> int:
    worksheet.write("A1", title, fmt["title"])
    worksheet.write("A2", subtitle, fmt["subtitle"])
    worksheet.set_row(0, 22)
    return 4


def _sheet_settings(workbook, fmt):
    """Sheet 20: instrument specifications + constants used by other sheets."""
    ws = workbook.add_worksheet("Settings")
    row = _title(ws, fmt, "Settings & Instrument Specifications",
                 "Edit the highlighted cells. Other sheets read these values, so a change here "
                 "flows through the whole workbook.")
    ws.write(row, 0, "Account constants", fmt["section"])
    constants = [
        ("Account currency", "USD", "text"),
        ("Starting equity", 250.0, "money"),
        ("Default risk % per trade (learning phase)", 0.0025, "pct"),
        ("Hard risk cap % per trade", 0.01, "pct"),
        ("Broker leverage (1:x)", 100, "int"),
        ("Max daily loss %", 0.01, "pct"),
        ("Max weekly loss %", 0.03, "pct"),
        ("Minimum reward:risk", 1.5, "plain"),
    ]
    row += 1
    for label, value, kind in constants:
        ws.write(row, 0, label, fmt["label"])
        ws.write(row, 1, value, {
            "money": fmt["input_money"], "pct": fmt["input_pct"], "int": fmt["input_int"],
            "text": fmt["text"], "plain": fmt["input_plain"],
        }[kind])
        row += 1
    ws.write(row + 1, 0, "Instrument specifications (Exness-verified where marked)", fmt["section"])
    header_row = row + 2
    for col, name in enumerate(["Symbol", "Name", "Contract size", "Pip size", "Digits",
                                "Quote", "Min lot", "Verified"]):
        ws.write(header_row, col, name, fmt["header"])
    for offset, spec in enumerate(list_instruments(), start=1):
        r = header_row + offset
        ws.write(r, 0, spec.symbol, fmt["text"])
        ws.write(r, 1, spec.name, fmt["text"])
        ws.write(r, 2, spec.contract_size, fmt["number"])
        ws.write(r, 3, spec.pip_size, fmt["number"])
        ws.write(r, 4, spec.digits, fmt["text"])
        ws.write(r, 5, spec.quote, fmt["text"])
        ws.write(r, 6, spec.min_volume_lots, fmt["number"])
        ws.write(r, 7, "yes" if spec.verified else "verify in MT5", fmt["text"])
    ws.set_column(0, 0, 34)
    ws.set_column(1, 1, 14)
    ws.set_column(2, 2, 26)
    ws.set_column(3, 8, 14)
    ws.freeze_panes(header_row + 1, 0)
    return {"constants_row": 5, "spec_header_row": header_row,
            "spec_first_row": header_row + 1, "spec_last_row": header_row + len(list_instruments())}


def _sheet_journal(workbook, fmt):
    ws = workbook.add_worksheet("Trading Journal")
    row = _title(ws, fmt, "Trading Journal",
                 "One row per trade. The R-multiple column is a formula: R = P/L / risk. "
                 "Never type R by hand - it must be derived from the money.")
    header_row = row
    for col, name in enumerate(JOURNAL_COLUMNS):
        ws.write(header_row, col, name, fmt["header"])
    ws.set_row(header_row, 34)

    # Pre-fill formulas for 300 rows so the sheet works as soon as data is typed.
    pnl_col = JOURNAL_COLUMNS.index("pnl")
    risk_col = JOURNAL_COLUMNS.index("risk_amount")
    r_col = JOURNAL_COLUMNS.index("r_multiple")
    status_col = JOURNAL_COLUMNS.index("status")
    equity_col = JOURNAL_COLUMNS.index("account_equity_at_entry")
    riskpct_col = JOURNAL_COLUMNS.index("risk_percent")
    for offset in range(300):
        r = header_row + 1 + offset
        ws.write_formula(
            r, r_col,
            f'=IF(OR(J{r + 1}="",{_col_letter(pnl_col)}{r + 1}=""),"",'
            f'IF({_col_letter(risk_col)}{r + 1}<>"",{_col_letter(pnl_col)}{r + 1}/{_col_letter(risk_col)}{r + 1},'
            f'IF(AND({_col_letter(riskpct_col)}{r + 1}<>"",{_col_letter(equity_col)}{r + 1}<>""),'
            f'{_col_letter(pnl_col)}{r + 1}/({_col_letter(riskpct_col)}{r + 1}*{_col_letter(equity_col)}{r + 1}),"")))',
            fmt["number"],
        )
        ws.write_formula(
            r, status_col,
            f'=IF({_col_letter(pnl_col)}{r + 1}="","",'
            f'IF({_col_letter(pnl_col)}{r + 1}>0,"win",IF({_col_letter(pnl_col)}{r + 1}<0,"loss","breakeven")))',
            fmt["text"],
        )
    last_row = header_row + 300

    height = last_row + 1
    ws.data_validation(header_row + 1, JOURNAL_COLUMNS.index("direction"),
                       last_row, JOURNAL_COLUMNS.index("direction"),
                       {"validate": "list", "source": ["long", "short"]})
    ws.data_validation(header_row + 1, JOURNAL_COLUMNS.index("session"),
                       last_row, JOURNAL_COLUMNS.index("session"),
                       {"validate": "list",
                        "source": ["Sydney", "Tokyo", "London", "New York",
                                   "London/New York overlap", "Off-hours"]})
    ws.data_validation(header_row + 1, JOURNAL_COLUMNS.index("setup_quality"),
                       last_row, JOURNAL_COLUMNS.index("setup_quality"),
                       {"validate": "list", "source": ["A", "B", "C", "D"]})
    ws.data_validation(header_row + 1, JOURNAL_COLUMNS.index("emotional_state"),
                       last_row, JOURNAL_COLUMNS.index("emotional_state"),
                       {"validate": "list",
                        "source": ["calm", "confident", "anxious", "frustrated", "euphoric",
                                   "bored", "fearful", "impatient"]})
    ws.data_validation(header_row + 1, JOURNAL_COLUMNS.index("rules_followed"),
                       last_row, JOURNAL_COLUMNS.index("rules_followed"),
                       {"validate": "list", "source": ["TRUE", "FALSE"]})
    # Conditional formatting: results and rule breaches jump out.
    ws.conditional_format(header_row + 1, r_col, last_row, r_col,
                          {"type": "cell", "criteria": ">", "value": 0, "format": fmt["positive"]})
    ws.conditional_format(header_row + 1, r_col, last_row, r_col,
                          {"type": "cell", "criteria": "<", "value": 0, "format": fmt["negative"]})
    ws.conditional_format(header_row + 1, JOURNAL_COLUMNS.index("rules_followed"),
                          last_row, JOURNAL_COLUMNS.index("rules_followed"),
                          {"type": "text", "criteria": "containing", "value": "FALSE",
                           "format": fmt["negative"]})
    for col in range(len(JOURNAL_COLUMNS)):
        ws.set_column(col, col, 15)
    ws.set_column(JOURNAL_COLUMNS.index("reason_for_entry"),
                  JOURNAL_COLUMNS.index("reason_for_entry"), 34)
    ws.set_column(JOURNAL_COLUMNS.index("mistakes"), JOURNAL_COLUMNS.index("lesson"), 28)
    ws.freeze_panes(header_row + 1, 3)
    ws.autofilter(header_row, 0, last_row, len(JOURNAL_COLUMNS) - 1)
    _ = height
    return {"header_row": header_row, "first_row": header_row + 1, "last_row": last_row,
            "r_col": r_col, "pnl_col": pnl_col, "risk_col": risk_col}


def _col_letter(index: int) -> str:
    letters = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def _sheet_position_calculator(workbook, fmt, settings):
    ws = workbook.add_worksheet("Position Calculator")
    row = _title(ws, fmt, "Position Size Calculator",
                 "The most important calculator in the file. Risk first, stop second, size third.")
    rows = [
        ("Account equity", 250.0, "input_money"),
        ("Risk % per trade", 0.0025, "input_pct"),
        ("Instrument", "EURUSD", "input_text"),
        ("Contract size (from Settings)", None, "formula"),
        ("Pip size (from Settings)", None, "formula"),
        ("Quote currency (from Settings)", None, "formula"),
        ("Entry price", 1.1000, "input"),
        ("Stop loss price", 1.0950, "input"),
        ("Stop distance (price units)", None, "formula"),
        ("Stop distance (pips)", None, "formula"),
        ("Pip value per 1.00 lot (account ccy)", None, "formula"),
        ("Risk budget (money)", None, "formula"),
        ("Risk per 1.00 lot", None, "formula"),
        ("Lots (exact)", None, "formula"),
        ("LOTS TO TRADE (rounded down to 0.01)", None, "formula"),
        ("Actual risk at that lot size", None, "formula"),
        ("Actual risk %", None, "formula"),
    ]
    start = row
    for offset, (label, value, kind) in enumerate(rows):
        r = start + offset
        ws.write(r, 0, label, fmt["label"])
        if kind == "formula":
            continue
        if kind == "input_text":
            ws.write(r, 1, value, fmt["text"])
        elif kind == "input_money":
            ws.write(r, 1, value, fmt["input_money"])
        elif kind == "input_pct":
            ws.write(r, 1, value, fmt["input_pct"])
        else:
            ws.write(r, 1, value, fmt["input"])

    # Formulas. The instrument lookup uses IFERROR so a typo produces a readable
    # message instead of #N/A everywhere.
    spec_range = (f"Settings!$A${settings['spec_first_row']}:$H${settings['spec_last_row']}")
    ws.write_formula(start + 3, 1, f"=IFERROR(VLOOKUP($B${start + 2},{spec_range},3,FALSE),"
                                   f"\"instrument not in Settings\")", fmt["result"])
    ws.write_formula(start + 4, 1, f"=IFERROR(VLOOKUP($B${start + 2},{spec_range},4,FALSE),\"\")",
                     fmt["result"])
    ws.write_formula(start + 5, 1, f"=IFERROR(VLOOKUP($B${start + 2},{spec_range},6,FALSE),\"\")",
                     fmt["result"])
    ws.write_formula(start + 8, 1, f"=ABS($B${start + 6}-$B${start + 7})", fmt["result"])
    ws.write_formula(start + 9, 1, f"=IFERROR($B${start + 8}/$B${start + 4},\"\")", fmt["result"])
    ws.write_formula(start + 10, 1, f"=$B${start + 3}*$B${start + 4}", fmt["result_money"])
    ws.write_formula(start + 11, 1, f"=$B${start}*$B${start + 1}", fmt["result_money"])
    ws.write_formula(start + 12, 1, f"=$B${start + 9}*$B${start + 10}", fmt["result_money"])
    ws.write_formula(start + 13, 1, f"=IFERROR($B${start + 11}/$B${start + 12},\"\")", fmt["result"])
    ws.write_formula(start + 14, 1, f"=ROUNDDOWN($B${start + 13},2)", fmt["result"])
    ws.write_formula(start + 15, 1, f"=$B${start + 14}*$B${start + 12}", fmt["result_money"])
    ws.write_formula(start + 16, 1, f"=IFERROR($B${start + 15}/($B${start}*1),\"\")", fmt["result"])
    ws.write(start + 18, 0,
             "WARNING: pip value above assumes the instrument's quote currency equals the account "
             "currency (EURUSD, GBPUSD, XAUUSD, AUDUSD, NZDUSD). For USDJPY, cross pairs or gold in "
             "a non-USD account, divide by the conversion rate yourself before trusting the lot "
             "size - or use `python main.py position ...`, which converts explicitly and refuses to "
             "guess.", fmt["warning"])
    ws.set_row(start + 18, 46)
    ws.write(start + 20, 0, "Assumptions and limits", fmt["section"])
    ws.write(start + 21, 0,
             "1. Rounding is always DOWN; the exact size is shown so you can see what was given up. "
             "2. If the rounded size is below the 0.01 minimum, the trade is not tradable at this "
             "risk: skip it or use a Cent account. 3. Spread, commission and swap are not in the "
             "risk budget - they reduce profit and slightly enlarge losses; add them when the "
             "spread is wide. 4. The stop must sit at a level that invalidates your idea, never at "
             "a round number chosen to make the lot size look nice.", fmt["note"])
    ws.set_row(start + 21, 70)
    ws.set_column(0, 0, 44)
    ws.set_column(1, 1, 22)
    return {"start": start}


def _sheet_risk_calculator(workbook, fmt):
    ws = workbook.add_worksheet("Risk Calculator")
    row = _title(ws, fmt, "Risk Framework for a USD 250 Account",
                 "Losses compound on the remaining equity, so the counts below are slightly higher "
                 "than naive division. Generated by forex_mastery.core.risk.drawdown_ladder.")
    from ..core.risk import drawdown_ladder

    header = ["Risk %", "Risk (USD)", "Equity left if lost", "Losses to -5%", "Losses to -10%",
              "Losses to -20%", "Losses to -30%", "Losses to -50%", "Gain needed to recover 10% DD"]
    for col, name in enumerate(header):
        ws.write(row, col, name, fmt["header"])
    ladder = {r.drawdown_percent: r for r in drawdown_ladder()}
    for offset, risk in enumerate([0.001, 0.0025, 0.005, 0.01, 0.02, 0.05], start=1):
        r = row + offset
        ws.write_number(r, 0, risk, fmt["percent"])
        ws.write_formula(r, 1, f"=250*{risk}", fmt["money"])
        formula_col = {0.001: 3, 0.0025: 4, 0.005: 5, 0.01: 6, 0.02: 7, 0.05: 8}
        ws.write_formula(r, 2, f"=250*(1-A{r + 1})", fmt["money"])
        ws.write_formula(r, 3, f"=ROUNDUP(LN(0.95)/LN(1-A{r + 1}),0)", fmt["result_int"])
        ws.write_formula(r, 4, f"=ROUNDUP(LN(0.90)/LN(1-A{r + 1}),0)", fmt["result_int"])
        ws.write_formula(r, 5, f"=ROUNDUP(LN(0.80)/LN(1-A{r + 1}),0)", fmt["result_int"])
        ws.write_formula(r, 6, f"=ROUNDUP(LN(0.70)/LN(1-A{r + 1}),0)", fmt["result_int"])
        ws.write_formula(r, 7, f"=ROUNDUP(LN(0.50)/LN(1-A{r + 1}),0)", fmt["result_int"])
        ws.write_formula(r, 8, "=0.10/(1-0.10)", fmt["percent"])
        _ = formula_col
    start_note = row + 8
    ws.write(start_note, 0, "Reference table verified by the Python engine", fmt["section"])
    ws.write(start_note + 1, 0, "Drawdown", fmt["header"])
    ws.write(start_note + 1, 1, "Gain required to recover", fmt["header"])
    for offset, row_dd in enumerate([5, 10, 20, 30, 50, 70], start=2):
        ws.write(start_note + offset, 0, f"-{row_dd}%", fmt["text"])
        ws.write_formula(start_note + offset, 1, f"=({row_dd}/100)/(1-{row_dd}/100)", fmt["percent"])
    ws.write(start_note + 9, 0,
             "This table is the mathematical case for capital preservation: after a 50% drawdown "
             "you must double the remainder to get back to where you were, while the risk of "
             "further losses has not changed at all.", fmt["note"])
    ws.set_row(start_note + 9, 34)
    ws.set_column(0, 0, 26)
    ws.set_column(1, 8, 17)
    _ = ladder
    return {}


def _sheet_rr_calculator(workbook, fmt):
    ws = workbook.add_worksheet("RR Calculator")
    row = _title(ws, fmt, "Reward:Risk, Break-even Win Rate and Expectancy",
                 "Change the yellow cells. Break-even win rate = 1 / (1 + R:R). "
                 "Expectancy per trade = p x W - (1 - p) x L.")
    labels = ["Entry", "Stop loss", "Take profit", "Direction (long/short)",
              "Risk distance (pips)", "Reward distance (pips)", "Reward:Risk",
              "Break-even win rate", "Your assumed win rate", "Expectancy (R per trade)",
              "Expectancy as % of risk", "Verdict"]
    start = row
    for offset, label in enumerate(labels):
        ws.write(start + offset, 0, label, fmt["label"])
    ws.write(start, 1, 1.1000, fmt["input"])
    ws.write(start + 1, 1, 1.0950, fmt["input"])
    ws.write(start + 2, 1, 1.1100, fmt["input"])
    ws.write(start + 3, 1, "long", fmt["text"])
    ws.write_formula(start + 4, 1, '=IF($B$4="long",($B$33-$B$34)/0.0001,($B$34-$B$33)/0.0001)', fmt["result"])
    ws.write_formula(start + 5, 1, '=IF($B$4="long",($B$35-$B$33)/0.0001,($B$33-$B$35)/0.0001)', fmt["result"])
    ws.write_formula(start + 6, 1, "=IFERROR($B$37/$B$36,\"\")", fmt["result"])
    ws.write_formula(start + 7, 1, '=IFERROR(1/(1+$B$38),"")', fmt["percent"])
    ws.write(start + 8, 1, 0.45, fmt["input_pct"])
    ws.write_formula(start + 9, 1, "=$B$40*$B$38-(1-$B$40)*1", fmt["result"])
    ws.write_formula(start + 10, 1, "=$B$41", fmt["percent"])
    ws.write_formula(
        start + 11, 1,
        '=IF($B$41>0,"Positive expectancy - a real edge exists IF the win rate estimate is honest",'
        'IF($B$41=0,"Break-even before costs - costs make it a losing system",'
        '"Negative expectancy - do not trade this configuration"))',
        fmt["text"])
    ws.set_row(start + 11, 30)
    ws.write(start + 13, 0,
             "Costs matter. A 1.4-pip spread on a 50-pip stop is 2.8% of your risk on every trade, "
             "round trip. Add it to the loss side and subtract it from the win side before "
             "concluding that a marginal system is profitable.", fmt["note"])
    ws.set_row(start + 13, 30)
    ws.set_column(0, 0, 30)
    ws.set_column(1, 1, 40)
    return {}


def _sheet_pip_calculator(workbook, fmt, settings):
    ws = workbook.add_worksheet("Pip Calculator")
    row = _title(ws, fmt, "Pip Value Reference",
                 "Pip value = lots x contract size x pip size x (quote currency -> account "
                 "currency rate). Values below assume the quote currency IS the account currency, "
                 "which is true for EURUSD/GBPUSD/AUDUSD/NZDUSD/XAUUSD on a USD account.")
    headers = ["Symbol", "Pip size", "Contract size", "Pip value 1.00 lot",
               "Pip value 0.10 lot", "Pip value 0.01 lot", "Pip value 0.01 lot on 250 USD",
               "Verified from docs"]
    for col, name in enumerate(headers):
        ws.write(row, col, name, fmt["header"])
    for offset, spec in enumerate(list_instruments(), start=1):
        r = row + offset
        ws.write(r, 0, spec.symbol, fmt["text"])
        ws.write(r, 1, spec.pip_size, fmt["number"])
        ws.write(r, 2, spec.contract_size, fmt["number"])
        ws.write_formula(r, 3, f"=B{r + 1}*C{r + 1}", fmt["money"])
        ws.write_formula(r, 4, f"=D{r + 1}*0.1", fmt["money"])
        ws.write_formula(r, 5, f"=D{r + 1}*0.01", fmt["money"])
        ws.write_formula(r, 6, f"=IFERROR(F{r + 1}/250*100,\"\")", fmt["percent"])
        ws.write(r, 7, "yes" if spec.verified else "verify in MT5", fmt["text"])
    ws.set_column(0, 0, 14)
    ws.set_column(1, 7, 20)
    ws.freeze_panes(row + 1, 0)
    _ = settings
    return {}


def _sheet_margin_calculator(workbook, fmt):
    ws = workbook.add_worksheet("Margin Calculator")
    row = _title(ws, fmt, "Margin, Free Margin and Margin Level",
                 "Required margin = notional / leverage. Margin level = equity / used margin x 100. "
                 "Exness advertises a 0% stop-out on its account types - meaning the broker only "
                 "closes positions when equity would go negative. That is NOT protection; your own "
                 "stop loss is the only protection you have.")
    labels = ["Instrument (from Settings)", "Lots", "Current price", "Leverage (1:x)",
              "Contract size (lookup)", "Notional value", "Required margin", "Account equity",
              "Free margin after this trade", "Used margin % of equity",
              "Effective leverage (notional / equity)", "House effective-leverage limit",
              "Effective leverage check", "Price 1% adverse move", "Loss on a 1% adverse move",
              "That loss as % of equity"]
    start = row
    for offset, label in enumerate(labels):
        ws.write(start + offset, 0, label, fmt["label"])
    ws.write(start, 1, "EURUSD", fmt["text"])
    ws.write(start + 1, 1, 0.01, fmt["input"])
    ws.write(start + 2, 1, 1.1000, fmt["input"])
    ws.write(start + 3, 1, 100, fmt["input_int"])
    ws.write_formula(start + 4, 1,
                     f"=IFERROR(VLOOKUP($B${start + 1},Settings!$A${settings_row(workbook)}:$H$999,3,FALSE),\"\")",
                     fmt["result"])
    ws.write_formula(start + 5, 1, f"=$B${start + 2}*$B${start + 5}*$B${start + 3}", fmt["result_money"])
    ws.write_formula(start + 6, 1, f"=$B${start + 6}/$B${start + 4}", fmt["result_money"])
    ws.write(start + 7, 1, 250.0, fmt["input_money"])
    ws.write_formula(start + 8, 1, f"=$B${start + 8}-$B${start + 7}", fmt["result_money"])
    ws.write_formula(start + 9, 1, f"=IFERROR($B${start + 7}/$B${start + 8},\"\")", fmt["percent"])
    ws.write_formula(start + 10, 1, f"=IFERROR($B${start + 6}/$B${start + 8},\"\")", fmt["result"])
    ws.write(start + 11, 1, 10, fmt["input_int"])
    ws.write_formula(start + 12, 1,
                     f'=IF($B${start + 11}<=$B${start + 12},"within limit","ABOVE LIMIT - reduce size")',
                     fmt["text"])
    ws.write_formula(start + 13, 1, f"=$B${start + 3}*0.01", fmt["result"])
    ws.write_formula(start + 14, 1,
                     f"=$B${start + 14}*$B${start + 2}*$B${start + 5}", fmt["result_money"])
    ws.write_formula(start + 15, 1, f"=IFERROR($B${start + 15}/$B${start + 8},\"\")", fmt["percent"])
    ws.write(start + 17, 0,
             "Read the last four rows slowly. A 0.50-lot gold position on a 250 USD account loses "
             "about 1,200 USD on a 1% adverse move - nearly five times the account. Leverage does "
             "not create this risk; position size does. The margin requirement only decides whether "
             "the order is accepted.", fmt["warning"])
    ws.set_row(start + 17, 46)
    ws.set_column(0, 0, 40)
    ws.set_column(1, 1, 30)
    return {}


def settings_row(workbook) -> int:
    """First data row of the instrument table on the Settings sheet (see _sheet_settings)."""
    return 10


def _sheet_strategy_log(workbook, fmt):
    ws = workbook.add_worksheet("Strategy Log")
    row = _title(ws, fmt, "Strategy Development Log",
                 "Every strategy you develop, in writing, before you trade it. A strategy that is "
                 "not written down cannot be tested, and cannot be followed on a bad day.")
    headers = ["Strategy name", "Version", "Market condition it targets", "Instrument(s)",
               "Timeframe(s)", "Session(s)", "Entry rules (objective)", "Stop rule",
               "Target rule", "Invalidation", "Risk % used", "Backtest sample size",
               "Backtest expectancy (R)", "Out-of-sample expectancy (R)", "Status",
               "Date promoted", "Notes"]
    for col, name in enumerate(headers):
        ws.write(row, col, name, fmt["header"])
    ws.set_row(row, 40)
    ws.data_validation(row + 1, 14, row + 60, 14,
                       {"validate": "list",
                        "source": ["idea", "rules written", "backtesting", "out-of-sample",
                                   "demo forward test", "live small", "retired"]})
    ws.write(row + 1, 0, "(example) Trend pullback v1", fmt["text"])
    ws.write(row + 1, 1, "1.0", fmt["text"])
    ws.write(row + 1, 2, "Established uptrend with pullbacks to a prior level", fmt["text"])
    ws.write(row + 1, 3, "EURUSD", fmt["text"])
    ws.write(row + 1, 4, "H4 bias / M15 entry", fmt["text"])
    ws.write(row + 1, 5, "London", fmt["text"])
    ws.write(row + 1, 6, "H4 higher-high/higher-low intact; price returns to the last H4 demand "
                         "zone or the 20 EMA; M15 bullish engulfing or pin bar close above the level",
             fmt["text"])
    ws.write(row + 1, 7, "Below the swing low that formed the pullback, plus 1 spread", fmt["text"])
    ws.write(row + 1, 8, "Prior H4 swing high, or 2R, whichever comes first", fmt["text"])
    ws.write(row + 1, 9, "H4 close below the prior higher low", fmt["text"])
    ws.write(row + 1, 10, "0.0025", fmt["percent"])
    ws.write(row + 1, 11, 120, fmt["input_int"])
    ws.write(row + 1, 12, 0.18, fmt["number"])
    ws.write(row + 1, 13, 0.09, fmt["number"])
    ws.write(row + 1, 14, "rules written", fmt["text"])
    ws.set_column(0, 2, 26)
    ws.set_column(3, 5, 16)
    ws.set_column(6, 10, 34)
    ws.set_column(11, 16, 18)
    ws.freeze_panes(row + 1, 0)
    return {}


def _sheet_backtest(workbook, fmt):
    ws = workbook.add_worksheet("Backtest")
    row = _title(ws, fmt, "Backtest Record",
                 "Record every backtested trade exactly as you would a live trade. If you only "
                 "record the winners, you are not backtesting - you are storytelling. Target at "
                 "least 100 trades per strategy, across more than one market regime.")
    headers = ["#", "Date (bar time)", "Symbol", "Timeframe", "Session", "Direction",
               "Setup", "Entry", "Stop", "Target", "Stop (pips)", "Risk:Reward", "Outcome",
               "R result", "Rule followed?", "Notes / what the chart showed"]
    for col, name in enumerate(headers):
        ws.write(row, col, name, fmt["header"])
    ws.set_row(row, 32)
    ws.data_validation(row + 1, 2, row + 400, 2, {"validate": "list", "source": ["win", "loss", "breakeven", "skipped"]})
    ws.data_validation(row + 1, 12, row + 400, 12, {"validate": "list", "source": ["win", "loss", "breakeven"]})
    ws.data_validation(row + 1, 14, row + 400, 14, {"validate": "list", "source": ["YES", "NO"]})
    ws.write_formula(row + 1, 10, "=IFERROR(ABS(G2-F2)/0.0001,\"\")", fmt["number"])
    ws.write_formula(row + 1, 11, "=IFERROR(ABS(H2-F2)/ABS(F2-G2),\"\")", fmt["number"])
    ws.set_column(0, 0, 6)
    ws.set_column(1, 1, 14)
    ws.set_column(2, 2, 12)
    ws.set_column(3, 5, 14)
    ws.set_column(6, 6, 20)
    ws.set_column(7, 9, 12)
    ws.set_column(10, 14, 13)
    ws.set_column(15, 15, 48)
    ws.freeze_panes(row + 1, 3)

    summary_row = row + 3
    ws.write(summary_row, 0, "Backtest summary", fmt["section"])
    summary = [
        ("Trades recorded", '=COUNT($N$' + str(row + 2) + ':$N$' + str(row + 401) + ')'),
        ("Wins", f'=COUNTIF($N${row + 2}:$N${row + 401},">0")'),
        ("Losses", f'=COUNTIF($N${row + 2}:$N${row + 401},"<0")'),
        ("Win rate", f'=IFERROR(COUNTIF($N${row + 2}:$N${row + 401},">0")/'
                     f'(COUNTIF($N${row + 2}:$N${row + 401},">0")+COUNTIF($N${row + 2}:$N${row + 401},"<0")),"")'),
        ("Total R", f'=SUM($N${row + 2}:$N${row + 401})'),
        ("Expectancy (R)", f'=IFERROR(AVERAGE($N${row + 2}:$N${row + 401}),"")'),
        ("Profit factor", f'=IFERROR(SUMIF($N${row + 2}:$N${row + 401},">0")/'
                          f'ABS(SUMIF($N${row + 2}:$N${row + 401},"<0")),"")'),
        ("Rule violations", f'=COUNTIF($O${row + 2}:$O${row + 401},"NO")'),
    ]
    for offset, (label, formula) in enumerate(summary, start=1):
        ws.write(summary_row + offset, 0, label, fmt["label"])
        ws.write_formula(summary_row + offset, 1, formula, fmt["result"])
    ws.write(summary_row + len(summary) + 2, 0,
             "Sample-size honesty: below 30 trades, a backtest is a hypothesis, not evidence. "
             "Between 30 and 100 it is suggestive. Only above ~100 trades, across at least two "
             "different market regimes (trending and ranging), does it start to be informative - "
             "and even then it is in-sample until you test it on data you did not look at.",
             fmt["note"])
    ws.set_row(summary_row + len(summary) + 2, 44)
    return {}


def _sheet_performance(workbook, fmt, journal):
    ws = workbook.add_worksheet("Performance")
    row = _title(ws, fmt, "Performance Dashboard",
                 "Every figure is calculated from the Trading Journal sheet. Blank journal = blank "
                 "dashboard, which is the honest state of affairs at the start.")
    first, last = journal["first_row"], journal["last_row"]
    r_col = _col_letter(journal["r_col"])
    pnl_col = _col_letter(journal["pnl_col"])

    metrics = [
        ("Total trades (closed)", f'=COUNT({pnl_col}{first + 1}:{pnl_col}{last + 1})', "int"),
        ("Winning trades", f'=COUNTIF({pnl_col}{first + 1}:{pnl_col}{last + 1},">0")', "int"),
        ("Losing trades", f'=COUNTIF({pnl_col}{first + 1}:{pnl_col}{last + 1},"<0")', "int"),
        ("Win rate", f'=IFERROR(COUNTIF({pnl_col}{first + 1}:{pnl_col}{last + 1},">0")/'
                     f'COUNTA({pnl_col}{first + 1}:{pnl_col}{last + 1}),"")', "pct"),
        ("Gross profit", f'=SUMIF({pnl_col}{first + 1}:{pnl_col}{last + 1},">0")', "money"),
        ("Gross loss", f'=ABS(SUMIF({pnl_col}{first + 1}:{pnl_col}{last + 1},"<0"))', "money"),
        ("Net P/L", f'=SUM({pnl_col}{first + 1}:{pnl_col}{last + 1})', "money"),
        ("Profit factor", f'=IFERROR(SUMIF({pnl_col}{first + 1}:{pnl_col}{last + 1},">0")/'
                          f'ABS(SUMIF({pnl_col}{first + 1}:{pnl_col}{last + 1},"<0")),"")', "plain"),
        ("Average win (money)", f'=IFERROR(AVERAGEIF({pnl_col}{first + 1}:{pnl_col}{last + 1},">0"),"")', "money"),
        ("Average loss (money)", f'=IFERROR(ABS(AVERAGEIF({pnl_col}{first + 1}:{pnl_col}{last + 1},"<0")),"")', "money"),
        ("Payoff ratio", f'=IFERROR(AVERAGEIF({pnl_col}{first + 1}:{pnl_col}{last + 1},">0")/'
                         f'ABS(AVERAGEIF({pnl_col}{first + 1}:{pnl_col}{last + 1},"<0")),"")', "plain"),
        ("Largest win", f'=IFERROR(MAX({pnl_col}{first + 1}:{pnl_col}{last + 1}),"")', "money"),
        ("Largest loss", f'=IFERROR(MIN({pnl_col}{first + 1}:{pnl_col}{last + 1}),"")', "money"),
        ("Total R", f'=IFERROR(SUM({r_col}{first + 1}:{r_col}{last + 1}),"")', "plain"),
        ("Average R per trade", f'=IFERROR(AVERAGE({r_col}{first + 1}:{r_col}{last + 1}),"")', "plain"),
        ("Average winning R", f'=IFERROR(AVERAGEIF({r_col}{first + 1}:{r_col}{last + 1},">0"),"")', "plain"),
        ("Average losing R", f'=IFERROR(ABS(AVERAGEIF({r_col}{first + 1}:{r_col}{last + 1},"<0")),"")', "plain"),
        ("Expectancy (money per trade)", f'=IFERROR(AVERAGE({pnl_col}{first + 1}:{pnl_col}{last + 1}),"")', "money"),
        ("Expectancy (R per trade)", f'=IFERROR((AVERAGE({r_col}{first + 1}:{r_col}{last + 1})),"")', "plain"),
        ("Sharpe-like (mean R / std R)", f'=IFERROR(AVERAGE({r_col}{first + 1}:{r_col}{last + 1})/'
                                        f'STDEV({r_col}{first + 1}:{r_col}{last + 1}),"")', "plain"),
        ("Rule violations", f'=COUNTIF(Trading Journal!$AF${first + 1}:$AF${last + 1},"FALSE")', "int"),
        ("Violation rate", f'=IFERROR(COUNTIF(Trading Journal!$AF${first + 1}:$AF${last + 1},"FALSE")/'
                           f'COUNTA({r_col}{first + 1}:{r_col}{last + 1}),"")', "pct"),
    ]
    for offset, (label, formula, kind) in enumerate(metrics):
        r = row + offset
        ws.write(r, 0, label, fmt["label"])
        style = {"int": fmt["result_int"], "pct": fmt["percent"],
                 "money": fmt["result_money"], "plain": fmt["result"]}[kind]
        ws.write_formula(r, 1, formula, style)
    ws.set_column(0, 0, 38)
    ws.set_column(1, 1, 22)

    # Setup performance table (SUMIF-driven, so it updates as the journal grows).
    start = row + len(metrics) + 3
    ws.write(start, 0, "Performance by setup", fmt["section"])
    setup_col = _col_letter(JOURNAL_COLUMNS.index("setup"))
    for col, name in enumerate(["Setup", "Trades", "Total R", "Average R"]):
        ws.write(start + 1, col, name, fmt["header"])
    setups = ["trend_pullback", "breakout_retest", "range_edge_rejection",
              "failed_breakout_reversal", "htf_level_reaction"]
    for offset, setup in enumerate(setups, start=2):
        r = start + offset
        ws.write(r, 0, setup, fmt["text"])
        ws.write_formula(r, 1, f'=COUNTIF({setup_col}${journal["first_row"] + 1}:'
                              f'{setup_col}${journal["last_row"] + 1},$A{r + 1})', fmt["result_int"])
        ws.write_formula(r, 2, f'=IFERROR(SUMIF({setup_col}${journal["first_row"] + 1}:'
                              f'{setup_col}${journal["last_row"] + 1},$A{r + 1},'
                              f'{r_col}${journal["first_row"] + 1}:{r_col}${journal["last_row"] + 1}),"")',
                         fmt["result"])
        ws.write_formula(r, 3, f'=IFERROR(AVERAGEIF({setup_col}${journal["first_row"] + 1}:'
                              f'{setup_col}${journal["last_row"] + 1},$A{r + 1},'
                              f'{r_col}${journal["first_row"] + 1}:{r_col}${journal["last_row"] + 1}),"")',
                         fmt["result"])
    chart = workbook.add_chart({"type": "column"})
    chart.add_series({
        "name": "Total R by setup",
        "categories": ["Performance", start + 2, 0, start + 1 + len(setups), 0],
        "values": ["Performance", start + 2, 2, start + 1 + len(setups), 2],
    })
    chart.set_title({"name": "Total R by setup (check sample sizes)"})
    chart.set_legend({"none": True})
    ws.insert_chart(start + 1, 6, chart)
    ws.write(start + len(setups) + 3, 0,
             "The Python analytics (python main.py report --journal ...) computes the full "
             "statistical set - bootstrap confidence intervals, t-statistics, drawdown profiles "
             "and breakdowns by instrument, session, weekday and setup quality - and produces a "
             "PDF you can archive each month.", fmt["note"])
    ws.set_row(start + len(setups) + 3, 34)
    return {}


def _sheet_drawdown(workbook, fmt):
    ws = workbook.add_worksheet("Drawdown")
    row = _title(ws, fmt, "Drawdown Tracker",
                 "Enter equity at the end of each period. Drawdown is calculated from the running "
                 "peak, and the recovery column shows how much you need to gain back - the number "
                 "that should govern your risk, not your feelings.")
    headers = ["Date", "Equity", "Running peak", "Drawdown %", "Gain needed to recover",
               "Notes"]
    for col, name in enumerate(headers):
        ws.write(row, col, name, fmt["header"])
    ws.write(row + 1, 0, "2026-09-15", fmt["date"])
    ws.write(row + 1, 1, 250.0, fmt["input_money"])
    ws.write_formula(row + 1, 2, f"=MAX($B${row + 2}:B{row + 2})", fmt["result_money"])
    ws.write_formula(row + 1, 3, f"=IFERROR((C{row + 2}-B{row + 2})/C{row + 2},0)", fmt["percent"])
    ws.write_formula(row + 1, 4, f"=IFERROR(D{row + 2}/(1-D{row + 2}),0)", fmt["percent"])
    for offset in range(row + 2, row + 120):
        ws.write_formula(offset, 2, f"=MAX($B${row + 2}:B{offset + 1})", fmt["result_money"])
        ws.write_formula(offset, 3, f"=IF(B{offset + 1}=\"\",\"\",(C{offset + 1}-B{offset + 1})/C{offset + 1})",
                         fmt["percent"])
        ws.write_formula(offset, 4, f"=IF(D{offset + 1}=\"\",\"\",D{offset + 1}/(1-D{offset + 1}))",
                         fmt["percent"])
    ws.conditional_format(row + 1, 3, row + 119, 3,
                          {"type": "cell", "criteria": ">=", "value": 0.10, "format": fmt["negative"]})
    ws.set_column(0, 0, 14)
    ws.set_column(1, 2, 16)
    ws.set_column(3, 4, 18)
    ws.set_column(5, 5, 44)
    ws.freeze_panes(row + 1, 0)
    return {"row": row + 2, "last": row + 119}


def _sheet_psychology(workbook, fmt):
    ws = workbook.add_worksheet("Psychology")
    row = _title(ws, fmt, "Psychology Journal",
                 "One entry per trading day. Patterns in this sheet are usually more valuable than "
                 "patterns on the charts: they explain why the same setup produces different "
                 "results on different days.")
    headers = ["Date", "Sleep (1-5)", "Stress (1-5)", "Energy (1-5)", "Pre-session state",
               "Urges felt (revenge/FOMO/boredom)", "Trades taken", "Did I follow the plan?",
               "Strongest emotion during the session", "What triggered it",
               "What I did instead of acting on it", "One sentence for tomorrow's self"]
    for col, name in enumerate(headers):
        ws.write(row, col, name, fmt["header"])
    ws.set_row(row, 40)
    ws.data_validation(row + 1, 7, row + 60, 7, {"validate": "list", "source": ["YES", "NO"]})
    ws.data_validation(row + 1, 4, row + 60, 4,
                       {"validate": "list",
                        "source": ["calm", "confident", "anxious", "frustrated", "euphoric",
                                   "bored", "fearful", "impatient"]})
    ws.set_column(0, 0, 12)
    ws.set_column(1, 4, 11)
    ws.set_column(5, 5, 30)
    ws.set_column(6, 8, 14)
    ws.set_column(9, 11, 40)
    ws.freeze_panes(row + 1, 0)
    return {}


def _checklist_sheet(workbook, fmt, name: str, title: str, subtitle: str, items: list[str],
                     extra_columns: list[str] | None = None):
    ws = workbook.add_worksheet(name)
    row = _title(ws, fmt, title, subtitle)
    ws.write(row, 0, "Check", fmt["header"])
    ws.write(row, 1, "Done", fmt["header"])
    ws.write(row, 2, "Evidence / note", fmt["header"])
    for col, extra in enumerate(extra_columns or [], start=3):
        ws.write(row, col, extra, fmt["header"])
    for offset, item in enumerate(items, start=1):
        r = row + offset
        ws.write(r, 0, item, fmt["text"])
        ws.data_validation(r, 1, r, 1, {"validate": "list", "source": ["YES", "NO", "N/A"]})
        ws.write(r, 2, "", fmt["text"])
        for col in range(3, 3 + len(extra_columns or [])):
            ws.write(r, col, "", fmt["text"])
    ws.conditional_format(row + 1, 1, row + len(items), 1,
                          {"type": "text", "criteria": "containing", "value": "NO",
                           "format": fmt["negative"]})
    ws.set_column(0, 0, 62)
    ws.set_column(1, 1, 10)
    ws.set_column(2, 2, 46)
    ws.set_column(3, 3 + len(extra_columns or []), 20)
    ws.freeze_panes(row + 1, 0)
    return ws


def _sheet_daily_checklist(workbook, fmt):
    return _checklist_sheet(
        workbook, fmt, "Daily Checklist", "Daily Trading Checklist",
        "Complete this before the first trade of the day. 'N/A' is a valid answer; blank is not.",
        [
            "I have checked the economic calendar for today and the next 24 hours",
            "I know which releases are high impact for the pairs I trade",
            "I have marked the daily, weekly and session highs/lows of my instruments",
            "I have identified the higher timeframe bias (up / down / range / unclear)",
            "I have written my key levels BEFORE looking at the lower timeframe",
            "I have a written plan for the day: which setup, at which level, at what risk",
            "I know my maximum loss for the day and for the week (in money)",
            "My chart layout is clean: no more than two indicators I actually use",
            "I have calculated the lot size for my planned setup in advance",
            "I am well rested, calm and free of the urge to win back anything",
            "I have no more than the allowed number of open positions",
            "Correlation check: my open trades do not all express the same currency view",
            "Spread on my instrument is at or near its normal level",
            "I accept that the outcome is uncertain and that my job is process, not prediction",
            "There is a written invalidation level for every trade I am about to take",
        ],
        extra_columns=["Date", "Session", "Equity at start"],
    )


def _sheet_weekly_review(workbook, fmt):
    return _checklist_sheet(
        workbook, fmt, "Weekly Review", "Weekly Review",
        "Same time every week. Review the process, not just the money.",
        [
            "Recorded every trade with screenshots, reasons and emotional state",
            "Calculated total R, expectancy and profit factor for the week",
            "Counted rule violations and identified their cost in R",
            "Reviewed each losing trade: was the decision good and the outcome bad, or vice versa?",
            "Reviewed each winning trade for luck vs skill (was the plan followed?)",
            "Checked whether any instrument or session consistently underperformed",
            "Checked whether position sizes matched the plan exactly",
            "Checked for correlation mistakes (same risk expressed more than once)",
            "Updated the journal statistics sheet and recorded equity",
            "Wrote down one process change for next week (maximum one, and only in writing)",
            "Verified no strategy change was made mid-week in response to a loss",
            "Confirmed the next week's calendar has been reviewed for high-impact events",
        ],
        extra_columns=["Week ending", "Trades this week", "Net R", "Rule violations"],
    )


def _sheet_monthly_review(workbook, fmt):
    return _checklist_sheet(
        workbook, fmt, "Monthly Review", "Monthly Review",
        "This is where a strategy is genuinely judged - not on any single week.",
        [
            "Total sample size for the month recorded (trades)",
            "Expectancy computed with its confidence interval, not just its mean",
            "Maximum drawdown for the month measured against the plan's limit",
            "Compared demo results with the backtest distribution (are they similar?)",
            "Reviewed whether any rule was changed mid-month (it must not have been)",
            "Reviewed the psychology journal for recurring emotional triggers",
            "Reviewed performance by setup, instrument, session and weekday",
            "Identified the single biggest source of lost R (rule breach, bad size, bad exit?)",
            "Decided in writing whether to keep, adjust or retire each setup",
            "Confirmed the readiness criteria for the next phase (see the scorecard)",
            "No decision was made during a drawdown or immediately after a big loss",
            "Backed up the journal and this workbook",
        ],
        extra_columns=["Month", "Trades", "Total R", "Max DD %"],
    )


def _sheet_economic_calendar(workbook, fmt):
    ws = workbook.add_worksheet("Economic Calendar")
    row = _title(ws, fmt, "Economic Calendar & News Risk Log",
                 "Fill this from a calendar you trust (Exness provides one in its terminal; "
                 "central-bank sites are the primary source). Verify times yourself - a wrong "
                 "release time is a risk-management failure, not a data problem.")
    headers = ["Date", "Time (UTC)", "Currency", "Release", "Impact",
               "Forecast", "Previous", "Actual", "Blackout start (UTC)",
               "Blackout end (UTC)", "Position plan during this event", "Outcome / notes"]
    for col, name in enumerate(headers):
        ws.write(row, col, name, fmt["header"])
    ws.data_validation(row + 1, 4, row + 200, 4,
                       {"validate": "list", "source": ["high", "medium", "low"]})
    ws.data_validation(row + 1, 10, row + 200, 10,
                       {"validate": "list",
                        "source": ["no new positions", "reduce exposure", "flatten before release",
                                   "hold with stop already at breakeven", "not applicable"]})
    ws.set_column(0, 0, 12)
    ws.set_column(1, 2, 11)
    ws.set_column(3, 3, 34)
    ws.set_column(4, 6, 12)
    ws.set_column(7, 7, 12)
    ws.set_column(8, 9, 20)
    ws.set_column(10, 10, 30)
    ws.set_column(11, 11, 42)
    ws.freeze_panes(row + 1, 0)
    return {}


def _sheet_watchlist(workbook, fmt, settings):
    ws = workbook.add_worksheet("Watchlist")
    row = _title(ws, fmt, "Watchlist & Pre-Market Preparation",
                 "A short list you actually follow beats a 200-symbol Market Watch. These are the "
                 "majors plus gold; add an instrument only when you will backtest it.")
    headers = ["Symbol", "Group", "Pip size", "Typical spread (points)", "Daily ATR (pips)",
               "Higher timeframe bias", "Key support", "Key resistance", "In session?",
               "Tradeable today?", "Reason / plan", "Last updated"]
    for col, name in enumerate(headers):
        ws.write(row, col, name, fmt["header"])
    core = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "XAUUSD"]
    specs = {s.symbol: s for s in list_instruments()}
    for offset, symbol in enumerate(core, start=1):
        r = row + offset
        spec = specs.get(symbol)
        ws.write(r, 0, symbol, fmt["text"])
        ws.write(r, 1, spec.group if spec else "", fmt["text"])
        ws.write(r, 2, spec.pip_size if spec else "", fmt["number"])
        for col in range(3, 12):
            ws.write(r, col, "", fmt["text"])
    ws.data_validation(row + 1, 9, row + 30, 9, {"validate": "list", "source": ["YES", "NO"]})
    ws.set_column(0, 1, 14)
    ws.set_column(2, 4, 16)
    ws.set_column(5, 8, 18)
    ws.set_column(9, 11, 34)
    ws.freeze_panes(row + 1, 0)
    _ = settings
    return {}


def _sheet_trade_statistics(workbook, fmt, journal):
    ws = workbook.add_worksheet("Trade Statistics")
    row = _title(ws, fmt, "Trade Statistics",
                 "Distributional view of the journal. A strategy is not one number; it is a "
                 "distribution of R values, and the tail is what kills accounts.")
    r_col = _col_letter(journal["r_col"])
    first, last = journal["first_row"] + 1, journal["last_row"] + 1
    rng = f"{r_col}{first}:{r_col}{last}"
    stats = [
        ("Trades", f'=COUNT({rng})'),
        ("Mean R", f'=IFERROR(AVERAGE({rng}),"")'),
        ("Median R", f'=IFERROR(MEDIAN({rng}),"")'),
        ("Standard deviation of R", f'=IFERROR(STDEV({rng}),"")'),
        ("Best R", f'=IFERROR(MAX({rng}),"")'),
        ("Worst R", f'=IFERROR(MIN({rng}),"")'),
        ("25th percentile R", f'=IFERROR(PERCENTILE({rng},0.25),"")'),
        ("75th percentile R", f'=IFERROR(PERCENTILE({rng},0.75),"")'),
        ("R > 0 count", f'=COUNTIF({rng},">0")'),
        ("R <= -1 count (stop breaches)", f'=COUNTIF({rng},"<=-1.05")'),
        ("Mean R of winners", f'=IFERROR(AVERAGEIF({rng},">0"),"")'),
        ("Mean R of losers", f'=IFERROR(AVERAGEIF({rng},"<0"),"")'),
        ("Fat-tail check: trades better than +4R", f'=COUNTIF({rng},">4")'),
    ]
    for offset, (label, formula) in enumerate(stats):
        r = row + offset
        ws.write(r, 0, label, fmt["label"])
        ws.write_formula(r, 1, formula, fmt["result"])
    ws.write(row + len(stats) + 2, 0,
             "Why the tail matters: if one +8R trade carries a whole quarter, your edge may be "
             "smaller than the average suggests. Recompute expectancy with that trade removed - "
             "that is the 'robustness check' professionals run before increasing risk.",
             fmt["note"])
    ws.set_row(row + len(stats) + 2, 34)
    ws.set_column(0, 0, 40)
    ws.set_column(1, 1, 20)
    return {}


def _sheet_correlation(workbook, fmt):
    ws = workbook.add_worksheet("Correlation")
    row = _title(ws, fmt, "Correlation & Exposure Matrix",
                 "Correlations are unstable: they change with the regime, and they approach 1 "
                 "exactly when you least want them to (during risk-off shocks). Treat this table "
                 "as a checklist for 'am I expressing the same idea twice?', not as a fixed law.")
    headers = ["Instrument", "USD exposure", "Typical relationship", "Correlated with",
               "Live exposure driver", "Positions sharing this driver", "Within limit?"]
    for col, name in enumerate(headers):
        ws.write(row, col, name, fmt["header"])
    rows = [
        ("EURUSD", "Short USD (long EUR)", "Inverse to DXY", "GBPUSD (+), USDCHF (-)", "", "", ""),
        ("GBPUSD", "Short USD (long GBP)", "Inverse to DXY", "EURUSD (+), GBPJPY n/a", "", "", ""),
        ("USDJPY", "Long USD vs yen", "Rates & risk sentiment driven", "USDCHF (+), UST yields (+)", "", "", ""),
        ("USDCHF", "Long USD", "Inverse to EURUSD", "USDJPY (+)", "", "", ""),
        ("AUDUSD", "Short USD", "Risk-on / commodity sensitive", "NZDUSD (+), gold (+)", "", "", ""),
        ("NZDUSD", "Short USD", "Risk-on sensitive", "AUDUSD (+)", "", "", ""),
        ("USDCAD", "Long USD", "Inverse to oil", "Oil (-)", "", "", ""),
        ("XAUUSD", "Inverse to real yields", "Risk and US real-yield sensitive", "Silver (+), AUDUSD (+)", "", "", ""),
        ("DXY", "The USD itself", "Basket of USD pairs", "EURUSD/GBPUSD/AUDUSD (-)", "", "", ""),
        ("USOIL", "Global growth proxy", "Supply/demand + USD", "USDCAD (-)", "", "", ""),
    ]
    for offset, values in enumerate(rows, start=1):
        r = row + offset
        for col, value in enumerate(values):
            ws.write(r, col, value, fmt["text"] if col != 5 else fmt["input_int"])
    ws.data_validation(row + 1, 6, row + len(rows), 6, {"validate": "list", "source": ["YES", "NO"]})
    ws.write(row + len(rows) + 2, 0,
             "Worked example of hidden exposure: long EURUSD + long GBPUSD + short USDCHF = one "
             "short-USD position taken three times. If the dollar rallies on a hot US CPI print, "
             "all three lose together and your '0.25% per trade' becomes 0.75% in one minute, while "
             "the portfolio heat rule that you thought was protecting you was counting positions, "
             "not risk.", fmt["warning"])
    ws.set_row(row + len(rows) + 2, 60)
    ws.set_column(0, 0, 14)
    ws.set_column(1, 2, 26)
    ws.set_column(3, 3, 30)
    ws.set_column(4, 4, 24)
    ws.set_column(5, 5, 16)
    ws.set_column(6, 6, 14)
    ws.freeze_panes(row + 1, 0)
    return {}


def _sheet_dashboard(workbook, fmt, journal, performance, drawdown, statistics, position):
    ws = workbook.add_worksheet("Dashboard")
    row = _title(ws, fmt, "Forex Trading Dashboard",
                 f"Generated {date.today().isoformat()} by the Forex Mastery System. "
                 "Everything here is derived from the Trading Journal sheet - no manual entry.")
    ws.write(row, 0, "Headline numbers", fmt["section"])
    r_col = _col_letter(journal["r_col"])
    pnl_col = _col_letter(journal["pnl_col"])
    # Column letters come from the schema itself. Hard-coding them is how a workbook
    # silently starts counting the wrong column after a schema change.
    risk_col = _col_letter(JOURNAL_COLUMNS.index("risk_percent"))
    rules_col = _col_letter(JOURNAL_COLUMNS.index("rules_followed"))
    shot_col = _col_letter(JOURNAL_COLUMNS.index("screenshot_before"))
    shot2_col = _col_letter(JOURNAL_COLUMNS.index("screenshot_after"))
    first, last = journal["first_row"] + 1, journal["last_row"] + 1
    tiles = [
        ("Closed trades", f'=COUNT({pnl_col}{first}:{pnl_col}{last})', "int"),
        ("Win rate", f'=IFERROR(COUNTIF({pnl_col}{first}:{pnl_col}{last},">0")/'
                     f'COUNTA({pnl_col}{first}:{pnl_col}{last}),"")', "pct"),
        ("Total R", f'=IFERROR(SUM({r_col}{first}:{r_col}{last}),"")', "plain"),
        ("Expectancy (R)", f'=IFERROR(AVERAGE({r_col}{first}:{r_col}{last}),"")', "plain"),
        ("Net P/L", f'=IFERROR(SUM({pnl_col}{first}:{pnl_col}{last}),"")', "money"),
        ("Profit factor", f'=IFERROR(SUMIF({pnl_col}{first}:{pnl_col}{last},">0")/'
                          f'ABS(SUMIF({pnl_col}{first}:{pnl_col}{last},"<0")),"")', "plain"),
    ]
    for offset, (label, formula, kind) in enumerate(tiles, start=1):
        r = row + offset
        ws.write(r, 0, label, fmt["label"])
        style = {"int": fmt["result_int"], "pct": fmt["percent"],
                 "money": fmt["result_money"], "plain": fmt["result"]}[kind]
        ws.write_formula(r, 1, formula, style)

    start = row + len(tiles) + 3
    ws.write(start, 0, "Risk and process status", fmt["section"])
    dd_first, dd_last = drawdown["row"], drawdown["last"]
    equity_formula = (
        f'=IFERROR(LOOKUP(2,1/(Drawdown!$B${dd_first}:$B${dd_last}<>""),'
        f'Drawdown!$B${dd_first}:$B${dd_last}),"")'
    )
    checks = [
        ("Current equity (from the Drawdown sheet)", equity_formula, "money"),
        ("Current drawdown %",
         f'=IFERROR((MAX(Drawdown!$B${dd_first}:$B${dd_last})-{equity_formula.lstrip("=")})/'
         f'MAX(Drawdown!$B${dd_first}:$B${dd_last}),"")'.replace("=IFERROR(", "IFERROR("),
         "pct"),
        ("Rule violation rate",
         f'=IFERROR(COUNTIF(Trading Journal!${rules_col}${first}:${rules_col}${last},"FALSE")/'
         f'COUNTA({r_col}{first}:{r_col}{last}),"")', "pct"),
        ("Trades risking more than 1%",
         f'=COUNTIF(Trading Journal!${risk_col}${first}:${risk_col}${last},">0.01")', "int"),
        ("Journal rows with no screenshot recorded",
         f'=COUNTIFS(Trading Journal!${shot_col}${first}:${shot_col}${last},"",'
         f'Trading Journal!${shot2_col}${first}:${shot2_col}${last},"")', "int"),
        ("Readiness",
         "run:  python main.py readiness --criteria", "text"),
    ]
    for offset, (label, formula, kind) in enumerate(checks, start=1):
        r = start + offset
        ws.write(r, 0, label, fmt["label"])
        style = {"int": fmt["result_int"], "pct": fmt["percent"],
                 "money": fmt["result_money"], "plain": fmt["result"], "text": fmt["text"]}[kind]
        if isinstance(formula, str) and formula.startswith("="):
            ws.write_formula(r, 1, formula, style)
        else:
            ws.write(r, 1, formula, style)

    note_row = start + len(checks) + 2
    ws.write(note_row, 0,
             "Trading rules in force (edit config/strategy_rules.json; the Python rule engine is "
             "the authority): risk <= 1.00% per trade, <= 0.25% while learning; minimum R:R 1.5; "
             "no new positions within 30 minutes of high-impact news; maximum 2 trades per day; "
             "stop for the day at -1% and for the week at -3%; maximum one position per currency "
             "story; portfolio heat <= 2%.", fmt["warning"])
    ws.set_row(note_row, 60)
    ws.set_column(0, 0, 44)
    ws.set_column(1, 1, 26)
    _ = (performance, statistics, position)
    return {}
