# ANSWER KEY — LESSON 2

> **Do not read this until you have written your own answers.** Every number below was produced by the
> calculation engine in `forex_mastery/core/` and is pinned by the tests. Reproduce any of them with:
>
> ```bash
> python main.py pip --symbol GBPUSD --lots 0.05
> python main.py position --symbol EURUSD --balance 1000 --risk 1 \
>     --entry 1.1000 --stop 1.0970 --take-profit 1.1060 --spread 2.0
> python -c "from forex_mastery.core.margin import stop_out_price as s; \
> print(s('EURUSD', 0.05, 1.1000, 250.0, leverage=2000, stop_out_level_percent=0.0))"
> ```

---

## Exercise answers

**1. Spread and immediate loss (0.02 lots EURUSD; ask 1.10020, bid 1.09998).**
(a) Spread = (1.10020 − 1.09998) ÷ 0.0001 = **2.2 pips**.
(b) You bought at 1.10020 and the position is valued at the bid 1.09998: floating P/L =
−2.2 pips × 0.20 USD = **−0.44 USD**, immediately.
(c) Pip value = 0.02 × 100,000 × 0.0001 = **0.20 USD**; risk on a 25-pip stop = 25 × 0.20 = 5.00 USD;
so −0.44 ÷ 5.00 = **−0.088R** before the market has moved.
*Lesson:* you start every trade behind by the spread, expressed in R. Shorter stops make that
percentage bigger, which is why "tight stop" is not automatically "small risk".

**2. 0.05 lots GBPUSD, 40-pip stop.** Pip value = 0.05 × 100,000 × 0.0001 = **0.50 USD/pip**.
Risk = 40 × 0.50 = **20.00 USD = 8.00% of a 250 USD account**.
*Correct action:* **do not take this trade.** At a 1% limit the maximum risk is 2.50 USD, which at 0.05
lots would require a 5-pip stop — well inside normal noise. The honest options are: reduce the size
(0.01 lots gives 40 × 0.10 = 4.00 USD = 1.6%, still too large), widen nothing, or skip. This is exactly
the constraint the calculator reports rather than hides.

**3. Your own spread readings.** No fixed answer — the point is the method: for 0.01 lots the pip value
is 0.10 USD, so `cost_in_R = spread_pips ÷ stop_pips`. On a 30-pip stop: 1 pip = 0.033R, 2 pips =
0.067R, 6 pips = 0.20R. If your reading was taken around a news release or at 21:30 UTC and it is more
than about 3 pips on a major, you have measured why this system blocks those windows.

**4. Margin for 0.02 lots EURUSD at 1.1000.** Notional = 0.02 × 100,000 × 1.1000 = **2,200 USD**.

| Leverage | Margin held |
|---|---|
| 1:200 | **11.00 USD** |
| 1:1000 | **2.20 USD** |
| 1:2000 | **1.10 USD** |

What changed: how much margin is locked. What did **not** change: the money at risk on any given stop,
the notional, or the effective leverage (2,200 ÷ 250 = **8.8:1** on a 250 USD account, regardless of the
broker's headline).

**5. Stop out at 0% for 0.05 lots long EURUSD at 1.1000 (250 USD equity).**
Price = **1.05000**; distance = **500 pips**; loss at that point = **250.00 USD = 100% of the account**.
*Lesson:* with a single position and a 0% stop-out level, the broker's own protection does not act until
the equity is essentially gone. Nothing protects you except the stop you place and the size you choose —
and the size is the part you fully control.

**6. R:R before and after costs.** Entry 1.1000, stop 1.0970 (30 pips), target 1.1060 (60 pips):
gross **1:2.00**. With a 2-pip spread applied to entry and exit, the engine reports net
**1:1.69**. That 0.31 of reward is real money: on a 10.00 USD risk it is 3.10 USD per trade, and it
repeats every time. Costs are not an administrative detail; they are part of the strategy's definition.

**7. Stop versus take profit.** A stop loss is (usually) a **stop order**: when the level is touched it
becomes a **market order**, so the price it fills at depends on available liquidity at that moment — in
fast markets it fills *beyond* the level. A take profit is (usually) a **limit order**: it fills at your
price or better, or not at all, so it can never fill *better* than your limit and can miss by a fraction
of a pip. Protection is approximate; profit-taking is exact but not guaranteed to happen.

**8. Swap-free.** "Swap-free" removes the overnight interest/swap charge (or credit). To confirm the
cost has genuinely gone, check: (i) whether a **fee** replaces the swap or is charged on close;
(ii) whether the **spread or commission is wider** than the standard account; (iii) which instruments
and directions are eligible, and whether the exemption expires after a number of days; (iv) whether the
account is available to your entity. Treat a "free" cost as a cost moved somewhere else until you have
found where it went.

**9. Three no-entry windows.** Any three of: (a) **30 minutes before / 15 minutes after high-impact
news** — spreads multiply and stops fill far from their level; (b) the **21:00–00:00 UTC rollover lull**
— widening spreads, thin liquidity, swap application, false moves; (c) **Sunday open and Friday close**
— gaps and unpredictable liquidity; (d) **your own losing-streak cooldown (3 losses)** — the mechanism
is impaired judgement, not the market.

**10. "1:2000 leverage means my risk is higher."** **False as stated, partly true in practice.** From
§5: 0.01 lots EURUSD at 1.1000 has 1,100 USD notional; margin held is 11.00 USD at 1:100 versus 0.55 USD
at 1:2000, while the money at risk on a 50-pip stop is identical (0.50 USD). The 0%-stop-out price for
0.10 lots was the *same* at both leverages (1.07500). Leverage changes the margin held, not the risk of
a defined stop. It is dangerous only because it *permits* a position size that the risk formula would
otherwise have blocked — that is a sizing decision, which is yours.

---

## Test answers

1. You **buy at the ask**; the position is immediately valued at the **bid**. The difference is the
   spread, and it is why a new long shows a small loss at once.
2. Because the ask (your entry) is above the bid (the valuation price) by the spread.
3. A **stop order becomes a market order**, so execution is near-certain but the price is not; a
   **limit order** fills only at your price or better, so the price is certain but execution is not.
4. **Limit order** → price guaranteed, execution not. **Stop/market order** → execution (approximately)
   guaranteed, price not.
5. **Spread** (effectively charged on entry and on exit), **commission** (per side, per lot), **swap**
   (if held overnight), **slippage** (variable). The one charged twice is the **spread**.
6. 0.02 lots EURUSD pip value = **0.20 USD**. 2-pip spread = 0.40 USD. Risk on a 25-pip stop =
   25 × 0.20 = 5.00 USD. Cost = 0.40 ÷ 5.00 = **0.08R**. (Same as Exercises 1c and 3 — this is the
   number that tells you whether your style can survive its own costs.)
7. Notional = **1,100 USD**; margin at 1:500 = **2.20 USD**; effective leverage = 1,100 ÷ 250 =
   **4.4:1**.
8. A documented 0% stop out means the broker may not close a single losing position until equity is
   essentially exhausted — the account's committed capital can be lost in one trade. The **only**
   protection before that point is your own stop loss, applied with a size you chose.
9. **Wednesday** carries the triple swap for most instruments; the documented exception is **USDCAD**,
   which is charged on **Thursday** (official Exness documentation, read 2026-09-15 — confirm in your
   terminal).
10. The **minimum volume** affects your risk per trade, because it sets the smallest position you can
    take, which in turn sets the smallest money risk for a given stop distance (the small-account
    constraint). The **margin rate** affects how much margin is held; it does not change the money at
    risk on a defined stop.

---

## What this test is really measuring

Questions 1–5 and 9 measure mechanics: if any of them were guesses, re-read §1–4 and §7 and redo the
terminal exercises. Questions 6–8 and 10 measure the separation that this whole course depends on:
**margin, leverage, notional, risk and size are five different things**, and only the last two are
yours to decide. A trader who confuses them will eventually size a position from the margin the broker
allows rather than from the risk they can afford — and that is the single most common mechanism by
which a small account is destroyed.
