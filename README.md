# Forex Trading Mastery System

A complete, self-contained learning and tooling system for going from **absolute beginner** to
**competent, disciplined trader** — on Exness / MetaTrader 4 and 5, working toward a small live
account (**USD 250**) after a long demo phase.

> **Read this first.** Nothing in this repository predicts the market, guarantees a profit, or tells
> you to buy or sell. The system teaches a process and provides the arithmetic, the records and the
> audits that let *you* evaluate your own decisions. Most retail traders lose money. The honest
> objective of this project is to make you a good decision-maker who risks small amounts correctly —
> not to make you rich.

---

## 1. What is in the box

| Layer | What it does | Where it lives |
|---|---|---|
| **Curriculum** | Levels 0–28, from "what is a pip" to professional review loops | `docs/01_CURRICULUM.md`, `docs/handbooks/`, `notebooks/` |
| **Calculation engine** | pip value, position size, margin, R:R, expectancy, drawdown, risk of ruin, compounding, sessions, rule engine | `forex_mastery/core/` |
| **Journal** | 39-field trade record, atomic CSV storage, derived R-multiples | `forex_mastery/journal/` |
| **Analytics** | performance statistics from your own journal, with confidence intervals and honest sample-size warnings | `forex_mastery/analytics/` |
| **Reports** | Markdown → PDF / DOCX handbooks, 20-sheet Excel workbook, charts, CSV breakdowns | `forex_mastery/reports/` |
| **Training programme** | 90-day / 13-week / 10-phase demo programme with gates, mastery scorecard, readiness criteria | `forex_mastery/program/` |
| **Quiz bank** | 60+ questions across 10 categories, answers hidden until you commit | `data/questions/`, `forex_mastery/quiz/` |
| **Broker conditions** | account types, margin call / stop-out levels, higher-margin-requirement windows, trading-volume definition (dated, sourced) | `config/broker.json`, `forex_mastery/core/broker.py` |
| **Candle measurement** | 13 mechanical pattern definitions + forward statistics with baseline comparison and sample-size caveats (runs on data *you* supply) | `forex_mastery/core/candles.py` |
| **CLI** | every tool as one command | `main.py` |

## 2. Install and first run

```bash
# 1. (recommended) a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. core needs NOTHING - it is standard library only
python main.py doctor

# 3. optional extras, only if you want the matching feature
pip install -r requirements.txt    # pandas, matplotlib, XlsxWriter, reportlab, jupyterlab ...
```

```bash
python main.py --help                       # every command
python main.py specs --symbol XAUUSD        # instrument specification + notes
python main.py broker --hmr                 # account types, stop-out levels, HMR windows
python main.py candles --rules              # objective candle-shape definitions
python main.py candles --file data/raw/EURUSD_X_1d.csv --pattern bullish_pin  # honest stats
python main.py pip --symbol USDJPY --price USDJPY=150.0
python main.py position --symbol EURUSD --balance 250 --risk 0.25 \
    --entry 1.1000 --stop 1.0950 --take-profit 1.1100 --leverage 100
python main.py scenarios --symbol EURUSD --balance 250 --entry 1.1000 --stop 1.0950
python main.py drawdown --balance 250
python main.py ruin --win-rate 0.45 --rr 1.5 --risk 0.25 --trades 300
python main.py sessions --tz Asia/Kolkata --explain
python main.py journal new && python main.py journal add --symbol EURUSD --direction long \
    --entry 1.1 --stop 1.095 --lots 0.01 --equity 250 --risk 0.25
python main.py report --charts --pdf --json
python main.py quiz --category risk_management --n 10 --interactive
python main.py demo --list                  # the 90-day programme
python main.py progress                     # mastery scorecard
python main.py readiness --criteria         # live-account readiness
python main.py lesson --number 1            # the lessons
python main.py build all                    # Excel + PDF + DOCX + notebooks + templates
```

In VS Code: open the folder, select the interpreter, and use **Terminal → Run Task** or simply run
`python main.py ...`. `main.py` adds the project root to `sys.path`, so nothing needs installing.

## 3. Non-negotiable design rules

1. **Never invent market data.** If a price is required to convert a pip value, the code asks for it
   (`MissingRateError`) instead of assuming 1.0. Wrong arithmetic is worse than no arithmetic.
2. **Trading rules are configuration, not code.** `config/strategy_rules.json` drives the rule
   engine; the engine is the authority, the spreadsheet is a convenience.
3. **Unknown input = unverified = not satisfied.** If a blocking check has no data, the verdict is
   NO TRADE. Optimism is not evidence.
4. **No guarantees, ever.** Expectancy, drawdown and risk of ruin are estimates with confidence
   intervals; the reports say so on every page.
5. **Small sample, weak claim.** Below 30 trades the analytics call the result a hypothesis, not an
   edge.
6. **Capital preservation first.** 0.10–0.25% risk per trade while learning, hard cap 1%, and the
   drawdown ladder is calculated rather than imagined.
7. **Prohibited practices** (martingale, grid-as-guarantee, averaging down without predefined risk,
   revenge trading, unlimited leverage, chasing signals, "100% win rate" systems) are named and
   explained wherever they would otherwise seem attractive.

## 4. Honesty about what is verified

Broker-specific facts in `config/instruments.json` were checked against **official Exness
documentation on 2026-09-15** and carry per-instrument `verified` flags. Anything unverified says so
in the CLI (`python main.py specs`) and inside the data file. Session times are derived from IANA
time zones, so daylight-saving changes are handled by the timezone database rather than by hand.
**Always confirm in MT5 → Market Watch → right-click → Specification** before sizing a trade; the
broker's current contract specification overrides anything stored here.

## 5. Layout

```
config/          instruments, broker conditions, strategy rules, risk profile
data/            journal CSVs (git-ignored), question bank
docs/            00_MASTER_ROADMAP.md, 01_CURRICULUM.md, lessons/, handbooks/
forex_mastery/   core/ journal/ analytics/ reports/ program/ quiz/ cli.py
notebooks/       20-lesson Jupyter curriculum (generated)
outputs/         generated reports (git-ignored)
tests/           190+ unit tests: every calculation has a known-answer test
tools/           helper scripts (e.g. synthetic journal generator)
```

## 6. Tests

```bash
python -m pytest -q                        # all tests
python -m pytest --doctest-modules forex_mastery/core forex_mastery/journal
```

The suite pins the arithmetic with known answers (pip values, sizing, R-multiples, expectancy,
drawdown, streak probabilities, risk of ruin, session windows, rule verdicts) and asserts that
docstrings example values still hold.

## 7. Licence and responsibility

Use it, modify it, learn from it. You are responsible for every trade you place: not this software,
not a broker, not a course, not a signal group.
