# BEGINNER FOREX GUIDE

*Chapter 2 of the Forex Mastery Handbook. Assumes Lesson 1 has been completed and its test passed.*

This chapter is written for someone who has never placed a trade and does not intend to place one for
weeks. Its purpose is to make the market's mechanics boringly familiar, so that later lessons can be
about decisions rather than about vocabulary.

---

## 1. The market you are joining

Foreign exchange is the exchange of one currency for another. There is no central exchange and no
single price: prices come from a network of banks and liquidity providers, and what you see on your
platform is the price your broker is willing to trade with you at.

**Key consequence:** the price you see includes your broker's spread, and it can differ from another
broker's price, another platform's data feed, and the "official" rate you find on a news site. When
learning, always use **one** price source consistently (your own terminal) so your comparisons are
meaningful.

### Opening hours

The market is open continuously from Sunday ~21:00 UTC to Friday ~21:00 UTC, but it is not equally
alive the whole time:

| Session | Local hours | Character |
|---|---|---|
| Sydney | 08:00–17:00 Australia/Sydney | thin, ranges, gap risks around the open |
| Tokyo | 09:00–18:00 Asia/Tokyo | orderly ranges in JPY and AUD pairs, then a lull |
| London | 08:00–17:00 Europe/London | highest FX volume, strong trends, biggest ranges |
| New York | 08:00–17:00 America/New_York | US data, dollar moves, overlap with London |
| Overlap (London–New York) | ~12:00–16:00 UTC in summer | most liquid window; also the fastest reversals |
| Lull | ~21:00–00:00 UTC | thin spreads widen, false moves, avoid while learning |

Daylight saving changes these windows twice a year — the exact UTC times are computed for you:

```bash
python main.py sessions --tz <Your/Timezone> --explain
```

---

## 2. The instruments you will actually consider

You do not need eight instruments. You need one or two that you understand deeply.

| Instrument | What it is | Beginner suitability |
|---|---|---|
| EURUSD | euro vs US dollar | the most liquid pair; tightest spreads; the standard learning instrument |
| GBPUSD | pound vs dollar | similar profile, generally more volatile |
| USDJPY | dollar vs yen | trend-friendly, sensitive to US yields |
| AUDUSD, NZDUSD, USDCAD, USDCHF | commodity/risk-linked crosses | fine later; each has its own driver |
| XAUUSD (gold) | metal, not a currency | high volatility per pip; common beginner killer because "it looks cheap" |
| Exotics (USDTRY, USDZAR, ...) | thin markets | wide spreads, gaps, unsuitable for learning |
| Crypto CFDs, indices, oil | other asset classes | outside this course's scope |

**Rule for the first 90 days:** EURUSD, and nothing else, until Level 15 (position sizing) is passed —
then at most two more from {GBPUSD, USDJPY, AUDUSD} and, only if you can size it correctly, XAUUSD.

---

## 3. What you are actually trading: contracts, not currencies

Retail FX is traded in **contracts (lots)**:

| Lot | Base currency units | Pip value on EURUSD (USD account) |
|---|---|---|
| 1.00 standard lot | 100,000 | 10.00 USD |
| 0.10 mini lot | 10,000 | 1.00 USD |
| 0.01 micro lot | 1,000 | 0.10 USD |
| Cent-account 0.01 | 1,000 (but priced in cents) | 0.001 USD equivalent |

You own no euros and no dollars. A long EURUSD position is a *contract* whose value changes with the
price ratio. There is no delivery for retail CFD/spot accounts; positions are opened and closed for the
difference. Costs: spread on entry/exit, commission if your account charges it, and swap if a position
is held overnight (triple swap on Wednesdays for most pairs — Thursday for USDCAD).

---

## 4. Order types you must know

| Order | Meaning | When it is right |
|---|---|---|
| Market | execute now at the best available price | when the trigger has already occurred |
| Limit | execute only at your price or better | entering into a level rather than chasing it |
| Stop (buy/sell stop) | becomes a market order when price touches a level | breakout entries; also used for stop losses |
| Stop loss | closes your position to cap the loss | **always attached, before or with entry** |
| Take profit | closes the position at a target | when the target is structural, not arbitrary |
| Trailing stop | stop follows price at a fixed distance | only with a tested rule; it usually lowers expectancy if moved by feel |

**Non-negotiable:** a stop loss is decided *before* entry, sized from structure, and never widened.
If you cannot name the price that proves your idea wrong, you do not have a trade — you have a
position.

---

## 5. Margin, leverage, stop out — in plain language

* **Margin** is a deposit the broker holds while your position is open. It is returned when the
  position closes. It is not a fee and it is not your risk.
* **Leverage** (1:100, 1:2000, "unlimited") determines how much notional you can control per unit of
  margin. Higher leverage needs less margin. It does not change how much you can lose on a given stop.
* **Free margin** = equity − used margin. This is what is available for new positions.
* **Margin level** = equity ÷ used margin. Brokers act when it falls far enough: a **margin call**
  warns, and a **stop out** forcibly closes positions. Exness documents margin call 60% / stop out 0%
  for Standard accounts (verified 2026-09-15; **confirm the current figures for your own account type
  and entity in official Exness documentation**).
* **A 0% stop out is not safety.** It means the broker may not close your positions until the account
  has lost essentially everything committed in margin. Your own stop loss and your own risk limit are
  the only protections under your control.
* **Negative balance protection** means you cannot owe the broker money on a retail account. It does
  not mean you cannot lose what you deposited.

```bash
python main.py position --symbol EURUSD --balance 250 --risk 0.25 \
    --entry 1.1000 --stop 1.0950 --leverage 100
```

The output deliberately shows the **effective leverage** (notional ÷ equity). A 0.01-lot EURUSD
position is 1,100 USD of notional; against 250 USD equity that is 4.4:1 — fine for a 50-pip stop,
catastrophic for a stop measured in thousands of pips. Effective leverage is the honest measure; the
broker's headline number is not.

---

## 6. The four ways beginners lose

1. **Size.** Not "bad analysis" — nearly always size. The formula is in Lesson 1; a calculator is in
   this repository. Use it every single time, even when the answer is obvious.
2. **No stop, or a stop that is moved.** A stop that can be moved is not a stop; it is a suggestion.
   In this system you write the invalidation price down *before* entry, and the rule engine refuses
   setups without one.
3. **Costs and overtrading.** Eight trades a day on a 250 USD account at a 2-pip spread is a fee
   stream, not a strategy. Maximum two trades per day while learning, and only in your permitted
   session windows.
4. **Recovery behaviour.** After a loss, the urge to "get it back" produces larger size, earlier
   entries and wider stops — the exact opposite of what the arithmetic requires. The defence is
   mechanical: after two consecutive losses, a one-hour break is mandatory.

Notice that none of the four is a market event. All four are decisions you can automate away with
rules, checklists and logs — which is what the rest of this system is for.

---

## 7. Your first two weeks (do not trade)

| Day | Task | Output |
|---|---|---|
| 1 | Read Lesson 1 and this chapter; write your founding note | journal entries 1–3 |
| 2 | Install/verify MT5, find the specification of 4 instruments, record spread/swap/margin | Level 2 specification table |
| 3 | Pip-value drills: 10 instruments × 2 lot sizes, by hand, then verified | arithmetic sheet |
| 4 | Position sizing drills: 10 scenarios, including two that must be refused | arithmetic sheet |
| 5 | R-multiple drills; compute break-even win rate at 1:1, 1:2, 1:3 | arithmetic sheet |
| 6 | Drawdown ladder and recovery table at 0.25% and 1% risk | Level 16 worksheet |
| 7 | Quiz: `python main.py quiz --category beginner --n 10 --interactive` | ≥ 80% to proceed |
| 8–14 | Chart literacy begins (Levels 4–8): classify 20 charts, mark levels with reasons | chart workbook |

Only after the risk gate (Level 18) is passed do you place your first demo trade. That is not
conservative to the point of being useless: it is the shortest path that does not require you to
unlearn a habit later.

---

## 8. Vocabulary to be able to define without notes

pip · point/pipette · spread · bid · ask · lot · contract size · notional · margin · free margin ·
margin level · margin call · stop out · leverage · effective leverage · swap · commission · slippage ·
long · short · stop loss · take profit · trailing stop · R-multiple · expectancy · win rate ·
break-even win rate · payoff ratio · profit factor · drawdown · recovery gain · risk of ruin ·
portfolio heat · correlation · volatility · ATR · support · resistance · higher high · lower low ·
trend · range · transition · session · overlap · lull · news blackout window.

If any word on that list cannot be explained in one sentence, that is your next study task. This file
deliberately does not define them all for you: looking them up, writing them down, and then
cross-checking against this repository's engine is part of the learning.

---

## 9. What is *not* in this chapter, on purpose

* No signal service, no "best indicator", no entry rules.
* No profit projections. Any table of future returns you are shown, including by this software, is an
  assumption dressed as arithmetic.
* No claim that discipline guarantees success. Discipline prevents *avoidable* losses; it does not
  create an edge. An edge must be found, measured and maintained separately — Levels 19–23.
* No encouragement to go live sooner. The readiness criteria in `python main.py readiness --criteria`
  are strict for a reason: 14 hard conditions, every one of which corresponds to a documented way
  small accounts are destroyed.
