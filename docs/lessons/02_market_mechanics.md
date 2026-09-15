# LESSON 2 — Market Mechanics: What Actually Happens When You Click Buy

**Level:** 1–2 (Market mechanics; broker and platform reality)
**Estimated time:** 2 sessions of 60–75 minutes, plus the terminal exercises
**Prerequisites:** Lesson 1 passed (pip value, sizing, R, drawdown arithmetic)
**What you will be able to do afterwards:** describe the full lifecycle of an order; explain the
difference between a stop loss and a limit order and why one can slip while the other can simply not
fill; compute your real cost per trade in money and in R; read margin, margin level and stop-out
correctly; and explain why **leverage changes nothing about how much you can lose on a defined stop**.

> **Verification rule.** Brokers change specifications. Everything broker-specific in this lesson was
> read from **official Exness documentation on 2026-09-15**, is labelled as such, and tells you how to
> confirm it yourself. Where a number is illustrative it is marked *(illustrative)*. Nothing here is
> copied from a review site, a course or a forum. **Your terminal's specification always wins.**

---

## 1. The lifecycle of one trade

When you click **Buy** on EURUSD at 1.10000, this is what actually happens:

| # | Step | What matters to you |
|---|---|---|
| 1 | Your platform shows a **bid** (what buyers pay you) and an **ask** (what you pay to buy) | the gap is the spread — your first cost, paid immediately |
| 2 | You buy at the **ask**; the position opens instantly | your entry is not the mid-price you saw on a chart |
| 3 | The position is now valued at the **bid** | you are already down by the spread, on paper |
| 4 | Margin equal to `notional ÷ leverage` is **held** (not paid) | this affects free margin, not your risk |
| 5 | The position carries a floating P/L that moves with the price | your stop and target are prices, not "amounts" |
| 6 | Overnight, a **swap** is credited or debited at the rollover time | costs accumulate if you hold |
| 7 | You close: you sell at the **bid** | spread is paid twice in effect: on entry and on exit |
| 8 | P/L settles in the **quote currency**, then converts to your account currency | why a JPY pair's pip value moves with the price |

Two consequences beginners consistently miss:

* **A long position is instantly in loss by the spread.** You do not start at zero; you start at
  −1 spread. Every trade must earn that back before it earns anything.
* **Chart prices are approximations.** Your chart may plot the bid (default on most platforms). Your
  entry and your stop execute on the correct side of the spread, not on the plotted line.

---

## 2. Order types, and what each one can do to you

| Order | What it does | Failure mode you must plan for |
|---|---|---|
| **Market** | fills immediately at the best available price | fills at whatever price is available — can be worse than the quote you saw |
| **Buy/Sell limit** | fills only at your price or better | **may never fill**; the market can move away without you. There is no "should have filled" |
| **Buy/Sell stop** | becomes a market order once price reaches the level | **slippage**: in fast markets it fills beyond the level |
| **Stop loss** | a stop order attached to your position | it is a market order — it protects you *approximately*, not exactly; in a gap it fills at the next available price |
| **Take profit** | a limit order attached to your position | it fills at your price or better — no slippage, but it can be missed by a fraction of a pip |
| **Trailing stop** | stop that follows price at a distance | usually reduces expectancy when moved by feel; only use with a tested rule |

**The asymmetry to internalise:** the order that protects you **can slip**, and the order that pays you
**can miss**. Any strategy whose survivability depends on a stop being filled *exactly* is not a
strategy; it is an assumption. This is why the system sizes from the **risk** (a fixed money amount),
not from the stop distance alone.

---

## 3. Slippage and spread widening: when execution costs more

Spreads are not constant, and the moments when they widen are precisely the moments beginners want to
trade:

| Condition | Typical behaviour | What to do |
|---|---|---|
| London/New York overlap | tightest spreads, fastest movement | your normal trading window |
| Rollover (~21:00–22:00 UTC) | spreads widen sharply for a few minutes | do not enter; the system treats 21:00–00:00 UTC as a lull |
| High-impact news (CPI, NFP, central banks) | spread multiples of normal, slippage, stop orders fill far from the level | no new positions within 30 min before / 15 min after |
| Sunday open / weekend gap | gaps from Friday's close; stops can fill far away | the system does not trade at the open |
| Late Friday | liquidity declines into the close | flat before the weekend until you have evidence you should not be |

**Illustrative, not a broker claim:** if your instrument's normal spread is 1.2 pips and it widens to
6 pips for three minutes around a release, your cost on a 0.01-lot trade is five times normal, and a
20-pip stop can be hit by the spread alone. Measure it yourself (Exercise 3) instead of trusting any
number in this file — including this one.

---

## 4. Costs, in money and in R

Four costs exist. Learn them as a **stack**, not as separate items:

```
total cost per round trip = spread cost + commission + swap (if held) + slippage
cost in R                 = total cost ÷ risk per trade
```

Worked, verified with the calculation engine on EURUSD, **0.01 lots**, 30-pip stop, 2-pip spread:

| Item | Calculation | Result |
|---|---|---|
| Pip value | 0.01 lots × 100,000 × 0.0001 | **0.10 USD / pip** |
| Risk per trade | 30 pips × 0.10 | **3.00 USD** |
| Spread cost (round trip equivalent) | 2 pips × 0.10 | **0.20 USD** |
| Cost in R | 0.20 ÷ 3.00 | **0.0667R** |

So before the market has done anything, that trade must earn **6.7% of one R** just to break even. Now
run the same trade on a 10-pip stop: cost = 0.20 ÷ 1.00 = **0.20R**. The shorter your stop, the larger
your cost in R becomes — which is exactly why very short stops are usually a cost trap for retail
traders rather than a sign of skill.

If your account is **Raw Spread** style (commission charged per side per lot — official Exness
documentation states from 3.5 USD per side per lot, verified 2026-09-15), then at 0.01 lots the
round-turn commission is ≈ **0.07 USD**, i.e. a further **0.023R** on a 3.00 USD risk. Small in money,
material in R when you trade often. On **Standard** accounts the official documentation states there is
no commission and the cost is in the spread, which is wider. Neither structure is "cheaper"; they trade
one cost for another, and you must compute yours.

**Swap** is charged or credited when you hold a position through the rollover time. Official Exness
documentation states that a **triple swap is applied on Wednesday** for most instruments, and on
**Thursday for USDCAD** (verified 2026-09-15). Swap rates are instrument- and direction-specific and
change; *(illustrative)* a −0.45 USD per night charge on 0.01 lots is 0.15R per night on a 3.00 USD
risk — three nights is nearly half your risk. Read your own instrument's swap in the terminal
(**Specification → Swap long / Swap short**) rather than trusting any example.

---

## 5. Margin: what leverage really changes

Margin is a **deposit held while the position is open**. Verified with the engine for **0.01 lots of
EURUSD at 1.1000**:

| Leverage | Margin held | What it changes |
|---|---|---|
| 1:100 | 11.00 USD | how much free margin remains |
| 1:500 | 2.20 USD | nothing about your risk |
| 1:1000 | 1.10 USD | nothing about your risk |
| 1:2000 | 0.55 USD | nothing about your risk |

* **Notional** = 0.01 × 100,000 × 1.1000 = **1,100 USD**. On a 250 USD account that is **4.4:1
  effective leverage** — a far more meaningful number than the broker's headline.
* **Margin level** = equity ÷ used margin. With 250 USD equity and 0.10 lots held at 1:2000
  (5.50 USD used), margin level = **4,545%**. Margin level tells you how much room you have before the
  broker acts; it does **not** tell you how much you are risking.

### Margin call and stop out

* **Margin call** — a warning threshold (official Exness documentation: **60%** for Standard accounts).
* **Stop out** — forced closure of positions (official: **0%** for Standard, Standard Cent, Pro, Raw
  Spread and Zero; the figure can rise under increased market risk, and differs for some entities —
  verify yours).

**What 0% actually means, computed rather than described.** Long 0.10 lots EURUSD at 1.1000 with 250 USD
equity, single position, no other margin used:

| Stop-out level | Price that triggers it | Distance | Loss at that point |
|---|---|---|---|
| 0% (Standard, as documented) | **1.07500** | 250 pips | **250.00 USD — the entire account** |
| 60% (for comparison) | 1.08149 | 185 pips | 185.00 USD |

Read that table twice. **0% stop out is not a safety feature; it means the broker may not close your
position until the account is essentially empty.** Leverage did not change that price at all (1:100 and
1:2000 both give 1.07500) — leverage changed only the margin held. Your own stop is the only protection
that acts before then. For scale: at the 0.01-lot size this system has you trade, the same 0%-stop-out
account would need a move of **2,500 pips** (to 0.85000) to be emptied by one position.

```bash
python main.py position --symbol EURUSD --balance 250 --risk 0.25 --entry 1.1000 --stop 1.0950 \
    --leverage 2000
```

Two related protections you should still understand (both verified from official Exness documentation,
2026-09-15):

* **Negative Balance Protection** — a retail account cannot end up owing the broker money.
* **Stop Out Protection** — the platform may use a virtual mid-price equity and defer the stop out;
  it can delay closure but it is not a guarantee about the fill price, and it may be unavailable on
  some account configurations (for example unlimited-leverage accounts). Do not build a plan that
  depends on it.

---

## 6. Platform and contract mechanics you will meet in MT5

| Item | Official Exness figure (verified 2026-09-15) | Why you care |
|---|---|---|
| Contract size, FX | 100,000 base units | every pip-value calculation |
| Contract size, XAUUSD | 100 troy ounces | gold's pip is 1/100th the money value per lot |
| Minimum volume | 0.01 lots | the small-account constraint from Lesson 1 |
| Volume step | 0.01 lots | size is rounded **down** |
| Max volume, Standard | 200 lots 07:00–20:59 GMT, 60 lots 21:00–06:59 GMT | irrelevant at your size; it shows that even position limits exist and change by hour |
| Hedged margin | 0% | holding long and short of the same symbol needs no extra margin — but you pay **two spreads** and a swap on one leg, so it is not free or riskless |
| Execution | market execution | your order fills at whatever is available; slippage is possible |
| Swap-free | available on some accounts | "swap-free" usually means a fee or wider spread replaces the swap; verify before assuming a cost is gone |

**Instrument specifications are not interchangeable.** A "100-pip stop" on XAUUSD is a different money
risk from a 100-pip stop on EURUSD, because the pip sizes and pip values differ. This system always
sizes from the money risk and the stop distance in pips; it never assumes a pip means the same thing
across instruments. Check any instrument's specification in MT5 via
**Market Watch → right-click the symbol → Specification**, and see
`python main.py specs --symbol XAUUSD`.

---

## 7. How to verify anything a broker tells you (the professional habit)

1. **Primary source only:** the broker's own help centre / legal documentation for your entity — not a
   review site, not a video, not a forum post, not this file.
2. **Match your entity and account type.** Stop-out levels, leverage caps and minimum deposits vary by
   country of registration and account type. Official Exness documentation states minimum deposit is
   **region based** — meaning any single hard number you read elsewhere is probably wrong for you.
3. **Confirm in the terminal.** MT5's Specification window is the authoritative numbers for your
   account right now: contract size, digits, volume min/step/max, swap long/short, margin rate.
4. **Re-verify anything older than a quarter.** Specifications and conditions change; a fact verified
   in September is a hypothesis in December.
5. **Write the number and the date in your journal.** "Spread on EURUSD at 08:30 UTC was 1.4 pips on
   2026-09-15, source: my terminal" is evidence. "Spreads are usually about a pip" is folklore.

**Labelling, applied to this section:**

* **FACT** — "Official Exness documentation states a 0% stop out for Standard accounts (read
  2026-09-15)."
* **INTERPRETATION** — "A 0% stop out removes the broker's automatic protection before your account is
  empty, so the trader's own stop is doing more work than on a 20%-stop-out account."
* **SCENARIO** — "If I hold a losing position through rollover three nights running, my realised cost
  will be the swap plus the spread."
* **SPECULATION** — "Unlimited leverage means Exness wants me to lose faster."

---

## 8. Setting up your demo account without creating bad habits

Do these in order, and do not fund anything:

1. Open an **Exness demo** account (not live), Standard or Standard Cent depending on what the
   platform offers you; take the default leverage.
2. In MT5: **Market Watch → right-click → Specification** for EURUSD, GBPUSD, USDJPY and XAUUSD.
   Record: contract size, digits, volume min/step, swap long/short, margin.
3. Place **one** 0.01-lot order with a stop and a target, then close it. Do not try to profit. The
   purpose is to see: the entry at the ask, the immediate small loss equal to the spread, the swap
   column the next day if you hold overnight.
4. Screenshot the **spread** at four times: 08:00 UTC, 14:00 UTC, 21:30 UTC, and on a Sunday evening.
   You now have your own verified cost table.
5. Fill `outputs/templates/market_analysis_template.csv` for one instrument — read-only exercise, no
   trade decision.

**Do not** open a live account "just to test with a small amount", do not enable unlimited leverage,
and do not add funds until the readiness assessment (`python main.py readiness --criteria`) passes —
that is 14 hard conditions, deliberately.

---

## 9. Exercises

1. You buy 0.02 lots EURUSD at an ask of 1.10020; the bid is 1.09998. **(a)** What is the spread in
   pips? **(b)** What is your floating P/L immediately after entry, in USD? **(c)** In R, if your stop
   is 25 pips away?
2. 0.05 lots of GBPUSD, 40-pip stop. Compute the pip value, the risk in USD, and the percentage of a
   250 USD account.
3. Record your own four spread readings from §8 step 4. Compute the **cost in R** for each reading on a
   30-pip stop (0.01 lots).
4. Margin: compute the margin required for 0.02 lots of EURUSD at 1.1000 at 1:200, 1:1000 and 1:2000.
   Then state, in one sentence, what changed and what did not.
5. Using the engine, compute the price at which a 0% stop out would close a 0.05-lot long EURUSD
   position entered at 1.1000 with 250 USD equity. How far is that in pips, and what percentage of the
   account is that loss?
6. You enter long at 1.1000 with a stop at 1.0970 and a target at 1.1060. Compute the R:R before
   costs, then the R:R after a 2-pip spread on each side.
7. Explain in your own words, in under 60 words, why a stop loss can fill worse than its level while a
   take profit cannot fill better than its level. (The answer is about order types, not about brokers.)
8. Your broker offers a swap-free account. Write two sentences: what "swap-free" removes, and what you
   must check to see whether the cost has genuinely disappeared.
9. Name three moments in a normal week when you will **not** enter a trade, and the mechanism that
   makes each dangerous.
10. A trader says: "I use 1:2000 leverage, so my risk is higher." Is that statement true, partly true or
    false? Justify it with the numbers from §5.

---

## 10. Short test (answers hidden)

1. When you buy at market, which price do you pay, and at which price is the position valued right
   afterwards?
2. Why does a new long position show a small loss immediately after entry?
3. What is the difference in execution risk between a stop order and a limit order?
4. Which order type guarantees a price but not an execution, and which guarantees an execution but not
   a price?
5. Give the four components of your round-trip cost stack, and say which one is charged twice.
6. What is the pip value of 0.02 lots of EURUSD in USD, and what is the cost in R of a 2-pip spread on
   a 25-pip stop?
7. On a 250 USD account, 0.01 lots of EURUSD at 1.1000: state the notional, the margin at 1:500, and
   the effective leverage.
8. On an account with a documented 0% stop out, what does that mean for a single position — and what is
   the only thing that stops you losing the account's committed capital?
9. Which day carries a triple swap for most instruments, and which instrument is the documented
   exception?
10. The broker's specification says the instrument's margin rate is 1% and the minimum volume is 0.01.
    Which of those two numbers affects your risk per trade, and why?

**Pass standard:** 8 of 10, with the arithmetic written out for questions 6 and 7. If you cannot do
those two without the tool, redo Lesson 1 §3 and Exercises 1–3.

---

## 11. Deliverable for this lesson

Write into your journal, and keep it as a reference page:

1. Your **own verified cost table**: instrument, spread at four times of day, swap long/short, contract
   size, volume min/step — with the date and the source (your terminal).
2. The **cost in R** for your typical trade on your main instrument, computed both with and without
   commission.
3. Your **leverage decision**: which leverage you will use and why, plus the statement "leverage changes
   the margin held, not the money at risk on a defined stop" in your own words.
4. Your **three no-entry windows** (news, rollover lull, Sunday/Friday edge hours) with the reason for
   each.

Then run:

```bash
python main.py specs --symbol EURUSD
python main.py pip --symbol GBPUSD --lots 0.05 --pips 40
python main.py position --symbol EURUSD --balance 250 --risk 0.25 --entry 1.1000 --stop 1.0975
python main.py sessions --tz <Your/Timezone>
python main.py quiz --category market_mechanics --n 8 --interactive
```

**Next:** Lesson 3 — the Exness / MetaTrader 5 operating guide (account types, order entry, the
specification window, and a full platform walkthrough on demo). Then Lesson 4 — candlesticks.

Do not place a demo trade yet: execution begins only after the risk gate (Level 15–18) is passed, and
the 90-day programme then tells you exactly which day to start
(`python main.py demo --day 1`).
