# LESSON 3 — The Exness and MetaTrader 5 Operating Guide

**Level:** 2 (Broker and platform reality)
**Estimated time:** 2 sessions of 60–75 minutes, plus the terminal walkthrough
**Prerequisites:** Lessons 1 and 2 passed — you can size a trade and you know what a spread costs.
**What you will be able to do afterwards:** open the right demo account without creating bad habits;
read an MT5 specification window correctly; choose an account type, currency and leverage with reasons
rather than by default; place and manage an order following a fixed procedure; and state exactly what
your account does when a trade goes wrong.

> **Three labels are used throughout.** Every claim carries one of them:
>
> * **[BROKER]** — an Exness-specific fact, from the official Exness Help Center, with the date read.
> * **[PLATFORM]** — a MetaTrader 5 feature (MetaQuotes' software, not Exness' rules). Verify it in your
>   own terminal, since Exness can restrict or configure what your build exposes.
> * **[GENERAL]** — a fact of arithmetic or market structure that is true at any broker.
>
> Everything marked [BROKER] was verified on **2026-09-15**. Conditions change; the date is part of the
> fact. Re-check anything before you rely on it, and remember that **your Personal Area and terminal
> override this document**.
>
> You can inspect every [BROKER] value in this project from the command line:
>
> ```bash
> python main.py broker                     # account types + margin call / stop out
> python main.py broker --account standard  # one type in detail
> python main.py broker --hmr               # higher margin requirement windows
> python main.py broker --check 2026-12-20  # how old are these figures?
> ```

---

## 1. What an Exness trading account actually is

An account is not "a broker"; it is a **type + platform + currency + leverage + server** combination.
The type decides your costs and your margin call and stop-out levels. The server decides what
instruments and conditions you see, and **[BROKER] it cannot be changed after creation** — the
documentation states the account type and server cannot be changed; if you want a different one, you
create another account. That single sentence is why this lesson exists: these are decisions you make
*before* you know whether they were right.

### The five account types, as documented [BROKER, read 2026-09-15]

| Account type | Minimum initial deposit | Spread from | Commission | Margin call | Stop out |
|---|---|---|---|---|---|
| **Standard Cent** | none stated | 0.3 pips | none | 60% | 0% |
| **Standard** | none stated | 0.2 pips | none | 60% | 0% |
| **Pro** | yes — **region based** | 0.1 pips | none | 30% | 0% |
| **Raw Spread** | yes — **region based** | 0.0 pips | up to 3.50 USD each side per lot | 30% | 0% |
| **Zero** | yes — **region based** | 0.0 pips | from 0.02 USD each side per lot | 30% | 0% |

Five things to notice, because each one is a common misunderstanding:

1. **"From X pips" is a floor, not a typical value.** It describes the best case the broker advertises.
   Your own measurements from Lesson 2's exercise are the cost you actually pay.
2. **"Region based" is not evasion — it is information.** The official page does not publish one
   minimum deposit, because the requirement depends on where you are registered. Any single number you
   read on a review site is unreliable *for you* by construction.
3. **Zero commission does not mean zero cost.** Standard accounts price everything into the spread;
   Raw Spread and Zero split the cost into a tighter spread plus a commission. Which is cheaper depends
   on your size and your actual spread (see §9).
4. **The professional accounts have a *lower* margin call level (30% vs 60%).** That sounds better and
   is not: a margin call is a warning, and a warning that arrives later is a warning that helps less.
5. **Stop out is 0% on all five types — with two documented exceptions.** [BROKER] For stocks, the
   stop-out level may rise to 100% under increased market risk; and a stop out of **20%** applies to
   clients registered via **Exness (KE) Limited** and **Exness Limited Jordan Ltd**. Confirm yours.

### What a 0% stop out means, in money

At a documented 0% stop out, **[GENERAL + BROKER]** the broker's automatic protection does not act until
equity is essentially exhausted. Computed with this project's engine, single position, no other margin
used, EURUSD entered at 1.1000:

| Position | Equity | Stop-out price at 0% | Distance | Loss |
|---|---|---|---|---|
| 0.01 lots | 250 USD | 0.85000 | 2,500 pips | 250 USD (100%) |
| 0.05 lots | 250 USD | 1.05000 | 500 pips | 250 USD (100%) |
| 1.00 lot | 250 USD | 1.09750 | 25 pips | 250 USD (100%) |

Every row ends at "100% of the account". That is what 0% means. Nothing in those rows is different in
*kind* — only in how quickly you get there. The conclusion is not "avoid 0% stop-out accounts"; it is
**your stop loss and your position size are the only limits that act before the account is gone**.

---

## 2. Which account type to use, and why

### For the demo phase (the next 90+ days)

**[BROKER]** Demo accounts are available for **every account type except Standard Cent**. So:

* Use a **Standard demo, on MT5**, with **USD** as the account currency if your entity offers it.
* Reason: Standard demo reproduces the conditions of the account you will most plausibly start live
  with, its costs are all-in-the-spread (simplest to measure), and it is the account type whose
  minimum-lot problem you can rehearse properly.
* **Do not** create an account just to look at it. One demo account, one journal, one set of numbers.

### For the eventual live account (USD 250, after readiness passes)

The honest trade-off is this:

| Option | Advantage on 250 USD | Disadvantage |
|---|---|---|
| **Standard Cent** | 0.01 cent-lots are roughly 1/100th the money value of 0.01 standard lots — it solves the minimum-lot problem from Lesson 1 | **[BROKER] No demo version exists**, so you cannot rehearse cent-lot maths on demo first; and the account is a different environment from the one you practised on |
| **Standard** | Same account type as your demo; simplest progression; all-in spread costs | 0.01 lots × a normal stop can exceed a 0.25% risk budget on a 250 USD balance (see Lesson 1's worked example) |
| **Raw Spread / Zero** | Tight spreads, commission-based | Same minimum-lot constraint as Standard, plus a different cost structure to re-measure |

**Decision rule for this course:** start live on **Standard** only if the arithmetic works for the
instrument and stop you actually trade (verify with `python main.py position`); otherwise use
**Standard Cent** for the first live phase and accept that you are trading a different account type from
your demo — and adjust the numbers, not the risk rules. Write the decision, and the reason, in your
journal before you fund anything.

---

## 3. Creating the accounts (documented steps)

**[BROKER]** The documented creation flow is:

1. Log in to your Personal Area (PA).
2. Open the **My Accounts** area and select **Open Account**.
3. Select a trading account type → **Continue**.
4. Choose **Real** or **Demo** and fill in: currency, account nickname, max leverage, platform, and
   (**Pro only**) execution type, plus a trading password (**MT4/MT5 only**).
5. Click **Create an Account**.
6. The account appears under the **Real** or **Demo** tab of My Accounts.

Documented notes worth remembering: creating trading accounts carries no fee; the account type and
server cannot be changed afterwards; demo is available for all types **except Standard Cent**.

### Credentials, and which three things you need to log in [PLATFORM]

Logging MT5 into an account needs, at minimum: the **account number**, the **trading password**, and
the **exact server name** assigned in your Personal Area. Your Personal Area password is not the
trading password. Write all three into your journal's account page (never into a public repository, and
never into a file you might commit).

### Verification and deposits [BROKER, region dependent]

Identity and address verification, payment methods and withdrawal rules are **region- and
method-specific**, and the official documentation deliberately does not publish a single global answer.
So the honest instruction is procedural, not numeric:

* Complete whatever verification your own Personal Area requires **before** you deposit anything.
* Read the deposit/withdrawal pages for *your* country of registration, on the official site.
* When you eventually go live, make your **first withdrawal early and small**. Testing the withdrawal
  path with a trivial amount is a cheap way to discover problems while the amount at risk is small.
* Never sign in through links from messages, social media or "account managers". Go to the official
  site yourself.

---

## 4. Account currency and leverage: two decisions you only make once

### Account currency [GENERAL]

Your account currency changes what conversions the arithmetic needs:

* **USD account**: EURUSD, GBPUSD, AUDUSD, NZDUSD and XAUUSD are quoted *in* USD, so the pip value is a
  clean number (10.00 USD per pip per lot for a standard FX pair, 1.00 USD per pip per lot for gold).
  USDJPY still needs a JPY→USD conversion at the current price.
* **Any other account currency**: every instrument needs an extra conversion, and the pip value moves
  with that conversion rate as well as the instrument.

Choosing a USD account (if your entity offers it — check the account-creation screen) removes one layer
of moving parts from every calculation you will do for the next year. If you cannot have USD, the engine
still works: it will **refuse** to guess a rate (`MissingRateError`) rather than silently mis-size you.

### Leverage [GENERAL — with a broker-specific detail]

**[BROKER]** Exness documents maximum leverage of **1:2000**, or **1:Unlimited** for eligible accounts,
with unlimited leverage unavailable on some instruments. Because leverage changes your *margin level*,
it changes how close a broker-side stop out is:

| Position (1.00 lot long EURUSD @1.1000, 250 USD equity) | Margin used | Margin level at entry | Stop out (0%) | Stop out (20%, if applicable) |
|---|---|---|---|---|
| at 1:100 | 1,100 USD | 23% — *the order would not open at all* | — | — |
| at 1:2000 | 55.00 USD | 455% | 1.09750 (25 pips) | 1.09761 (24 pips) |

Read that table twice:

* **At 1:100 you could not open this position** (it needs more margin than the account holds), and even
  if you could, the margin level of 23% is already below the documented 60% margin call.
* **At 1:2000 the same position opens easily** — and the 0% stop out stands **25 pips** away from entry.
  Leverage did not create risk; it removed the obstacle that would have stopped you from creating it.
* **The stop-out *level* barely matters at small size, and matters enormously at large size.** Compare
  with the 0.05-lot row in §1: at 500 pips away, the difference between a 0% and a 20% stop out is one
  pip. At 1.00 lot it is one pip *of a 25-pip budget*. The variable that moves the stop-out closer is
  **size relative to equity** — which is the one thing you control completely.

**Decision for this course:** use the broker's default or a mid-range leverage (1:100–1:500) on your
demo, keep the hard cap of **10:1 effective leverage** (notional ÷ equity) from `config/risk_profile.json`,
and treat the headline number as irrelevant to your risk. If a broker offers "unlimited", the correct
response is to calculate what that *permits* and then not do it.

---

## 5. The MT5 workspace: the five windows that matter

**[PLATFORM]** MetaTrader 5 has hundreds of settings. You need five areas, and you should learn them
properly rather than explore:

| Window | What it is for | What you do there |
|---|---|---|
| **Market Watch** (Ctrl+M) | the instrument list, live bid/ask and spread | add only your instruments; check the **Spread** column before every order |
| **Chart window** | price, timeframes, drawing tools | your level map and screenshot before each trade |
| **Toolbox → Trade** | open positions, pending orders, **Balance / Equity / Margin / Free margin / Margin level** | the numbers you must be able to read at a glance |
| **Toolbox → History** | closed trades, with comments | source of truth for journalling; export to CSV if useful |
| **Navigation + Specification dialog** | symbol specification (contract size, digits, volume min/step, swaps) | Market Watch → right-click symbol → **Specification** |

**The pip-versus-point trap [PLATFORM + GENERAL].** MT5 quotes prices and many columns in *points*;
this project defines a **pip** as 10 points for a 5-digit pair (or 10 points on a 3-digit gold quote).
When the platform's Spread column shows `12`, that may be 12 points = **1.2 pips**. This project's data
file carries the same warning: read the live Spread column and convert it yourself before assuming a
cost. If your numbers look ten times bigger or smaller than expected, you have almost certainly mixed
pips and points.

**Daily habits in the terminal [PLATFORM]:**

* Turn **one-click trading OFF** while learning. Every order should pass through the order ticket, where
  the size, stop and risk can be checked one more time.
* Set **alerts** at your levels instead of watching candles. Watching produces decisions; alerts produce
  attention.
* Do not leave the **Strategy Tester** or an EA running on a live account you do not fully understand.
  Automation you cannot audit is a risk you cannot measure.
* Keep a chart **template** with your levels and timeframes, so preparation is repeatable rather than
  improvised.

---

## 6. Placing an order: the procedure you follow every time

**[PLATFORM]** Order types available in MT5: **Market** execution, and the pending orders **Buy Limit,
Sell Limit, Buy Stop, Sell Stop, Buy Stop Limit, Sell Stop Limit**, each with optional **Stop Loss** and
**Take Profit** attached. In a hedging account there is also **Close By** (closing one position with
another). A **Trailing Stop** exists too — leaving it unused is a valid, evidence-based decision until
you have tested the alternative.

### The ten-step order procedure

1. **Setup is named and in the plan.** If it is not in `docs/handbooks/12_trading_plan.md`, stop.
2. **Levels are decided**: entry trigger price, stop price *with the structural reason*, target price
   *with the reason*.
3. **Risk is chosen**: percentage, converted to money (`equity × risk%`).
4. **Size is computed**: `python main.py position ...` — never by eye, never by feel, always rounded
   **down** to the volume step.
5. **The rule engine approves it**: `python main.py rules ... --from-journal` — APPROVED, APPROVED WITH
   WARNINGS, or NO TRADE. NO TRADE is a result, not a mistake.
6. **The order ticket is filled**: symbol → volume → order type → stop loss → take profit → **comment**.
   The comment is part of your record: use `setup_T-0007` (setup name + journal id) so the History window
   can be matched to the journal later.
7. **Screenshot before** entry, with levels marked and the ticket visible.
8. **Send**, then confirm: the position appears in Toolbox → Trade with a visible SL and TP, and the
   margin numbers match what the calculator said.
9. **Walk away.** No moving stops, no adding, no watching every tick. Set the alert and come back for the
   planned review.
10. **Journal it** (`python main.py journal add ...`) *before* looking at the next instrument. A trade
    that is not recorded did not happen, as far as your learning is concerned.

### Pending orders: when each is appropriate [GENERAL]

* **Limit** — you want a better price than current: entering on a pullback into a level you identified in
  advance. Risk: it may never fill. That is not the market "cheating" you.
* **Stop** — you want confirmation: the breakout, the structure break, the level giving way. Risk:
  slippage, and a false break that triggers you and reverses.
* **Stop-limit** — confirmation *and* price control; the cost is that a fast move can leave you unfilled.
* **[PLATFORM, verify in your terminal]** Some instruments enforce a minimum distance between the current
  price and stop/limit levels. If the platform refuses an order that seems reasonable, check the symbol
  specification and the platform's message before adjusting anything — and never "fix" it by moving a
  stop into noise.

---

## 7. Hedging: the most misunderstood button

**[BROKER]** Hedged margin is documented as **0%**, meaning a position and its opposite on the same
symbol do not require extra margin. **[GENERAL]** That is not the same as removing risk, and it is worth
being precise about why:

* Hedging **locks in** the current loss on the closed-out portion (the spread is already paid on both
  legs, and one leg carries a swap).
* You now hold **two positions** with two stops and two management decisions, at a moment when you have
  just demonstrated that your judgement about this instrument was wrong.
* Unlocking the hedge is a **new** directional decision, made under pressure, with a loss already
  realised.
* Every cost you avoided by not simply closing is replaced by two spreads plus financing.

The professional equivalent of "hedging" a losing position is **closing it** and, if the plan supports a
new trade in the other direction, taking that trade afterwards with a fresh, written justification. This
course prohibits using hedges to defer a decision. A hedge is a legitimate tool when a *plan* requires
synthetic exposure (rare for retail learners) — not when a trade goes the wrong way.

---

## 8. Higher Margin Requirements (HMR): when the platform demands more money

**[BROKER, quoted from the official Help Center, read 2026-09-15]**

* **Scheduled market breaks:** *"For most instruments, from 3 hours before a weekend close until 1 hour
  after the market reopens, margin is calculated using the instrument's maximum leverage."*
  *"Cryptocurrencies trade 24/7, so weekend HMR does not apply to them."*
* **High-impact economic news:** *"For most instruments, positions opened 15 minutes before a news
  release until 90 seconds after are limited to the instrument's maximum leverage during HMR."*
  Existing positions remain unaffected, **except for stocks**, where previously opened orders may also be
  recalculated during financial report announcements.
* **Duration:** *"The period of HMR is dependent on different instruments and events. HMR may last
  longer based on risk management decisions."*
* **How to know:** an **HMR banner** appears on the chart in the Exness Terminal and Exness Trade, and
  the **New Order window always shows the leverage that will be used** for margin calculation.

**Interpretation (not a quote).** The practical consequence for a small account is that a position which
fits comfortably on Friday morning can require several times the margin on Friday evening, and a new
order placed near a release may need more margin at the exact moment spreads widen. The arithmetic:

| 0.10 lots EURUSD @1.1000 (notional 11,000 USD) | Margin required |
|---|---|
| Leverage used for margin 1:2000 | **5.50 USD** |
| Leverage used for margin 1:200 | **55.00 USD** |

On a 250 USD account that difference (49.50 USD of free margin) is material, and it is the kind of thing
that turns a comfortable position into a margin call if you are already holding two others.

**Rule for this course:** the system's own blackout already keeps you out of the news window (no entry
30 minutes before / 15 minutes after), and the programme has you **flat before the weekend** while
learning. Read the leverage shown in the New Order window every time; it is the number that governs the
margin, not the leverage you chose when you opened the account.

---

## 9. Your broker's calculator, and this project's engine

**[BROKER]** Exness provides a **trading calculator** in the Personal Area (**Tools & Services**) and in
the Exness Trade app. It returns **margin, spread cost, commission, swap long, swap short and pip
value**, based on your account type, account currency, instrument, volume and leverage. Its own
documented caveats matter: spread cost is based on **the average spread of the previous trading day**,
and the real spread cost can only be known when a real order is opened; for instruments with **fixed
margin requirements the leverage setting is disabled**.

| | Broker calculator | This project's engine (`forex_mastery`) |
|---|---|---|
| Authority on that broker's conditions | **yes** | no — it carries a dated snapshot |
| Live spread | last day's average | you supply it; it refuses to guess |
| Conversion rate for pip value | broker's live rate | **refuses to run without one** (`MissingRateError`) |
| Below-minimum-lot size | describes it | **hard error, with the alternatives spelled out** |
| Reproducible offline / auditable | no | yes — pure functions, unit-tested |
| Works with no account, no login, no internet | no | yes |

**How to use both.** Use the broker calculator to sanity-check a specific order's margin and costs under
that broker's current conditions; use this engine for the planning arithmetic (risk, R, expectancy,
drawdown), for the journal, and for anything you want to be able to reproduce in six months. **When the
two disagree, treat it as a finding, not an inconvenience** — record both numbers, work out which input
differed (spread, conversion rate, leverage, contract size), and write the answer in your journal. That
single habit is what separates an operator from a gambler.

---

## 10. Trading volume: what the platform means by "size"

**[BROKER]** *"Trading volume is always calculated in base currency"* and is given by:

```
trading volume (TV) = number of lots × contract size
```

Documented examples: 3 lots EURUSD → 3 × 100,000 = **300,000 EUR**; 3 lots UKOIL → 3 × 1,000 = **3,000 BBL**.
Your own:

| Order | TV |
|---|---|
| 0.02 lots EURUSD | 2,000 EUR |
| 0.35 lots XAUUSD | 35 troy ounces |
| 0.50 lots UKOIL | 500 barrels |

**Why this matters [GENERAL]:** TV is the *size* of the position, and it is the number from which margin
and pip value are derived. It is **not** your risk. Your risk is `stop distance × pip value × lots` — a
0.35-lot gold position with a 30-pip stop is a very different risk from the same position with a 300-pip
stop. Confusing TV with risk is how traders conclude that "a small position" is a safe one.

---

## 11. Operational habits that prevent most account-level accidents

1. **One demo account, one journal, one plan.** Multiple accounts fragment your data and your attention.
2. **Record your account conditions** in the journal *today* (type, currency, leverage, margin call, stop
   out, entity) with the date — and re-verify quarterly. Conditions are a snapshot.
3. **Read the New Order window every time**: it shows the leverage actually used for margin. During HMR
   it will differ from what you expect.
4. **Never trade an instrument you have not checked in the Specification dialog** (contract size,
   volume min/step, swaps). `python main.py specs` shows what this project believes; the terminal is the
   authority.
5. **Turn off notifications that invite action** (push alerts about big moves, "top gainers"), and ignore
   anyone who contacts you offering signals, account management or "guaranteed" returns. **[GENERAL]**
   Those are the recruiting channels of every retail loss pattern in this course.
6. **Keep the platform boring.** No EAs you did not write or fully understand, no indicators you cannot
   explain, no extra windows.
7. **If something is unavailable and you do not know why**, read the platform's error message and the
   broker's help article before changing your order. "It wouldn't let me" is a reason to slow down, not a
   reason to try a different size.

---

## 12. Exercises

1. **Account conditions.** From `python main.py broker`, list the margin call and stop-out level for each
   of the five account types, and write one sentence on why the professional accounts' *lower* margin call
   percentage is not an advantage.
2. **Stop-out distance.** For 0.05 lots long EURUSD at 1.1000 with 250 USD equity, compute the 0% stop-out
   price and the distance in pips. Then state, in one sentence, what would happen to that distance if you
   traded 0.5 lots instead (you may verify with the engine).
3. **Margin and HMR.** Compute the margin required for 0.10 lots EURUSD at 1.1000 using 1:2000 and 1:200.
   State the difference in free margin on a 250 USD account, and one practical rule that avoids living
   through that difference.
4. **Cost comparison (illustrative).** Using *your own* measured spreads from Lesson 2, compare a
   Standard-style account (spread only) with a Raw Spread-style account (tighter spread + 3.50 USD per
   side per lot) for **0.01 lots** with a **30-pip stop**. Report both as a cost in R. State which you
   would use and why — and what would change your answer.
5. **Trading volume.** Compute the TV in base currency for: 0.02 lots EURUSD; 0.35 lots XAUUSD; 0.50 lots
   UKOIL. Then explain in one sentence why TV is not risk.
6. **Specification search.** In MT5, find and record for EURUSD and XAUUSD: contract size, digits, volume
   min, volume step, swap long, swap short, and any minimum stop distance the platform enforces. Write the
   date and the source ("MT5 Specification dialog, my demo account").
7. **The ten-step procedure.** Write your own version of §6's order procedure in your journal, and time
   yourself doing steps 1–6 for a *hypothetical* trade (no order sent). Target: under five minutes.
8. **Hedge reasoning.** In under 100 words, explain why "hedging" a losing position is usually a decision
   to *avoid* deciding — and what the professional equivalent is.
9. **Pip-versus-point.** Your platform's Market Watch shows a spread of `14` on a 5-digit pair. What is
   that in pips, and what is the cost in USD for 0.02 lots?
10. **Readiness gate.** Run `python main.py readiness --criteria` and list the criteria that concern
    *broker and platform operation*. Explain why "journal complete" and "costs understood" are on the
    same list as statistical criteria.

---

## 13. Short test (answers hidden)

1. Name the five documented account types and the two whose minimum initial deposit is *not* region based.
2. Which account type has **no demo version**, and why does that matter for this course?
3. What are the documented margin call and stop-out levels for Standard, and what are they for Pro?
4. State two documented exceptions to the 0% stop out, and explain why you must check yours.
5. What exactly happens to a single losing position on an account with a documented 0% stop out?
6. Which is unchangeable after creation: the account type, the leverage, the account currency, or the
   server? (More than one may be correct — say which.)
7. What does "HMR" mean, and what are the documented weekend and news windows?
8. During HMR, which number in the terminal tells you the leverage actually being used for margin?
9. Give the definition and formula for trading volume, and one example of your own.
10. Name two documented caveats of the broker's own trading calculator, and one thing this project's
    engine does that the broker calculator does not.

**Pass standard:** 8 of 10, with exercises 2, 3 and 5 correct. If you cannot do exercise 3 without the
engine, redo Lesson 2 §5 before continuing — margin arithmetic is not optional.

---

## 14. Deliverable for this lesson

Add an **account page** to your journal containing:

1. Account type, platform, account currency, leverage chosen — with a one-line reason for each.
2. Documented margin call and stop-out levels **for your entity and account type**, with the date and
   the source.
3. Your recorded instrument specifications for EURUSD and XAUUSD (contract size, digits, volume min/step,
   swaps, minimum stop distance) from your own terminal.
4. Your own cost-in-R table from Lesson 2, updated with the account type you actually chose.
5. The date you will re-verify all of it (put it in your calendar: quarterly).

Then:

```bash
python main.py broker --account standard --hmr
python main.py broker --check 2026-09-15
python main.py specs --symbol EURUSD
python main.py position --symbol EURUSD --balance 250 --risk 0.25 --entry 1.1000 --stop 1.0975
python main.py quiz --category market_mechanics --n 8 --interactive
python main.py quiz --category beginner --n 8 --interactive
```

**Next:** Lesson 4 — candlesticks and price representation: reading a candle as information rather than
as a symbol to memorise, with the honest hit-rate exercise that follows (find twenty signals, record every
outcome, including the failures).

**Reminder before you go:** nothing in this lesson is a recommendation to open, fund or trade an account.
The demo account is for rehearsal; live capital comes only after the readiness criteria pass — 14 hard
conditions, deliberately, each corresponding to a documented way small accounts are destroyed.
