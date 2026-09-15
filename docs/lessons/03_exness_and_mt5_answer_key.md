# ANSWER KEY — LESSON 3

> **Do not read this until you have written your own answers.** Every number below comes from the
> calculation engine (`forex_mastery.core`) or from official Exness documentation read on **2026-09-15**.
> Reproduce the arithmetic yourself with:
>
> ```bash
> python main.py broker --account standard --hmr
> python -c "from forex_mastery.core.margin import stop_out_price as s; \
> print(s('EURUSD', 0.05, 1.1000, 250.0, leverage=2000, stop_out_level_percent=0.0))"
> python main.py position --symbol EURUSD --balance 250 --risk 0.25 --entry 1.1000 --stop 1.0975
> ```

---

## Exercise answers

**1. Margin call and stop-out levels by account type (documented).**

| Account type | Margin call | Stop out |
|---|---|---|
| Standard Cent | 60% | 0% |
| Standard | 60% | 0% |
| Pro | 30% | 0% |
| Raw Spread | 30% | 0% |
| Zero | 30% | 0% |

A *lower* margin call percentage is not an advantage: the margin call is a **warning**, so a warning that
triggers at 30% instead of 60% arrives later — after the account has already lost more of its equity.
The stop-out level (0% everywhere except the documented entity exception of 20%) is the level at which
positions are forcibly closed; the margin call is the earlier notification. Later notification is not
more protection.

**2. Stop-out distance for 0.05 lots long EURUSD at 1.1000, 250 USD equity.**
Stop-out price at 0% = **1.05000**; distance = **500 pips**; loss at that point = **250.00 USD = 100% of
the account**.
With 0.5 lots (10× the size), the stop-out moves to roughly **50 pips** away (10× closer), because the
money loss per pip is 10× larger and the account is unchanged. **The stop-out comes closer in proportion
to size relative to equity** — not in proportion to leverage. That is the whole lesson of §4 in one
number.

**3. Margin and HMR.**
0.10 lots EURUSD at 1.1000 → notional **11,000 USD**.
Margin at 1:2000 = **5.50 USD**; margin at 1:200 = **55.00 USD**. Difference: **49.50 USD of free margin**
on a 250 USD account — about 20% of the account, converted from capital available for other positions
into margin held.
Illustrative leverage figures; what matters is the method — read the leverage shown in the New Order
window and compute the margin yourself. The practical rule that avoids the problem: **be flat before the
weekend while learning**, and never hold multiple positions through an HMR window.

**4. Cost comparison (illustrative spreads — replace with your own measurements).**
Using a 1.2-pip Standard spread and a 0.3-pip Raw Spread spread plus 3.50 USD per side per lot, on
**0.01 lots** with a **30-pip stop** (risk = 30 × 0.10 = 3.00 USD):

| Account style | Cost components | Total | Cost in R |
|---|---|---|---|
| Standard | 1.2 pips × 0.10 = 0.12 USD | **0.12 USD** | **0.0400R** |
| Raw Spread | 0.3 pips × 0.10 = 0.03 USD + (3.50 × 2 × 0.01) = 0.07 USD | **0.10 USD** | **0.0333R** |

The two are **within 0.007R of each other** — under 2 cents per trade at this size. The advertised "from
0.0 pips" does not mean free, and at micro size the commission can consume most of the spread saving.
What would change the answer: your actual measured spread (rather than the advertised floor), a different
stop distance (shorter stops raise cost-in-R for everything), higher volume (commission scales linearly
with lots, as does the spread saving), and swap if you hold overnight. *This is why the rule is "measure
your own costs in R", not "choose the account with the lowest advertised spread".*

**5. Trading volume.**
`TV = lots × contract size`, always in base currency.

| Order | TV |
|---|---|
| 0.02 lots EURUSD | **2,000 EUR** |
| 0.35 lots XAUUSD | **35 troy ounces** |
| 0.50 lots UKOIL | **500 BBL** |

TV is the *size* of the position; it is not risk. Risk is `stop distance × pip value × lots`. The same
0.35-lot gold position is a small risk with a 30-pip stop and a very large one with a 300-pip stop.

**6. Specification search.** No fixed answer — the required content is: contract size, digits, volume
min, volume step, swap long, swap short, plus any minimum stop/limit distance, each with the date and the
source ("MT5 → Market Watch → right-click EURUSD → Specification, my demo account, 2026-09-15"). This
becomes a permanent page in your journal. Note the trap: **1 pip = 10 points**; if a value looks 10× too
large or too small, you have mixed the two units.

**7. The ten-step procedure.** Judged on completeness, not wording. It must include: setup named and in
the plan; levels with structural reasons; risk in percent and money; size computed and rounded **down**;
rule-engine verdict read; order ticket with SL, TP and a comment tying the trade to the journal id;
screenshot before; confirmation that the position shows SL and TP; deliberate disengagement; journal entry
before the next instrument. Target: under five minutes, every time.

**8. Hedge reasoning (example).** Hedging a loser locks in the loss, pays two spreads plus a swap, and
creates two new decisions at the moment your judgement has just been proven wrong; unlocking it is a fresh
directional bet made under pressure. The professional equivalent of "hedging" a losing position is
**closing it** — and if the other direction is genuinely supported by your plan, taking that trade
afterwards with a new written justification.

**9. Pip versus point.** A displayed spread of `14` on a 5-digit pair = **1.4 pips**.
For 0.02 lots EURUSD (pip value 0.20 USD): 1.4 × 0.20 = **0.28 USD** paid on entry.

**10. Readiness criteria concerning broker and platform operation.** The relevant ones include *costs
understood* (you can state the round-trip cost of your typical trade in money and in R), *journal
complete* (which requires platform history, screenshots and reasons), *documented routine* (you operate
the platform the same way every session), and *risk discipline* (never more than the stated risk, which
can only be verified from the platform's records). They sit alongside the statistical criteria because
operational failure and statistical failure are the same failure viewed from two sides: an account can be
destroyed by two bad decisions just as easily as by a system with no edge — and only the operational
criteria are fully under your control.

---

## Test answers

1. **Standard Cent, Standard, Pro, Raw Spread, Zero.** Those whose deposit is *not* region based are
   **Standard Cent and Standard** (the documentation states "No" rather than "Yes; region based").
2. **Standard Cent has no demo version.** It matters because the account that solves the minimum-lot
   problem on a 250 USD balance cannot be rehearsed in advance — so if you plan to use it live, you must
   reason about cent-lot arithmetic explicitly (0.01 cent-lots are roughly 1/100th the money value of
   0.01 standard lots), and you cannot rely on demo muscle memory for the exact numbers.
3. **Standard: margin call 60%, stop out 0%.** **Pro: margin call 30%, stop out 0%.**
4. (i) **Stocks** may rise to a **100%** stop out under increased market risk; (ii) a **20%** stop out
   applies to clients registered via **Exness (KE) Limited** and **Exness Limited Jordan Ltd**. You must
   check yours because the difference between 0% and 20% decides whether one position can empty the
   account, and because entity rules differ by where your account is registered.
5. The broker may **not close the position until equity is essentially exhausted** — a single losing
   position can take the account to (approximately) zero. Nothing automatic protects you before that
   point; only your own stop loss and your own size do.
6. **The account type and the server cannot be changed** after creation (documented). Leverage and
   account currency are account settings you can typically change in the Personal Area — verify in yours.
   (The test asked for the unchangeable ones.)
7. **HMR = Higher Margin Requirements.** Documented windows: from **3 hours before a weekend close until
   1 hour after the market reopens**, and for **positions opened 15 minutes before a news release until
   90 seconds after**. Crypto is exempt from weekend HMR, because it trades 24/7.
8. The **New Order window** always shows the leverage that will be used for margin calculation (and an
   HMR banner appears on charts in Exness Terminal and Exness Trade).
9. *"Trading volume is always calculated in base currency"*: **TV = number of lots × contract size.**
   Example: 0.02 lots EURUSD = 2,000 EUR (or 3 lots UKOIL = 3,000 BBL, per the documentation).
10. Documented caveats (any two): spread cost is based on the **previous trading day's average** spread
    and the real cost is only known when an order is really opened; results depend on account type,
    currency, instrument, volume and leverage; for instruments with **fixed margin requirements the
    leverage setting is disabled**. One thing this engine does that the broker calculator does not: it
    **refuses to run without a known conversion rate** (`MissingRateError`) and reports a below-minimum-lot
    size as a **hard error listing the alternatives**, rather than producing a number that looks usable.

---

## What this test is really measuring

Questions 1–6 measure whether you understand that an account is a **package of conditions you choose
once** — and that the significant part of it (what happens when a trade goes wrong) is decided before
your first trade. Questions 7–10 measure whether you can operate the platform with the same precision you
bring to the arithmetic: reading the leverage actually applied, converting points to pips, knowing what
"volume" means, and treating the broker's own tools as evidence to be compared rather than truth to be
believed.

The single most valuable habit from this lesson is small and unglamorous: **record your account conditions
and verify them quarterly.** A trader who knows their stop-out level, their real cost in R, and the
leverage their orders are actually using cannot be surprised by the platform — only by the market, which
is normal, and by themselves, which the journal catches.
