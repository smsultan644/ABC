# MASTER ROADMAP AND SYSTEM ARCHITECTURE

**Project:** Forex Trading Mastery System
**Trader profile assumed:** complete beginner, Exness account (MT4/MT5), eventual live capital
**USD 250**, long demo phase first
**Primary objective:** capital preservation and decision-making quality
**Secondary objective:** profitability — accepted as an *outcome*, never as a promise
**Document version:** 2026-09-15

---

## PART A — Executive summary

This system is built on four claims, each of which is either true or falsifiable, and none of which
is a prediction:

1. **A retail trader's main risk is not the market; it is position size and self-management.**
   Therefore, the first tool built is a position-size calculator, and the first skill mastered is
   risking a small, fixed, pre-decided amount.
2. **Without records there is no learning.** Every trade is journalled in a fixed schema so that
   statistics — not memory, not mood — drive decisions about what to keep, change or drop.
3. **Judgements need to be calibrated, not asserted.** Every decision is sorted into FACT,
   INTERPRETATION, SCENARIO or SPECULATION, and into KNOWLEDGE, ANALYSIS, STRATEGY, SIGNAL, RISK
   MANAGEMENT, EXECUTION or PERFORMANCE — so ideas cannot masquerade as evidence.
4. **Progress must be gated, not felt.** Ten phases with objective gates decide when the next stage
   begins. A failed gate means repeat the phase; it does not mean "try harder with real money".

What you get: 28 curriculum levels, 20 notebook lessons, 18 handbook chapters, a tested calculation
engine, a journal, an analytics suite, PDF/Excel reports, a question bank, a 90-day demo programme, a
mastery scorecard and a strict readiness assessment for a live account.

What you do not get: signals, predictions, guarantees, or a way to skip the risk-management
requirement. There is no such way.

---

## PART B — Architecture

### B.1 Layer diagram

```
                        ┌──────────────────────────────────────────────┐
   YOU (decisions)      │  1. CURRICULUM      docs/, notebooks/, quiz   │
                        │  2. RISK FRAMEWORK  config/risk_profile.json  │
                        │  3. TRADING PLAN    docs/handbooks/12_*.md    │
                        └───────────────────────┬──────────────────────┘
                                                │ rules, thresholds
                        ┌───────────────────────▼──────────────────────┐
   CALCULATION (math)   │  forex_mastery/core/                         │
                        │  instruments · pip · margin · position_size   │
                        │  risk · metrics · risk_of_ruin · compounding  │
                        │  sessions · rule_engine · validation          │
                        │  (standard library only, unit-tested)         │
                        └───────────────────────┬──────────────────────┘
                                                │ sizes, verdicts, stats
                        ┌───────────────────────▼──────────────────────┐
   RECORD (evidence)    │  forex_mastery/journal/  (39-column schema)   │
                        │  data/journal/journal.csv  ·  atomic writes   │
                        └───────────────────────┬──────────────────────┘
                                                │ closed trades
                        ┌───────────────────────▼──────────────────────┐
   ANALYSIS (evidence)  │  forex_mastery/analytics/  performance, charts│
                        │  reports/ excel_workbook, pdf_docs, docx,     │
                        │  markdown_renderer, library, templates        │
                        └───────────────────────┬──────────────────────┘
                                                │ scorecards, gates
                        ┌───────────────────────▼──────────────────────┐
   PROGRESSION (gates)  │  forex_mastery/program/  90-day programme,    │
                        │  mastery scorecard, readiness criteria        │
                        └───────────────────────┬──────────────────────┘
                                                │
                        ┌───────────────────────▼──────────────────────┐
   INTERFACE            │  main.py → forex_mastery/cli.py (one command │
                        │  per tool, VS Code friendly, no install)      │
                        └──────────────────────────────────────────────┘
```

### B.2 Why the layers are separated

* **Calculation is pure and testable.** `core/` has no I/O, no network calls and no hidden state, so
  every number can be pinned by a unit test. A trading tool that is 99% right about risk is a
  liability.
* **Rules live in configuration.** `config/strategy_rules.json` and `config/risk_profile.json` are
  data. Changing your rule set does not mean editing Python, and the rule engine's verdicts are
  reproducible from those files.
* **Evidence is separated from opinion.** The journal stores what happened; analytics derive
  statistics; reports present them with uncertainty. Nothing in the analysis layer knows your
  feelings about a pair.
* **Progression is explicit.** Gates in `program/` turn "I think I'm ready" into a checklist that
  fails loudly.
* **Markdown is the source of truth for documents.** PDF and DOCX are rendered from the same text, so
  the printed handbook and the repository can never disagree.

### B.3 Data flow of a single trade

```
idea → rule_engine.evaluate_setup(config)  →  APPROVED / WITH WARNINGS / NO TRADE
     → position_size.calculate_position_size()  →  lots (rounded DOWN), R, costs, margin
     → journal.add(TradeRecord)                 →  evidence, screenshots, invalidation
     → journal.close_trade(...)                 →  P/L, derived R-multiple
     → analytics.analyse_journal()              →  statistics with confidence intervals
     → reports (PDF/Excel/CSV/PNG)              →  monthly review material
     → program gates + readiness criteria       →  decision about the next phase
```

---

## PART C — The 28 curriculum levels

The levels are grouped into seven stages. Full detail: `docs/01_CURRICULUM.md`.

| Stage | Levels | Theme | Gate to pass |
|---|---|---|---|
| 0. Foundations | 0–3 | What FX is, market mechanics, broker and platform, vocabulary | Explain bid/ask, pip, lot, margin, leverage, stop-out and spread in your own words; correct numbers in a sizing exercise |
| 1. Chart literacy | 4–8 | Candles, structure, levels, indicators, timeframes, sessions | Classify 20 charts (trend/range/transition) and place levels with reasons |
| 2. Analysis | 9–14 | Macro, central banks, news, correlation, price-action reading, order-flow vocabulary | Write a one-page macro note and a structured pre-trade analysis for one pair |
| 3. Risk & money | 15–18 | Position sizing, R-multiples, expectancy, drawdown, ruin, psychology of loss | Size 10 trades across 4 instruments by hand and with the calculator; pass the risk exam |
| 4. Strategy & testing | 19–23 | Setup specification, edge, backtesting, statistics, validation biases | 100-trade backtest with costs, out-of-sample check, written strategy spec |
| 5. Execution & psychology | 24–28 | Routine, journaling discipline, error taxonomy, performance review, adaptation | 90-day demo programme with 100+ journalled trades and gate passes |
| 6. Live readiness | (post-programme) | Readiness criteria, small live start, scaling rules, ongoing review | 14 hard readiness criteria satisfied |

---

## PART D — The 12-phase build order

The project is built in this order. Each phase produces something usable on its own, and nothing
later is allowed to jump ahead of risk management.

| Phase | Deliverable | Status in this repository |
|---|---|---|
| 1 | Curriculum, handbook chapters, notebook lessons, quiz bank | Curriculum map + Lesson 1 written; handbook chapters in progress; 20 notebooks generated; 60-question bank |
| 2 | Risk framework: risk profile, sizing, drawdown ladder, ruin simulation | **Complete** — `config/risk_profile.json`, `core/risk.py`, `core/risk_of_ruin.py`, `core/compounding.py` |
| 3 | Journal | **Complete** — 39-field schema, atomic CSV store, JSON import/export |
| 4 | Calculators | **Complete** — pip, margin, position size, R:R, scenarios + CLI |
| 5 | Trading plan | Template + guide written; your own plan is authored by you |
| 6 | Backtesting | Methodology chapter, cost model, seven-stage validation gate; manual-first by design |
| 7 | Performance dashboard | **Complete** — `analytics/`, charts, CSV breakdowns, 20-sheet Excel workbook, PDF report |
| 8 | Educational documents | `reports/library.py` + renderers; chapters are being written in curriculum order |
| 9 | Notebooks | **Complete** — generator produces 20 notebooks with runnable cells |
| 10 | Decision training | Structured analysis template + decision workbooks + 60-question bank |
| 11 | 90-day demo programme | **Complete** — 13 weeks, 10 phases, gates, progress tracking |
| 12 | Mastery assessment | **Complete** — weighted scorecard + 16 readiness criteria (14 hard) |

---

## PART E — The decision framework used everywhere

Every statement you make about the market is tagged:

| Tag | Meaning | Example |
|---|---|---|
| **FACT** | Verifiable, sourced, timestamped | "The ECB deposit rate is X% as of <date>, per the ECB." |
| **INTERPRETATION** | A reading of facts, which can be wrong | "Rate-cut expectations are being priced out, so EUR is supported." |
| **SCENARIO** | A conditional future | "If H4 closes above 1.1050 and holds, the next reference is 1.1120." |
| **SPECULATION** | No defensible basis; entertainment | "Gold will hit 3000 next week." |

And every activity you perform is classified as **KNOWLEDGE** (learning), **ANALYSIS** (structured
reading of conditions), **STRATEGY** (a tested, written rule set), **SIGNAL** (someone else's
opinion — treat with suspicion), **RISK MANAGEMENT** (deciding and enforcing size), **EXECUTION**
(placing and managing orders) or **PERFORMANCE** (measuring outcomes). Confusing these categories is
the most common beginner error: a signal is not analysis, and analysis is not a strategy.

---

## PART F — The rules that define "competent" here

These are enforced numerically, not aspirationally:

* Risk per trade: **0.10% → 0.25%** while learning; hard cap **1.00%**.
* Minimum reward:risk **1.5** (below 1:1 the required win rate becomes unrealistic).
* Maximum **2 trades per day**; stop for the day at **−1%**, for the week at **−3%**.
* Maximum **one position per currency story**; total portfolio heat **≤ 2%**.
* No new positions within **30 minutes before** or **15 minutes after** high-impact news.
* Trade only **London, New York, or the overlap** while learning; avoid the 21:00–24:00 UTC lull.
* A trade requires: written setup name, entry trigger, stop with a structural reason, target, risk %,
  invalidation condition, correlation check, and a psychological self-check.
* **Unknown = not satisfied.** Missing data blocks the trade.
* Prohibited: martingale, grid-as-guarantee, doubling after losses, averaging down without predefined
  risk, unlimited leverage, revenge trading, overtrading, signal chasing, "100% win rate" systems.

---

## PART G — The 13 strategy families (taught as frameworks, not signals)

Trend continuation · Pullback in trend · Break-of-structure continuation · Range reversal ·
Range breakout with retest · Failed breakout (trap) · Momentum expansion · Mean reversion to
reference · Session-open behaviour · News reaction vs news fade · Weekly-level reaction ·
Correlation divergence · Volatility compression expansion.

Each is taught with: market condition required, entry trigger, stop placement rationale, target
logic, expected trade frequency, known failure modes, and the statistics it must show before being
trusted. Full detail: `docs/handbooks/08_strategies.md`.

---

## PART H — Milestones and how you know you are on track

| Milestone | Evidence | Typical time |
|---|---|---|
| M0 — Mechanics understood | Pass the Level 0–3 quiz (≥ 80%) and 5 hand calculations | 1 week |
| M1 — Reads a chart | 20 charts classified blind, level maps with reasons | 2–4 weeks |
| M2 — Risk automation | 10 hand-sized trades, all correct; ruin and drawdown questions answered | 1 week (mandatory) |
| M3 — Strategy written | One setup specified so precisely a stranger could execute it | 1 week |
| M4 — Backtested | 100 trades with costs, out-of-sample check, distribution reviewed | 2–4 weeks |
| M5 — Demo forward test | 100+ journalled demo trades, gate passes, expectancy computed | 6–9 weeks |
| M6 — Readiness | 14 hard criteria satisfied; 250 USD is disposable | 1–2 weeks |
| M7 — Live, small | First 20 live trades at 0.10% risk, no rule violations | ongoing |
| M8 — Review loop | Monthly reports, one change at a time, documented decisions | ongoing |

---

## PART I — Success and failure, defined honestly

**Success is not a profit target.** Success is: you risk a pre-decided small amount each time, your
records are complete, your rule violations approach zero, and your decisions improve month after
month. Profit is a possible consequence, not a metric you control.

**Failure modes** (each is a chapter in the psychology handbook, with a mechanical defence):
revenge trading after a loss, moving a stop, adding to a loser, over-sizing after a winner, trading
outside the plan's sessions, taking a signal from a stranger, changing rules during a drawdown,
judging decisions by outcomes, and abandoning a tested plan after a normal losing streak.

**The one measurement that matters most:** rule-compliance rate. A trader with a small edge and 95%
compliance is in business; a trader with a great edge and 50% compliance is a donor.

**What this system will not do:** make you a professional trader, remove uncertainty, or turn 250 USD
into a living. It will make you competent, careful and measurable — which is the only foundation on
which any of those outcomes could legitimately be built.
