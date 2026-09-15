# LESSON 1 — What Forex Is, How Money Is Really Made and Lost, and the Two Numbers That Decide Everything

**Level:** 0–1 (Foundations, Market Mechanics)
**Estimated time:** 2 sessions of 60–75 minutes, plus the exercises
**Prerequisites:** none. This is written for someone who has never placed a trade.
**What you will be able to do afterwards:** read any FX quote correctly, state what a pip is worth on
any instrument in your account currency, explain why leverage is not the same thing as risk, and
describe how a trader can be right about direction and still lose money.

> **Lesson rule.** From here on, every number you write must come with its unit and its assumption,
> and every claim about the future must be labelled **SCENARIO**. There are no exceptions, because
> the habit of precision is the actual subject of this course.

---

## 1. What the foreign exchange market actually is

A currency has no absolute value. It only has value *relative to another currency*. When we "trade
forex", we are not buying a thing and storing it; we are exchanging a claim on one economy for a claim
on another, at a price that changes continuously.

The price of EURUSD — say 1.1000 — is a **ratio**, and every ratio needs both parts named:

* **Base currency** (first): EUR. What you are buying or selling.
* **Quote currency** (second): USD. What you are paying with, and what the price is expressed in.
* **EURUSD = 1.1000 means:** one euro costs 1.1000 US dollars.

If that number rises to 1.1050, the euro strengthened *against the dollar*. Note carefully: it does
not necessarily mean the euro strengthened against anything else. USDJPY could have moved at the same
time. There is no such thing as "the euro went up" in isolation — only "relative to a specific
another".

**Who is on the other side of your trade**

The FX market is decentralised: a network of banks, brokers, funds, corporates and other traders.
Participants have different motives, which is why the market is not a single "them":

| Participant | Typical motive | What this means for you |
|---|---|---|
| Banks / market makers | client flow, inventory, hedging | they set the prices you trade at, including the spread |
| Corporates | paying/hedging real business obligations | their flow is price-insensitive in the short run |
| Funds / institutions | macro positioning, risk premia | they move size, but on slow horizons |
| Central banks | policy, intervention | the single largest regime-setters for FX |
| Retail traders | speculation | a small share of volume, and usually the weakest information |
| **Your broker** | earns from spread, commission, swap, and client losses at some venues | your broker is a business partner and a counterparty at the same time |

That last row deserves honesty: depending on the entity and execution model, your broker may hedge your
order in the market or take the other side of it internally. This does not make the broker your enemy,
but it does mean you should understand your execution model (Lesson 3) rather than assume it.

**FACT vs INTERPRETATION.** "EURUSD traded at 1.1000 at 14:00 UTC" is a fact if it is sourced and
timestamped. "The euro is strong because the ECB sounded hawkish" is an interpretation — a reasonable
one, but an interpretation, and it can be wrong even when the price move is real.

---

## 2. How money is actually made and lost here

Most beginners believe the game is prediction: "will price go up or down?" That is only one of three
questions, and it is the least controllable:

1. **Direction** — where price goes (a coin-flip in the short run for most people).
2. **Distance** — how far it goes before it comes back (decides your reward).
3. **Size** — how much money that distance is worth (fully under your control).

Professionals accept that (1) is uncertain and spend their effort on (2) and (3). Beginners obsess over
(1) and leave (3) to chance — which is exactly the wrong way round, because **size is the only one of
the three you control completely.**

### The honest arithmetic of a losing trader

Suppose you have 250 USD and you "risk about 10%" per trade (that is 25 USD — a number that feels
abstract until you see it in a table):

| Consecutive losses | Equity left (approximately) |
|---|---|
| 0 | 250.00 |
| 3 | 182.25 |
| 5 | 147.62 |
| 10 | 87.16 |
| 20 | 30.39 |
| 30 | 10.60 |

And the recovery arithmetic is worse than it looks:

| Drawdown | Gain required on the *remaining* equity |
|---|---|
| −10% | +11.1% |
| −20% | +25.0% |
| −30% | +42.9% |
| −50% | +100.0% |
| −70% | +233.3% |

This asymmetry — small losses are cheap, big losses are brutal — is the entire argument for risking
0.10–0.25% per trade while learning, and no more than 1% ever. You can verify every row with:

```bash
python main.py drawdown --balance 250
```

### The three ways a trader loses money while being "right"

1. **Size too large.** The idea was correct; the stop was hit on the way; the account is now too small
   to take the next, better opportunity.
2. **Costs ignored.** A 2-pip spread on a 20-pip stop is 0.1R paid immediately. Trade enough and you
   are paying a rent that your edge must beat before you make anything.
3. **Management by emotion.** Moving a stop "just this once", adding to a loser, closing a winner too
   early. Each is a size decision made badly, at the worst possible moment.

None of these are market problems. All three are process problems, which is good news: process is
learnable.

---

## 3. Pips: the unit of distance

A **pip** is the standard unit of price movement. For most pairs, 1 pip = 0.0001 (the fourth decimal).
For JPY pairs it is 0.01 (the second decimal). Metals like gold (XAUUSD) use 0.01.

Your platform will also show **points** (also called pipettes): 1 pip = 10 points.

> **Verify on your own platform.** Symbol specifications (digits, contract size, minimum volume) are
> broker- and instrument-specific. The numbers in this project were checked against official Exness
> documentation on 2026-09-15 and are marked verified, but **the specification in your MT5 terminal
> always wins** — confirm it in MT5 → Market Watch → right-click the symbol → Specification.

### The pip-value formula

```
pip value = lots × contract size × pip size × (quote currency → account currency rate)
```

For a USD account trading a pair quoted *in* USD (EURUSD, GBPUSD, AUDUSD, XAUUSD), the conversion is
1.0, so the numbers are simple:

| Instrument | Contract size | Pip size | Pip value per 1.00 lot | Pip value per 0.01 lot |
|---|---|---|---|---|
| EURUSD | 100,000 | 0.0001 | **10.00 USD** | 0.10 USD |
| GBPUSD | 100,000 | 0.0001 | 10.00 USD | 0.10 USD |
| XAUUSD (gold) | 100 oz | 0.01 | **1.00 USD** | 0.01 USD |
| USDJPY | 100,000 | 0.01 | ≈ 6.67 USD at 150.00 | ≈ 0.067 USD |

For USDJPY the pip value depends on the current price, because the profit is earned in JPY and must be
converted back to USD: `100,000 × 0.01 ÷ 150.00 = 6.6667 USD`.

**Worked example (do this by hand today).**

You have 250 USD. You want to risk 0.25% on EURUSD with a 50-pip stop.

1. Risk in money: `250 × 0.25% = 0.625 USD`
2. Risk per 1.00 lot: `50 pips × 10.00 USD = 500 USD`
3. Lots: `0.625 ÷ 500 = 0.00125 lots`

0.00125 lots is below the broker minimum of 0.01 lots. **This is not a rounding problem — it is the
central practical constraint of a small account**, and it has exactly four honest answers: skip the
trade, use a Standard Cent account (where 0.01 cent-lots are 1/100th the size), trade an instrument
with a smaller money-per-pip value, or knowingly accept a larger percentage after recalculating how
many such losses reach your drawdown limit. What you must *not* do is move the stop closer to make the
arithmetic work — that changes the trade to fit the size instead of the size to fit the trade.

```bash
python main.py position --symbol EURUSD --balance 250 --risk 0.25 \
    --entry 1.1000 --stop 1.0950 --take-profit 1.1100 --leverage 100
```

Read the output carefully. It shows the pip value, the exact size, the minimum-lot problem, and the
alternative. The tool does not hide bad news; that is its main feature.

---

## 4. Lots, leverage and margin — three different things

These are the most conflated ideas in retail trading. Separate them now and the rest of the course
becomes easier.

| Concept | What it is | What it changes | What it does NOT change |
|---|---|---|---|
| **Lot size** | the quantity you trade | money per pip, therefore risk | direction |
| **Leverage** | broker-provided borrowing capacity (1:100, 1:2000 ...) | **margin required** to open | your risk per trade |
| **Margin** | the deposit locked while a position is open | how much free margin you have | your maximum loss |

**Margin is not risk.** 0.01 lots of EURUSD at 1.1000 is 1,100 USD of notional: at 1:100 that locks
about 11.00 USD of margin, at 1:1000 about 1.10 USD. Your *risk* is unchanged in both cases — it is
still determined by your stop distance and your size, and nothing else. Leverage lets you open a position that
is too big; it never forces you to. That is why this system uses **effective leverage** as a portfolio
sanity check (notional ÷ equity) rather than the broker's headline number.

Two numbers you must know before any trade:

* **Notional value** — what the position is "worth" in the market: `lots × contract size × price`.
  0.01 lots of EURUSD at 1.1000 is 1,100 USD of notional against a 250 USD account — 4.4:1 effective
  leverage. Harmless *if* the stop is 50 pips (risk 0.50 USD) and catastrophic if it is 5,000 pips
  (risk 50 USD, 20% of the account).
* **Margin level** = equity ÷ used margin, expressed as a percentage. When it falls far enough, the
  broker stops you out (Exness: margin call 60%, stop out 0% on Standard accounts — a 0% stop out is a
  real risk control, but it is not a substitute for your own limits, and 0% means the account can lose
  everything it holds in margin before positions close).

**The honest summary:** leverage is a facility, risk is a choice, and only one of them has ever blown
up an account.

---

## 5. R: the only unit that lets you compare trades

A trade's result measured in money is not informative, because the size varies. Measured in **R**, it is:

```
R = profit or loss ÷ the amount you planned to risk
```

* You risked 0.625 USD and lost 0.625 USD → **−1.0R**.
* You risked 0.60 USD and made 1.20 USD → **+2.0R**.
* You risked 1.00 USD and made nothing → **0.0R**.

R-multiples are the language of process:
52 trades at +2.0R and −1.0R can be summed, averaged and compared regardless of size or instrument. It
is also how the analytics layer checks whether your results mean anything (Lesson 17 covers confidence
intervals):

```bash
python main.py report --journal outputs/demo_journal.csv
```

That command will show you, on fabricated practice data, how a small winning sample can still have a
confidence interval that includes zero — meaning **no demonstrated edge** — even while the equity curve
looks pleasant. That single experience is worth more than any win-rate claim you will ever read.

---

## 6. Putting it together: what a competent decision looks like

Before any trade, you must be able to say all of the following out loud, in this order:

1. **Setup name** (from your written plan) and the market condition it requires.
2. **Entry trigger** — an objective event, not a feeling.
3. **Stop** — the price at which your idea is *wrong*, and the structural reason for that price.
4. **Risk** — a percentage, decided before entry, converted into money.
5. **Size** — calculated from stop distance and risk, rounded *down* to the volume step.
6. **Target** — where price should go if your reading is right, and why.
7. **Invalidation** — the condition that ends the idea, even without the stop being hit.
8. **Correlation** — which other positions express the same idea.
9. **Costs** — spread, commission, swap, in money and in R.
10. **State check** — are you tired, angry, euphoric, rushed, or trying to win something back?

If any of the ten is missing, the correct outcome is **NO TRADE**, and the rule engine enforces that
by treating missing data as a failed check:

```bash
python main.py rules --symbol EURUSD --direction long --risk 0.25 --rr 2.0 \
    --session London --stop-pips 45 --atr 60 --spread 1.1 --news-in 240 \
    --htf-bias bullish --emotional-state calm --checklist --from-plan --screenshot \
    --structure-clear --level-defined --invalidation-defined --trigger-defined \
    --setups trend_pullback --from-journal
```

---

## 7. Exercises (do these before the test)

**Exercise 1.** EURUSD is 1.1000/1.1002. You buy at market. (a) What did the spread cost you in pips?
(b) In USD, for 0.10 lots? (c) In R, if your stop is 20 pips away?

**Exercise 2.** Compute the pip value for 0.05 lots of USDJPY when USDJPY is 150.00, in USD. Show the
arithmetic.

**Exercise 3.** You have 250 USD. You want to risk 0.25% with a 25-pip stop on EURUSD. Compute the
exact lot size. Then state, in one sentence, what you will actually do about the minimum lot of 0.01.

**Exercise 4.** You have 500 USD and risk 1% per trade. How many consecutive losses take you to
approximately −10%? (Use compounding, not naive division.) What gain do you then need to get back to
500 USD?

**Exercise 5.** Explain, in your own words and without using the word "leverage" more than once, why
using 1:2000 leverage does not by itself increase your risk per trade.

**Exercise 6.** Write one sentence of each type about EURUSD: a **FACT**, an **INTERPRETATION**, a
**SCENARIO** and a **SPECULATION**. Label them clearly.

---

## 8. Short test (answers hidden)

Answer without any tool first. Then check with the tools, then ask for the answer key.

1. In EURUSD, which is the base currency and what does the price represent?
2. What is a pip on EURUSD, and what is it on USDJPY?
3. What is the pip value of 0.10 lots of EURUSD in USD?
4. What is the pip value of 0.10 lots of XAUUSD in USD?
5. You risk 0.25% of a 250 USD account. How much money is that, to the cent?
6. Your stop is 40 pips away and the instrument's pip value is 1.00 USD per lot. How many lots should
   you trade if you are risking 1.00 USD? What will you do if the broker's minimum is 0.01 lots?
7. Why is a 50% drawdown not recovered by a 50% gain?
8. A trader wins 70% of trades but loses money over 100 trades. Give two different mechanisms that
   could cause this, and state which one is a size problem.
9. State one thing leverage changes and one thing it does not change.
10. You are right about direction, but the trade is stopped out. Name three process failures that
    could have produced that result.

**Pass standard:** 8 of 10 correct, with the arithmetic written out. Below that, re-read sections 3–5
and redo Exercises 1–4 before moving on. This gate exists because everything later assumes you can do
this arithmetic without thinking.

---

## 9. Deliverable for this lesson

Write, in your journal, the following (it becomes the first entry of your trading record):

1. Your founding note: why you are doing this, how much money you can lose without it changing your
   life, and how many hours per week you will commit.
2. Your maximum risk per trade, in percent and in money on a 250 USD account, with the reason.
3. The two calculations from Exercise 3, written out longhand, including the minimum-lot decision.

Then run:

```bash
python main.py quiz --category beginner --n 8 --interactive
python main.py progress
```

Answers are hidden during the test; explanations are shown only afterwards. Do not open the answer key
(`docs/lessons/01_what_is_forex_answer_key.md`) until you have committed to your answers — a test you
peek at teaches nothing.

**Next:** Lesson 2 (market mechanics in depth: orders, execution, spreads, swaps and stop-out) — only
after this lesson's test is passed.
