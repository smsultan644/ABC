# DAILY TRADING CHECKLIST

*Chapter 13 of the Forex Mastery Handbook. Designed to be printed, or kept beside the platform. Total
time: ~12 minutes per session, plus ~5 minutes per trade.*

**Why a checklist.** Under time pressure, working memory fails in predictable ways. A checklist is not
a beginner's crutch; it is how pilots, surgeons and professional traders remove the most common class
of error. The measure of success is not that you *know* these items — it is that you *do* them when you
are tired, bored or annoyed.

Copy this into your journal each session, or use the CSV template in
`outputs/templates/market_analysis_template.csv`.

---

## 1. PRE-SESSION (before you look at a chart — 5 minutes)

- [ ] Sleep, health, mood: am I fit to make decisions today? (1–5 on each; if any is 1, **do not trade**)
- [ ] How many hours until I must stop? Do I have a hard stop time today?
- [ ] Economic calendar checked: any high-impact release in the next 4 hours? At what time (UTC)?
- [ ] Yesterday's open positions: still inside plan, or do they need a decision *before* I look at new setups?
- [ ] Account state: equity, today's P/L, this week's P/L, remaining daily/weekly risk budget
      (`python main.py journal summary`)
- [ ] Am I inside a loss-limit stop (daily −1%, weekly −3%) or a mandatory cooldown after 3 losses?
- [ ] Do I already have positions expressing the same currency idea I am about to take?

## 2. MARKET PREPARATION (before any idea — 4 minutes)

- [ ] Sessions open now, and which is my permitted session?
- [ ] Higher-timeframe (W1/D1) structure: trend, range or transition — written in one line
- [ ] H4 structure and the levels that matter today (with the reason each matters)
- [ ] Where are the obvious stop clusters (session high/low, round numbers, prior day's range)?
- [ ] Volatility: ATR inside my tested band?
- [ ] Spread on my instruments: normal, or widened (news, lull, illiquid hour)?
- [ ] Written plan for the day: two scenarios (bullish and bearish) and the level that invalidates each
- [ ] Decision: is today a trading day at all? ("No" is a valid and common answer.)

## 3. PER-TRADE (before clicking — about 90 seconds, no exceptions)

- [ ] Setup name — one of the setups in my written plan. If it is not in the plan, **stop here**.
- [ ] The setup's required market condition is present (trend, range, level, session, volatility)
- [ ] Entry trigger has objectively occurred (not "it looks like it might")
- [ ] Entry price, and what I am paying in spread right now
- [ ] Stop price **and the structural reason** it means my idea is wrong
- [ ] Target price and why price should reach it
- [ ] Risk in percent → risk in money (`equity × risk%`)
- [ ] Position size calculated with the tool, **rounded down** to the volume step
- [ ] Position size cross-checked by hand (does the number feel right for this stop distance?)
- [ ] Reward:risk ≥ 1.5 before costs; and ≥ my minimum after costs
- [ ] Invalidation written in words (the condition that ends the idea without the stop being hit)
- [ ] Correlation check (am I doubling an existing exposure?)
- [ ] Portfolio heat after this trade within limit
- [ ] Not within 30 minutes before / 15 minutes after high-impact news
- [ ] Rule engine verdict (`python main.py rules ... --from-journal`) is APPROVED or
      APPROVED WITH WARNINGS — and if warnings, I have read them
- [ ] Screenshot taken **before** entry, with the levels marked
- [ ] Final question: **would I take this trade if I had just lost three in a row?** If no, the reason
      is emotional, not technical. Do not take it.

## 4. DURING THE TRADE

- [ ] Stop and target are in the platform, not in my head
- [ ] I have written down what would make me close early (and it is not "discomfort")
- [ ] I am not watching the position tick by tick; I have set an alert at the levels that matter
- [ ] No moving the stop away from the position. Ever. (Tightening per plan is allowed only if the plan
      says so.)
- [ ] No adding to a losing position, in any form, for any reason

## 5. POST-TRADE (within 10 minutes — this is where the learning happens)

- [ ] Exit recorded: price, reason, and whether the thesis was valid
- [ ] P/L and R-multiple recorded (R is derived, never typed: `python main.py journal close ...`)
- [ ] Live screenshot **after** the trade
- [ ] Decision grade A–F, judged on the process, ignoring the outcome:
      A = plan followed exactly · B = minor deviation, no risk impact · C = plan bent but risk kept ·
      D = risk limit exceeded or stop moved · F = prohibited practice
- [ ] Lesson in one sentence (if there is nothing to say, say "process followed; nothing to add")
- [ ] Rule violations listed explicitly, with the cost in R

## 6. END OF SESSION (3 minutes)

- [ ] All trades journalled and closed out (or consciously carried overnight with swap checked)
- [ ] Trades today: count, total R, rule violations count
- [ ] Daily P/L against the daily loss limit
- [ ] One sentence on what I did well (be specific — vague praise teaches nothing)
- [ ] One sentence on what I will do differently next session (maximum one change)
- [ ] Platform closed. The market will still be there tomorrow.

## 7. WEEKLY (Saturday, 60–90 minutes — no trading)

- [ ] Update the weekly review (`docs/handbooks/14_weekly_review.md`)
- [ ] `python main.py report` — statistics, expectancy, drawdown, breakdowns by setup/session/instrument
- [ ] Count rule violations and compute their cost in R
- [ ] Review every screenshot from the week (fast: 10 seconds each; slow: any trade you do not remember)
- [ ] Compare this week with the previous four, looking for *patterns*, not single events
- [ ] Decide the *one* change for next week, or decide to change nothing
- [ ] Re-read the trading plan, then confirm or adjust it in writing

---

## THE THREE QUESTIONS THAT PREVENT MOST DISASTERS

1. **"What is the invalidation?"** If you cannot answer in one sentence, you do not have a trade.
2. **"How much am I risking, in money?"** If you cannot state the number, you have not sized it.
3. **"What would I do if this were my last 250 USD?"** If the answer changes your decision, your
   decision is being driven by consequence rather than by process — take no trade today.

## A NOTE ON RULE VIOLATIONS

A violation is not a moral failure; it is data. Record it without drama, compute what it cost in R, and
identify which mechanical defence would have prevented it. Then implement that defence before the next
session — a rule you cannot check is not a defence, it is a wish. Track your violation rate weekly:
below 5% is the readiness threshold, and it matters more than your win rate because it is the only one
of the two you fully control.
