# COMPLETE CURRICULUM — LEVELS 0 TO 28

Every level has: **objective**, **modules**, **practice** (what you actually do), and a **gate**
(what must be true before the next level starts). Nothing here is optional except where marked
*(optional)*. Risk management (Levels 15–18) may never be skipped, postponed or "picked up later".

Reading time is not learning. Each level's practice requires producing something: a written answer,
a marked chart, a calculated number, a recorded trade.

---

## STAGE 0 — FOUNDATIONS (Levels 0–3)

### Level 0 — Orientation and honest expectations
**Objective:** understand what you are getting into and what "success" means here.
**Modules:** what FX is and is not; market size and participation; the base rate (most retail
accounts lose); why capital preservation outranks profit; the categories FACT / INTERPRETATION /
SCENARIO / SPECULATION; KNOWLEDGE / ANALYSIS / STRATEGY / SIGNAL / RISK MANAGEMENT / EXECUTION /
PERFORMANCE.
**Practice:** write one page: why you are doing this, how much money you can lose without it changing
your life, how many hours per week you have. Store it in your journal as the project's founding note.
**Gate:** you can state, in your own words, the difference between analysis and a signal, and the
difference between an edge and a win streak.
**Quiz categories:** `beginner`, `psychology`.

### Level 1 — Market mechanics
**Objective:** know what physically happens when you click buy or sell.
**Modules:** currencies and pairs; base and quote currency; bid, ask and spread; pips, points and
pipettes; lots, mini, micro, cent accounts; contract size; long vs short; order types (market, limit,
stop, stop-limit); execution models; slippage; swap and triple-swap days; margin, free margin, margin
level, margin call, stop out; leverage vs risk (they are not the same thing); the trading week.
**Practice:** for EURUSD, USDJPY and XAUUSD, compute by hand: pip value for 0.10 lots, the cost of a
2-pip spread, and the margin needed at 1:100. Verify with `python main.py pip` and
`python main.py position`.
**Gate:** all three instruments correct by hand *and* by calculator; you can explain why leverage
changes margin requirements but not the money at risk.
**Quiz categories:** `beginner`, `market_mechanics`.

### Level 2 — Broker and platform reality (Exness, MT4/MT5)
**Objective:** operate the platform correctly and understand broker-specific conditions.
**Modules:** account types and their honest differences (spreads, commission, stop-out level,
minimum lots); the minimum-lot problem on small accounts; order execution on Standard vs Raw Spread;
stop-out and negative balance protection; how to read the instrument specification in MT5; where
spreads widen; swap rates; demo vs live differences (fills, emotions, slippage, but *not* the maths);
what platform-side automation can and cannot do.
**Practice:** in your own terminal, record spread, swap and margin requirement for four instruments
at three different times of day; compare with the config file's verified figures.
**Gate:** a written table of the four instruments with your own captured numbers and the differences
explained. **Always verify broker specifics against current official documentation — never against a
tutorial, a review site or this repository's cached values.**
**Quiz categories:** `market_mechanics`.

### Level 3 — Trading vocabulary and the first calculations
**Objective:** speak the language precisely enough to be taught properly.
**Modules:** R-multiple; risk-reward ratio; expectancy; win rate and its relationship to R:R;
break-even win rate; drawdown; recovery gain; profit factor; position sizing; risk per trade;
portfolio heat; correlation; volatility (ATR); timeframe vocabulary.
**Practice:** convert five trades (given entry, stop, exit) into R-multiples by hand; compute the
break-even win rate for 1:1, 1:2 and 1:3.
**Gate:** quiz ≥ 80% in two categories; five R-multiples correct.
**Quiz categories:** `beginner`, `statistics`.

---

## STAGE 1 — CHART LITERACY (Levels 4–8)

### Level 4 — Candlesticks and price representation
**Objective:** read a candle as information, not as a symbol to memorise.
**Modules:** OHLC; body, wick, close; timeframes; candle-close versus intrabar noise; twelve common
candle shapes (pin, engulfing, inside, doji, marubozu ...) and their *contextual* meaning; why a
pattern alone is not a strategy.
**Practice:** find twenty pin/engulfing candles on H4, and for each record what happened in the next
20 candles — including the failures. Report the honest hit rate you find.
**Gate:** your written tally, including the losing examples, with a conclusion you can defend.
**Quiz categories:** `technical_analysis`.

### Level 5 — Market structure
**Objective:** classify any chart into trend, range or transition, and locate structure objectively.
**Modules:** swing highs/lows; higher highs and higher lows; breaks of structure; trend vs range;
transition zones; false breaks; how timeframe choice changes the structure you see; the difference
between "the trend is up" (fact-ish) and "the trend will continue" (scenario).
**Practice:** classify 20 charts blind (covered trend label), then score yourself.
**Gate:** ≥ 15/20 agreement with your own later, slower assessment.
**Quiz categories:** `technical_analysis`.

### Level 6 — Support, resistance, supply, demand
**Objective:** build a level map with a reason for every line.
**Modules:** how levels form (order clusters, round numbers, session extremes, prior highs/lows);
zones vs lines; level confluence; why levels fail; liquidity above/below obvious levels; the
difference between a level and a signal.
**Practice:** produce a weekly/daily/H4 level map for one pair, then track for five sessions how
price treated each level and how often each reaction was tradable.
**Gate:** the map plus the five-session follow-up, with an honest count of failures.
**Quiz categories:** `technical_analysis`.

### Level 7 — Indicators (and their redundancy)
**Objective:** use indicators as measuring instruments, not as oracles.
**Modules:** moving averages (what an average hides); MACD; RSI and Stochastic (and that they are
close cousins); ATR for volatility context and stop sizing; Bollinger Bands; volume in FX (tick
volume caveat); indicator lag; parameter fitting; redundancy and how to reduce tools, not add them.
**Practice:** demonstrate that RSI and Stochastic give near-identical signals on the same data, then
argue in writing for keeping only one — or neither.
**Gate:** the demonstration plus a written argument.
**Quiz categories:** `technical_analysis`.

### Level 8 — Multi-timeframe analysis and sessions
**Objective:** a repeatable top-down procedure.
**Modules:** higher timeframe bias; mid timeframe structure; lower timeframe trigger; timeframe
conflict; session windows (Sydney, Tokyo, London, New York, overlap); daylight saving; the
low-liquidity lull; how spreads and volatility differ by session; the weekly rhythm of data releases.
**Practice:** write your own top-down procedure in ≤ 10 steps; time yourself using it on three pairs.
**Gate:** the procedure plus three completed analyses produced inside 15 minutes each.
**Quiz categories:** `technical_analysis`, `market_mechanics`.

---

## STAGE 2 — ANALYSIS (Levels 9–14)

### Level 9 — Fundamentals: currencies as claims on economies
**Objective:** understand what moves a currency over weeks and months.
**Modules:** growth, inflation, employment, PMIs; interest rates and rate *expectations*; real yields;
central banks (Fed, ECB, BoE, BoJ, SNB, RBA, RBNZ, BoC) and how to read a statement without a
narrative; trade balances; risk sentiment and funding currencies; the difference between the level
of a rate and the direction of its change.
**Practice:** one-page macro note on one currency: what the central bank is doing, what is priced in,
what would change it.
**Gate:** the note, with sources and dates for every factual claim.
**Quiz categories:** `fundamental_analysis`.

### Level 10 — Economic data and events
**Objective:** know when not to trade, and why.
**Modules:** CPI, PCE, NFP, unemployment, GDP, retail sales, ISM/PMI, central bank decisions and
minutes; publication schedules; how expectations versus actuals drive price; the pre-release liquidity
drop; spread widening and slippage; the honest approach (stand aside, or redefine the stop and size);
why "I'll trade the news" is usually a cost, not an edge.
**Practice:** track five high-impact releases. Record spread 5 minutes before, 1 minute after, the
range in the first two minutes, and what your plan would have done.
**Gate:** the table plus a written protocol for high-impact events.
**Quiz categories:** `fundamental_analysis`.

### Level 11 — Correlations and hidden exposure
**Objective:** see the same idea when it wears three different costumes.
**Modules:** EURUSD/GBPUSD/AUDUSD correlations; the US dollar index; yields and gold; oil and CAD;
correlation instability; why "three longs" is one risk; correlation as a *risk* tool rather than a
signal generator.
**Practice:** find a week where EURUSD and GBPUSD diverged and explain what could have caused it;
then review your own open positions for shared exposure.
**Gate:** the divergence study plus a correlation-exposure table completed for a hypothetical
three-position portfolio.
**Quiz categories:** `fundamental_analysis`.

### Level 12 — Price action: impulse, correction, compression, expansion
**Objective:** describe what price is doing mechanically, without mysticism.
**Modules:** impulse and correction; compression before expansion; consolidation, expansion, climax;
momentum and exhaustion; liquidity sweeps; breakouts and failed breakouts; the objective content of
popular "smart-money" vocabulary (order blocks, liquidity voids, fair value gaps), and which parts of
it are untested claims.
**Practice:** take one such claim, separate its observable part from its interpretive part, and design
a test for the observable part.
**Gate:** the separation plus a test design with a pass/fail criterion.
**Quiz categories:** `technical_analysis`, `strategy`.

### Level 13 — Reading a market like an analyst (structured analysis)
**Objective:** produce a repeatable, decision-ready analysis of any instrument.
**Modules:** the analysis template: macro context, events, central-bank expectations, USD picture,
pair specifics, higher-timeframe structure, levels, volatility, scenarios with invalidation, risk
considerations, no-trade conditions.
**Practice:** produce three analyses on three different pairs; each must contain at least two
scenarios and an explicit invalidation for each.
**Gate:** all three analyses complete, with no buy/sell instruction anywhere in them.
**Quiz categories:** `professional_decision_making`, `fundamental_analysis`.

### Level 14 — Order-flow vocabulary and microstructure caveats
**Objective:** understand what retail data can and cannot show.
**Modules:** what a real order book is in FX (interbank, decentralised); why retail "volume" is tick
volume; the danger of interpreting bid/ask depth from a market-maker feed; the useful parts
(reaction to obvious levels, session extremes).
**Practice:** write a short essay explaining why "the banks are hunting stops" is an interpretation
rather than a fact, and what evidence would be needed to test it.
**Gate:** the essay, plus a statement of which claims you now refuse to make.
**Quiz categories:** `technical_analysis`, `professional_decision_making`.

---

## STAGE 3 — RISK AND MONEY (Levels 15–18) — MANDATORY, NO SKIPPING

### Level 15 — Position sizing from first principles
**Objective:** size any trade, on any instrument, in under 30 seconds, from a risk percentage.
**Modules:** the sizing formula; pip value and why it depends on the quote currency; conversion when
the account currency is not the quote currency; minimum lots and the small-account problem; volume
steps and rounding down; stops in pips vs money; the difference between "position size" and "margin
required"; why leverage is not risk but *can* enable it.
**Practice:** ten trades across four instruments hand-calculated, then verified with
`python main.py position`. Any mismatch means the level is not passed.
**Gate:** 10/10 correct with the arithmetic written out, including one case where the required size is
below the broker minimum and the correct action is to skip the trade.
**Quiz categories:** `risk_management`.

### Level 16 — R, expectancy and drawdown mathematics
**Objective:** think in R, and know what drawdown does to the arithmetic of recovery.
**Modules:** R-multiples; expectancy in R and in money; break-even win rate with and without costs;
payoff ratio; profit factor and its fragility; the drawdown ladder (losses compound on remaining
equity); recovery gain required; losing streaks and their true probability; risk of ruin as a
function of risk per trade; why "I'll risk more to recover" is mathematically self-defeating.
**Practice:** run the drawdown and ruin tools; write down the number of consecutive losses that would
take you to −10%, −20% and −50% at 0.25% and 1% risk; state the maximum streak you should plan for.
**Gate:** the written answers, correct, plus a clear statement of the maximum risk per trade you will
ever use and why.
**Quiz categories:** `risk_management`, `statistics`.

### Level 17 — Psychology of loss and mechanical defences
**Objective:** accept that you will make emotional errors, and design defences *before* they happen.
**Modules:** loss aversion; sunk-cost; the disposition effect; revenge trading; FOMO; overconfidence
after wins; outcome bias; tilt; decision fatigue; checklists and pre-commitment; why a *process*
metric (compliance) beats a *result* metric (P/L) as feedback.
**Practice:** name your three most likely failure modes and, for each, a specific, checkable
counter-measure (for example: "after two losses, I close the platform for 60 minutes").
**Gate:** the three defences written down, each one objectively checkable by a third party.
**Quiz categories:** `psychology`.

### Level 18 — Cost awareness
**Objective:** know exactly what each trade costs you, in money and in R.
**Modules:** spread as a cost; commission; swap; slippage; the real cost of trading the lull;
the cost expressed in R (a 2-pip spread on a 20-pip stop is 0.1R before you start); why high-frequency
styles die on small accounts; the ledger method for tracking costs.
**Practice:** compute your total round-trip cost in money and in R for your typical trade on three
instruments; then compute how many round trips it takes to lose 10% of the account in costs alone.
**Gate:** the calculation, correct. This level is what stops "overtrading" being an abstract idea.
**Quiz categories:** `risk_management`, `market_mechanics`.

---

## STAGE 4 — STRATEGY AND TESTING (Levels 19–23)

### Level 19 — The 13 strategy families
**Objective:** understand frameworks and their required conditions, instead of copying entry rules.
**Modules:** each family: market condition required, entry trigger, stop rationale, target logic,
trade frequency, known failure modes, evidence strength (FACT: mechanical; INTERPRETATION: behavioural
rationale; SPECULATION: no basis).
**Practice:** for three families of your choice, write the conditions under which they should *not* be
traded.
**Gate:** three "do not trade this when" lists that a stranger could apply.
**Quiz categories:** `strategy`.

### Level 20 — Writing a strategy specification
**Objective:** make your rules so precise that execution requires no judgement.
**Modules:** the spec template; entry trigger objectivity; stop placement from structure; target
logic; exclusions; expected statistics; failure conditions; versioning and freezing.
**Practice:** complete `outputs/templates/strategy_specification.md` for one setup.
**Gate:** the completed spec, reviewed a day later, with every ambiguity removed.
**Quiz categories:** `strategy`.

### Level 21 — Backtesting methodology
**Objective:** measure a rule set honestly, before risking anything.
**Modules:** manual backtesting (bar by bar, no peeking); sample size and confidence; costs; spread
variation by session; slippage; survivorship and selection bias; look-ahead bias; data quality
caveats for proxy data; why 20 trades prove nothing; how to record trades in the same schema as live
trades so the two are comparable.
**Practice:** backtest one setup over 100 trades with costs, recording every trade including ugly ones.
**Gate:** 100 trades recorded, costs applied, statistics computed
(`python main.py report --journal backtest.csv`), and a written statement of what would falsify the
setup.
**Quiz categories:** `backtesting`, `statistics`.

### Level 22 — Statistics that do not lie to you
**Objective:** read your own results with appropriate scepticism.
**Modules:** standard error; confidence intervals; the difference between "expectancy > 0" and
"expectancy is measurably > 0"; multiple testing and p-hacking your own strategy; regression to the
mean; streaks; the dispersion of R; why a high profit factor on ten trades means nothing; how the
analytics layer's warnings correspond to these concepts.
**Practice:** compute the confidence interval for your own expectancy; write one sentence on what it
does *not* tell you.
**Gate:** the sentence. If it does not include the word "yet" or the idea of uncertainty, rewrite it.
**Quiz categories:** `statistics`.

### Level 23 — Validation gate: from hypothesis to plan
**Objective:** a seven-stage gate that a strategy must pass before real execution.
**Modules:** (1) rules written; (2) 100+ backtest trades with costs; (3) out-of-sample period;
(4) demo forward test ≥ 40 trades; (5) compliance ≥ 95%; (6) drawdown inside limit; (7) documented
review decision. Each stage has an exit criterion and a rollback.
**Practice:** run your own strategy through the gate; document where it fails.
**Gate:** the completed gate document. Failing a stage is a valid, useful outcome; skipping one is not.
**Quiz categories:** `backtesting`, `professional_decision_making`.

---

## STAGE 5 — EXECUTION AND PSYCHOLOGY (Levels 24–28)

### Level 24 — The daily routine
**Objective:** remove decisions from the moment of execution.
**Modules:** pre-market preparation (calendar, levels, bias, plan for the session); the pre-trade
checklist; position sizing before entry, never after; order placement; stop and target handling;
trade management rules decided in advance; end-of-session review; the trading-day shutdown ritual.
**Practice:** run the routine for five consecutive sessions and log completion.
**Gate:** ≥ 4/5 sessions completed, with the checklists attached.
**Quiz categories:** `professional_decision_making`, `psychology`.

### Level 25 — Journal discipline
**Objective:** record a trade in under five minutes, completely.
**Modules:** the 39-field schema and why each field exists; before/after screenshots; invalidation and
thesis validity; emotional state; rule violations; grading decision quality separately from outcome.
**Practice:** record five trades end-to-end and grade each decision A–F.
**Gate:** five records complete, including one losing trade whose decision you graded "A".
**Quiz categories:** `professional_decision_making`, `psychology`.

### Level 26 — Error taxonomy and correction
**Objective:** classify mistakes so you can fix the expensive ones first.
**Modules:** error classes (planning, execution, risk, psychological, operational); frequency ×
cost × fixability; the "least fixable first" rule; why adding rules can make compliance worse.
**Practice:** review 30 of your records, classify every violation, and compute the R cost of each class.
**Gate:** the classification and one specific fix for the most expensive class.
**Quiz categories:** `professional_decision_making`, `statistics`.

### Level 27 — Performance review and adaptation
**Objective:** change your plan slowly, on evidence, with a documented reason.
**Modules:** weekly review; monthly review (the smallest honest unit); sample-size discipline; one
change at a time; freezing rules; the danger of adapting during a drawdown; when to retire a setup.
**Practice:** produce one weekly and one monthly review from your own data, using the templates.
**Gate:** both reviews, containing exactly one proposed change supported by the statistics.
**Quiz categories:** `statistics`, `professional_decision_making`.

### Level 28 — Operating as a small professional
**Objective:** behave like a small business, not like a gambler.
**Modules:** capital allocation and risk of ruin at the account level; personal accounting (deposits,
withdrawals, costs); taxes and record-keeping *(jurisdiction-specific — verify locally)*; regulatory
reality and why retail leverage caps exist; broker risk (execution, withdrawal, entity);
documentation of the trading plan and its versions; continuous education and peer review.
**Practice:** write your operating statement: maximum risk, instruments, hours, review cadence, and
the conditions under which you would stop trading entirely.
**Gate:** the operating statement, signed and dated, plus a completed readiness assessment
(`python main.py readiness --criteria`).
**Quiz categories:** `professional_decision_making`, `statistics`.

---

## GATES SUMMARY

| Gate | Where | Requirement |
|---|---|---|
| Mechanics | after Level 3 | 80% quiz + 5 correct calculations |
| Chart reading | after Level 8 | classification and level maps produced |
| **Risk (hard stop)** | after Level 18 | sizing 10/10, drawdown ladder written, defences written, costs computed |
| Strategy | after Level 20 | written specification, ambiguity removed |
| Backtest | after Level 23 | 100+ trades with costs, out-of-sample, gate document |
| Demo forward | programme phase 6 | 40+ live-time demo trades with compliance ≥ 95% |
| Execution | programme phase 7 | ≥ 4/5 routine completions, violations trending down |
| Psychology | programme phase 8 | defences written and tested at least twice |
| Readiness | before live | 14 hard criteria (`python main.py readiness --criteria`) |
| Live scaling | after 20 live trades | 0.10% risk, zero violations, documented review |

## HOW TO STUDY (so that it works)

1. **Hand calculation first, tool second.** The calculator confirms; the understanding protects.
2. **Write before you click.** Every idea becomes a written analysis with an invalidation.
3. **One change at a time, documented.** No rule changes during a drawdown, ever.
4. **Quiz yourself with answers hidden.** `python main.py quiz --interactive` — explanations only
   after you commit.
5. **Re-read your own journal monthly.** The patterns in your records are the real curriculum.
6. **Stop when the gate fails.** Repeating a week is cheaper than repeating a blown account.
