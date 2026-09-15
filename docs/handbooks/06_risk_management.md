# RISK MANAGEMENT HANDBOOK

*Chapter 6 of the Forex Mastery Handbook. This is the chapter the whole system is built around. If you
skip it, nothing else in this repository can help you.*

> "Risk management" is not a topic you learn once. It is the set of decisions you make identically on
> your best day and your worst day. This chapter is deliberately mechanical: rules, formulas, tables
> and refusals.

---

## 1. Why this chapter exists

Every documented path from "curious beginner" to "account destroyed" runs through the same four
mechanisms, and all four are risk failures rather than analysis failures:

1. **Position size too large** for the distance between entry and invalidation.
2. **No stop, or a stop that gets moved**, so a planned small loss becomes an unplanned large one.
3. **Risk concentrated** across correlated positions ("three longs" = one bet, three times the size).
4. **Escalation after losses** — increasing size to recover, which is the fastest mathematical route
   to ruin that exists.

Everything below is designed to make those four behaviours difficult, visible, and measurable.

---

## 2. The only formula you must never get wrong

```
risk_money   = equity × risk_percent
risk_per_lot = stop_distance_pips × pip_value_per_lot
lots         = risk_money ÷ risk_per_lot        (then ROUND DOWN to the volume step)
```

Worked example: 1,000 USD account, 1% risk, EURUSD, entry 1.1000, stop 1.0980 (20 pips).

```
risk_money   = 1,000 × 1%     = 10.00 USD
pip value    = 10.00 USD per 1.00 lot (EURUSD, USD account)
risk_per_lot = 20 pips × 10.00 = 200.00 USD
lots         = 10.00 ÷ 200.00  = 0.05 lots
```

Verify with `python main.py position --symbol EURUSD --balance 1000 --risk 1 --entry 1.1000 --stop 1.0980`.

**Three rules that follow from the formula:**

* **Round down, never up.** Rounding up silently increases risk beyond the limit you set. In this
  repository `round_volume` rounds down to the 0.01 step by construction.
* **Size from the stop, never the reverse.** Adjusting the stop to make the size work is how traders
  convince themselves that 2% risk is 1%.
* **Recompute after any change** to entry, stop or account equity. A stale lot size is a hidden risk.

### The small-account problem, stated plainly

On a 250 USD account risking 0.25% (0.625 USD) with a 50-pip stop on EURUSD, the arithmetic gives
0.00125 lots — below the broker minimum of 0.01 lots. The minimum lot would risk 5.00 USD (2.00% of the
account). **This is a structural constraint, not a rounding annoyance.** Your options are:

| Option | Honest assessment |
|---|---|
| Skip the trade | always acceptable; no edge requires you to take every setup |
| Standard Cent account (0.01 cent-lots ≈ 1/100th size) | the practical solution for accounts this small |
| Wider stop / lower-pip-value instrument | changes the risk per pip but not the minimum-lot floor |
| Accept 2% risk deliberately | only if you have recalculated the drawdown ladder at 2% and accepted it *before* the trade |
| Move the stop closer to fit the size | **never** — it changes the trade to fit the position |

At 2% risk, 23 consecutive losses reach −50%. At 0.25%, 277 do. Those two numbers are the entire
argument for either trading smaller lots or trading a smaller risk.

---

## 3. Risk levels and what they are for

| Risk per trade | On 250 USD | Use |
|---|---|---|
| 0.10% | 0.25 USD | the first four weeks of demo execution: learning the process at negligible cost |
| 0.25% | 0.63 USD | standard demo risk; where a first live evaluation belongs |
| 0.50% | 1.25 USD | only after 100+ journalled trades with ≥ 95% rule compliance |
| 1.00% | 2.50 USD | **hard cap. No exceptions, including during winning streaks** |

Percentage risk is a *decision*, fixed in advance. The dollar amount is an output of that decision — it
is not an input.

---

## 4. Drawdown: the arithmetic you must internalise

Losses compound on the *remaining* equity, so the number of losses to reach a drawdown level is:

```
n = ceil( ln(1 − dd) ÷ ln(1 − risk) )
```

| Risk per trade | to −5% | to −10% | to −20% | to −30% | to −50% |
|---|---|---|---|---|---|
| 0.10% | 52 | 106 | 224 | 357 | 693 |
| 0.25% | 21 | 43 | 90 | 143 | 277 |
| 0.50% | 11 | 22 | 45 | 72 | 139 |
| 1.00% | 6 | 11 | 23 | 36 | 69 |
| 2.00% | 3 | 6 | 12 | 18 | 35 |
| 5.00% | 1 | 3 | 5 | 7 | 14 |

And the recovery requirement on what is left:

| Drawdown | Gain required |
|---|---|
| −5% | +5.3% |
| −10% | +11.1% |
| −20% | +25.0% |
| −30% | +42.9% |
| −50% | +100.0% |
| −70% | +233.3% |

```bash
python main.py drawdown --balance 250
```

**Read the two tables together.** The first table says how long a streak of losers it takes to damage
you. The second says how much work it is to repair. This is why the risk per trade is small: not
because losing is unlikely, but because losing is certain to happen several times in a row, and the
recovery cost grows faster than the damage.

### Losing streaks are more common than intuition suggests

At a 45% win rate, over 100 trades, the probability of a run of at least six consecutive losses is
about **73%**. The engine computes this exactly rather than approximately:

```bash
python -c "from forex_mastery.core.risk import losing_streak_probabilities as f; \
print(dict(f(0.45, 8)))"
# {1: 1.0, 2: 1.0, 3: 0.99998, 4: 0.99380, 5: 0.92050, 6: 0.72897, 7: 0.49706, 8: 0.30681}
```

Interpretation: in 100 trades at a 45% win rate, a run of 6 consecutive losses has about a **73%**
chance of occurring at least once; a run of 8 has about a **31%** chance. These are not
tail events — they are the expected texture of a normal distribution of outcomes. Size accordingly.

A trader who does not expect a six-loss streak will meet one, conclude the strategy is broken, and
either abandon it or start improvising. A trader who expects it — and has sized so that it costs
10–15% rather than 60% — just keeps trading the plan.

---

## 5. Risk of ruin: the number that decides your size

"Risk of ruin" here means: *the probability that a sequence of losses takes the account to a level from
which the plan cannot continue*. It is a function of your edge, your risk per trade, and the level you
define as ruin.

```bash
python main.py ruin --win-rate 0.45 --rr 1.5 --risk 0.25 --trades 300 --paths 20000
```

The simulation assumes a 45% win rate at 1:1.5 with no cost advantage, and reports the distribution of
outcomes rather than a single number: probability of ruin, probability of each drawdown level,
percentiles of final equity. Two cautions, both essential:

* **It is not a forecast.** It shows what happens *if* your edge is real and stable. That "if" is the
  unproven part.
* **Costs change everything.** Add `--cost 0.05` (a typical round-trip cost of 5% of R) and the same
  simulation looks materially worse. Always model costs; `python main.py compound --cost 0.05` does the
  same for projections.

---

## 6. Portfolio heat, correlation and hidden size

Risk per trade limits **one** trade. Your account is exposed to the sum of all of them.

| Concept | Definition | Limit here |
|---|---|---|
| Open risk (heat) | Σ (remaining risk to stop) ÷ equity | ≤ 2% |
| Correlated positions | positions sharing a currency direction/story | ≤ 1 per story |
| Effective leverage | Σ notional ÷ equity | a sanity check, ideally ≤ 10:1 |

EURUSD long, GBPUSD long and XAUUSD long are not three trades; in a dollar-negative environment they
are one position with three times the size. The correlation table in
`outputs/templates/correlation_exposure.csv` exists to make this visible before the fact.

```bash
python main.py rules --symbol GBPUSD --direction long ... --correlated 1 --heat 1.5
```

---

## 7. Costs as risk

Costs are certain; edge is uncertain. A trade with a 20-pip stop and a 2-pip spread begins 0.1R
behind. Twenty such trades cost 2R before the market has done anything.

* Express every cost **in R**, not just in pips: `cost_in_R = spread_pips ÷ stop_pips + commission_in_R`.
* Kill styles that need high frequency to work. On a small account, the spread is the house edge.
* Avoid the low-liquidity lull (~21:00–00:00 UTC): wider spreads, thinner liquidity, more slippage.
* Check swap before holding positions overnight; Wednesday (Thursday for USDCAD) carries triple swap.

---

## 8. The prohibited list, with the mathematics of why

| Practice | Why it is prohibited |
|---|---|
| Martingale / doubling after losses | guarantees that the rare long losing streak takes the entire account; the probability of ruin approaches 1 as the sequence extends |
| Grid trading as a guaranteed system | hides the true risk as unrealised loss; one sustained trend removes the account |
| Averaging down without predefined risk | increases size into an adverse move with no defined invalidation — the opposite of sizing from the stop |
| Revenge trading | substitutes emotion for process at the moment when judgement is most impaired |
| Unlimited leverage | not dangerous by itself, but it removes the mechanical constraint that would otherwise prevent a catastrophic size |
| Chasing signals | removes your ability to state assumptions, invalidation and risk — the three things every trade requires |
| Moving stops | converts a defined risk into an undefined one; the single most expensive habit in retail trading |
| "100% win rate" systems | mathematically impossible and a reliable marker of fraud |
| Increasing size after wins | confuses a favourable sequence with improved skill; risk is set by the plan, not the mood |

If a technique on this list is ever presented to you as the solution to losing, the correct response is
to calculate what it does to the drawdown ladder and to ask who benefits from you believing it.

---

## 9. The risk routine (what you actually do)

**Before every session:** state equity, current daily/weekly P/L, and remaining daily/weekly risk
budget. `python main.py journal summary` gives you the numbers.

**Before every trade:**

1. Write the invalidation price and the structural reason for it.
2. Compute risk in money and size in lots with the calculator — never by eye.
3. Check correlation and total heat.
4. Check the news window (no entry within 30 minutes before / 15 minutes after high-impact releases).
5. Run the rule engine: `python main.py rules ... --from-journal`.
6. If the verdict is NO TRADE, explain it in the journal and move on. A refused trade is a successful
   use of the system.

**Every week:** compare actual risk taken against the planned risk on every trade
(`python main.py report`) and count violations. The violation rate — not the P/L — is the number that
predicts your future.

**After any violation:** write down what you were feeling, what the trigger was, and which mechanical
defence would have prevented it. Then implement that defence. Do not add rules that cannot be checked.

---

## 10. The risk questions you must be able to answer from memory

1. On a 250 USD account, what is 0.25% in money, and what is 1% in money?
2. How many consecutive losses take you to −10% at 0.25% and at 1%?
3. What gain is required to recover from −20%, −30%, −50%?
4. What is the pip value of 0.01 lots on EURUSD, USDJPY at 150.00, and XAUUSD?
5. What is your maximum risk per trade, and what event would make you change it? (The correct answer
   is "nothing objective; only a written plan revision after a documented review".)
6. What is your maximum number of concurrent positions, and why is correlation the reason?
7. What is your round-trip cost in money and in R on your typical trade?
8. What will you do after two consecutive losses? (Answer must be mechanical and checkable.)

If any answer is uncertain, that is your study task — the readiness assessment at
`python main.py readiness --criteria` will ask you the same things later, and it will not accept
"roughly".
