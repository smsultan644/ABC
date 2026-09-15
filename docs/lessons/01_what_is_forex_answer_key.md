# ANSWER KEY — LESSON 1

> **Do not read this until you have written your answers down.** A test you peek at teaches nothing.
> Every number below was produced by the calculation engine in `forex_mastery/core/` and is pinned by
> the unit tests, so you can reproduce all of it yourself:
>
> ```bash
> python main.py pip --symbol EURUSD --lots 0.1
> python main.py pip --symbol USDJPY --lots 0.05 --price USDJPY=150.0
> python main.py position --symbol EURUSD --balance 250 --risk 0.25 --entry 1.1000 --stop 1.0950
> python main.py drawdown --balance 500
> ```

---

## Exercise answers

**Exercise 1 — spread cost.**
(a) The market quotes 1.1000/1.1002: the spread is **2 pips** (0.0002 ÷ 0.0001).
(b) 0.10 lots of EURUSD = 1.00 USD per pip → **2.00 USD** paid on entry, before the market moves.
(c) With a 20-pip stop, 2 pips = **0.1R**. You begin every trade 0.1R behind. This is why cost per R
must be known for your typical trade (Level 18).

**Exercise 2 — USDJPY pip value.**
Contract 100,000; pip size 0.01 → `100,000 × 0.01 = 1,000 JPY` per pip per lot. For 0.05 lots:
`50 JPY` per pip. Convert to USD at 150.00: `50 ÷ 150 = 0.3333 USD` per pip. The engine reproduces
this: `pip_value_per_lot("USDJPY", "USD", lots=0.05, prices={"USDJPY": 150.0}) == 0.33333…`
Note the trap: the pip value of a JPY pair **changes as the price changes**.

**Exercise 3 — sizing on a small account.**
Risk: `250 × 0.25% = 0.625 USD`. Risk per 1.00 lot: `25 pips × 10.00 USD = 250 USD`.
Lots: `0.625 ÷ 250 = 0.0025` → **below the 0.01 minimum**.
What to actually do (any of these, honestly stated): skip the trade; use a Standard Cent account where
0.01 cent-lots are 1/100th the size; trade an instrument with lower money-per-pip; or knowingly accept
a larger percentage (0.01 lots would risk 2.50 USD = 1.00% of the account) *after* recalculating the
drawdown ladder at 1% (≈ 11 losses to −10%, 69 to −50% at 1% risk). What you must not do: move the stop
closer, or size up and call it 0.25% risk.

**Exercise 4 — drawdown by compounding.**
`n = ceil(ln(0.90) ÷ ln(0.99)) = ceil(10.48) = 11` consecutive 1% losses to reach about −10%
(exactly −10.47% after 11 losses). Recovery: **+11.1%** required on the remaining 447.61 USD.
The engine's ladder confirms: at 1.00% risk, 11 losses to −10%, 69 to −50%.

**Exercise 5 — leverage and risk.**
Leverage only changes how much margin is locked while the position is open. Risk per trade is
`stop distance × pip value × lots`; the broker's leverage figure appears nowhere in that product. Two
traders using 1:2000 and 1:100 with the same 0.01 lots and the same 50-pip stop risk exactly the same
money; the 1:2000 account merely needs less margin to hold the position. Leverage becomes dangerous
only because it *allows* a position size that the risk formula would otherwise make impossible.

**Exercise 6 — the four statement types (examples; yours will differ).**
* **FACT:** "EURUSD closed at 1.1042 on 2026-09-12 at 21:00 UTC, per my platform's H1 data."
* **INTERPRETATION:** "The euro has been supported by expectations that the ECB will not cut before
  December."
* **SCENARIO:** "If H4 closes above 1.1060 and holds, the next reference level is 1.1120."
* **SPECULATION:** "EURUSD will be above 1.15 by year-end." (No basis, no conditions, no falsification.)

---

## Test answers

1. **Base = EUR** (the currency being bought/sold). The price 1.1000 is how many **US dollars (the
   quote currency)** one euro costs.
2. Pip on EURUSD = **0.0001** (fourth decimal, 10 points). On USDJPY = **0.01** (second decimal).
3. 0.10 lots EURUSD = `0.10 × 100,000 × 0.0001 = 1.00 USD` per pip. **1.00 USD.**
4. 0.10 lots XAUUSD = `0.10 × 100 oz × 0.01 = 0.10 USD` per pip. **0.10 USD** — gold's pip is 1/100th
   the money value of a FX pip per lot, even though gold usually moves more pips per day.
5. `250 × 0.0025 = 0.625 USD` = **0.63 USD** (62.5 cents).
6. Risk per 1.00 lot = `40 pips × 1.00 USD = 40 USD`. Lots = `1.00 ÷ 40 = 0.025`. Rounded **down** to
   the 0.01 volume step you trade **0.02 lots**, which risks 0.80 USD (0.32% of a 250 USD account).
   Rounding up to 0.03 would risk 1.20 USD — 20% more than planned. Always round down.
7. A 50% loss leaves 50% of the original. To return to the original level you must **double** what
   remains, which is a **+100%** gain. Drawdowns destroy capital *and* the base on which recovery is
   earned — hence the asymmetry table.
8. Two mechanisms from: (a) **payoff asymmetry** — winners smaller than losers (e.g. +0.5R wins vs
   −2R losses) — this is a **size/stop-and-target problem**; (b) **costs** — spread, commission and
   swap consuming the gross edge; (c) **one catastrophic outlier** — a single oversized loss erasing
   many small wins (risk-discipline failure). The payoff asymmetry (a) is the size problem.
9. Leverage **changes** the margin required (buying power). It does **not change** your risk per trade
   or the direction of the market.
10. Three from: the size was too large for the stop; the stop was placed inside normal noise rather
    than at a structural invalidation; entry was taken before the trigger, worsening the R:R; the stop
    was moved or removed mid-trade; the trade was taken outside the plan's permitted conditions
    (session, news window, volatility band).

---

## What the test is really measuring

Questions 3–7 measure arithmetic. Questions 8–10 measure whether you have separated **market
uncertainty** (unavoidable) from **process failure** (avoidable). If you got the arithmetic right but
described the losing case in question 8 as "bad luck", the answer is incomplete: bad luck is real, but
it is not a mechanism you can fix, and this course only spends time on the things you can fix.
