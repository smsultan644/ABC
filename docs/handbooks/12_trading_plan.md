# PROFESSIONAL TRADING PLAN

*Chapter 12 of the Forex Mastery Handbook, and the document that governs every trade you take.*

**A trading plan is not a description of what you hope will happen.** It is the set of decisions you
have already made, in writing, so that you do not have to make them while money is at risk. If your
plan does not answer a question, the answer is "do not trade until it does".

Copy the block below into a new file (`docs/handbooks/my_trading_plan.md`), fill it in, date it and
freeze it. Change it only through the monthly review process (Level 27) — never during a drawdown and
never mid-session.

---

## THE PLAN TEMPLATE

### 0. Metadata
* Author:
* Version: v1.0
* Date frozen:
* Next scheduled review: (one month from the freeze date, then monthly)
* Account: demo / live · starting equity · broker entity and account type

### 1. Purpose and constraints
* Why I trade (in one sentence, without the word "profit"):
* Money I can lose entirely without it changing my life:
* Hours per week I can genuinely commit:
* Sessions I can attend (in **my** local time):
* Maximum risk per trade (percentage) and the reason:
* Hard limit: I will never risk more than ______% per trade.
* I will not trade when: (illness, stress, sleep deprivation, after a loss limit, after a rule
  violation, during a high-impact news window, in the 21:00–00:00 UTC lull)

### 2. Instruments and conditions
* Instruments I am permitted to trade (maximum three): __________
* Sessions permitted: __________
* News rule: no new positions within 30 minutes before or 15 minutes after a high-impact release
* Volatility rule: only when ATR is inside my tested band (______ to ______ pips)
* Spread rule: do not enter when the spread exceeds ______ pips

### 3. Setups (each one must have a written specification — see the strategy specification template)
| Setup name | Market condition required | Entry trigger | Stop rationale | Target logic | Expected frequency |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |

Permitted setups (from `config/strategy_rules.json`): trend_pullback, range_reversal,
breakout_retest, session_open, news_fade. **Any setup not written here does not exist**, no matter how
good it looks in the moment.

### 4. Position sizing
* Formula: `lots = (equity × risk%) ÷ (stop_pips × pip_value_per_lot)`, always rounded **down**
* Verified with `python main.py position` before every order, every time
* If the required size is below the broker minimum: skip the trade, or trade a Cent account — never
  move the stop to make the arithmetic work
* Maximum concurrent positions: ______
* Maximum correlated positions per currency story: 1
* Maximum portfolio heat: ______%

### 5. Risk limits
| Limit | Value | Action when reached |
|---|---|---|
| Risk per trade | ____% | no larger order is permitted |
| Daily loss | ____% | stop trading for the day, journal the reason |
| Weekly loss | ____% | stop trading for the week, review on paper |
| Consecutive losses | 3 | 60-minute break, then re-read this plan before the next trade |
| Monthly drawdown | ____% | revert to the previous phase (demo, lower risk, study) |

### 6. Execution rules
* Order type per setup:
* Where the stop goes and why (structure, not pips):
* Take profit method (fixed R / structure / partial + trail):
* Break-even rule (if any) — and the evidence that it improves the system rather than just the feeling
* Maximum trades per day:
* How I record the trade before and after (screenshot names included)

### 7. Record-keeping
* Journal fields required: all 39, no blanks in invalidation, reason for exit, lesson, emotional state
* Screenshots before and after: mandatory
* Weekly review: every Saturday, using `docs/handbooks/14_weekly_review.md`
* Monthly review: last day of the month, using the monthly template and `python main.py report`

### 8. Review and change control
* One change at a time, documented with the evidence that motivated it
* No rule changes for at least 30 trades after a change
* A change requires: the statistic that prompted it, the new rule, the date, and the condition that
  would revert it
* I will not change rules while in drawdown, and I will not change them mid-session

### 9. Prohibited (non-negotiable)
Martingale · grid-as-guarantee · doubling after losses · averaging down without predefined risk ·
moving a stop against the position · unlimited leverage · revenge trading · overtrading · trading
without a stop · taking positions from signals or social media · trading instruments not listed in
section 2 · trading while intoxicated, exhausted or emotionally compromised.

### 10. My three personal failure modes and their mechanical defences
| Failure mode | Trigger I can recognise | Mechanical defence |
|---|---|---|
| | | |
| | | |
| | | |

### 11. Signature
I have written this plan myself. I understand it does not predict the market and cannot guarantee a
profit. I agree to follow it, and to record honestly every occasion on which I do not.

Signed: ____________________  Date: ____________

---

## HOW TO USE THIS PLAN (the part most people skip)

1. **Freeze it before you trade.** An unfrozen plan is a preference.
2. **Re-read it at the start of every session** — 90 seconds, out loud if possible. This is the single
   highest-value habit in this handbook.
3. **Check compliance, not profit.** At the end of each week, count trades that followed the plan.
   95%+ is the target; the P/L is noise until compliance is high.
4. **Never argue with your own plan in the moment.** If it is wrong, it will still be wrong after the
   market closes, and you can change it then with evidence.
5. **Keep every version.** The history of your rule changes is the most honest record of your
   development as a trader.
