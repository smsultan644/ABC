# ANSWER KEY — LESSON 4

> **Do not read this until you have written your own answers.** The arithmetic here is reproducible with
> the project's own code, and the classification rules are printed by
> `python main.py candles --rules`. Verify anything you doubt rather than trusting this file.

---

## Exercise A — Anatomy drill

| open | high | low | close | body | range | upper wick | lower wick | body % |
|---|---|---|---|---|---|---|---|---|
| 1.1000 | 1.1060 | 1.0890 | 1.1050 | 50 pips | 170 pips | 10 pips | 110 pips | **29.4%** |

Reproduce with the module:

```python
from forex_mastery.core.candles import Bar, classify_bar
b = Bar(index=0, date="d", open=1.1000, high=1.1060, low=1.0890, close=1.1050)
print(b.body, b.range, b.upper_wick, b.lower_wick, b.body_fraction)
print(classify_bar(b))
```

Body % of 29.4% with a 110-pip lower wick and only a 10-pip upper wick: it **looks** like a hammer and
it fails the bullish-pin rule on one clause. Run the clauses:

* lower wick ≥ 2 × body → 110 ≥ 100 ✔
* upper wick ≤ 15% of range → 10 ≤ 25.5 ✔
* body in the top third → the body's bottom (the lower of open and close, i.e. 1.1000) is **110 pips
  above the low** of a 170-pip range = **64.7% up**, and the rule needs **≥ 66.7%** ✘

It misses the top-third test by **2 percentage points of range** (3.4 pips). It is not a spinning top
either, because only one wick is long. **The honest answer is: this candle matches no strict pattern.**
Measured with the project's own classifier it returns the empty set:

```python
Bar(index=0, date="d", open=1.1000, high=1.1060, low=1.0890, close=1.1050)  # classify -> set()
```

This is exactly the case where "by eye" classification invents a pattern. Which answer is right?
Whichever you wrote down **before** looking — that is why the definition exists.

## Exercise B — Intrabar exercise

No fixed answer; the expected findings are: the path usually contains moves that a stop placed inside the
wick would have survived *sometimes* and not others — meaning the destination (the wick) did not predict
the path. The three conclusions worth writing:

1. A candle shows an extreme, not the order in which it was reached.
2. A stop inside a wick is a stop inside noise by construction.
3. "Liquidity grabbing" language is an **interpretation** of a path you cannot see on a higher timeframe;
   the observable fact is just "price traded there and came back".

## Exercise C — Field tally

Judged on process, not on the number:

* The period was **fixed before looking** (write it down).
* All 20 occurrences have the shape's numbers recorded (not just "looks like a pin").
* The next 20 candles were examined for **every** occurrence, including the ones that went badly.
* A **baseline** of 20 random candles from the same period was measured the same way.
* The conclusion contains "sample", "cost", "not yet".

A student who reports "18 out of 20 worked" has almost certainly looked at charts knowing the answer, or
counted only the recognisable ones. A typical honest result on a 200-candle sample is a hit rate within a
few percentage points of the baseline, with wide overlap between the pattern's and the baseline's ranges
— which is the expected outcome, because **a three-candle shape is not enough information to predict 20
candles of a nearly-random walk.** Reporting that honestly is a pass. Reporting a triumph is a fail.

## Exercise D — Code comparison

Expected answers:

1. **A gap between your manual count and the code's** is normal and instructive. Usual causes: you
   counted intrabar (unfinished) candles; you used looser thresholds (e.g. "wick looks twice the body");
   you counted both pins and engulfings; or you included bars before/after your stated period. The code
   is not automatically "right" — but a definition you cannot reproduce mechanically cannot be tested by
   anyone, including future you.
2. **Above or below baseline, by a few points.** On most single datasets the difference will be small,
   and often the *sign flips* between instruments and periods. Note it; do not act on it.
3. **The ranking usually does not survive** a second dataset. That is expected: with overlapping windows,
   a few dozen samples, no cost model and one period, the top-ranked pattern is mostly the one that fits
   that period's noise.
4. **The best-looking pattern out of 13 tested** is subject to multiple testing. Testing 13 patterns at a
   nominal 5% significance level means roughly a 1-in-2 chance that at least one looks "significant" on
   pure noise. Its own number is therefore nearly worthless as evidence; only replication out-of-sample,
   with costs, would upgrade it.

## Exercise E — Trap drill (model answers)

* **Open candle:** "I enter on a pin bar at 14:20, and the candle closes as a marubozu in the opposite
  direction; my trigger never actually occurred."
* **Found by eye, after the fact:** "I select the pins that are followed by rallies and unconsciously skip
  the ones in chop, so my tally reflects my attention, not the market."
* **12 occurrences:** "I read a 67% hit rate as an edge, when 8 wins from 12 occurrences is entirely
  consistent with a coin flip."
* **One instrument:** "The pattern liked the trending range EURUSD was in during my sample; on a
  range-bound pair in the same months it has no edge, and I never checked."

---

## Test answers

1. `open 1.2000, high 1.2060, low 1.1940, close 1.1980`:
   **body** = |1.1980 − 1.2000| = 20 pips · **range** = 120 pips · **upper wick** = 1.2060 − 1.2000 =
   60 pips · **lower wick** = 1.1980 − 1.1940 = 40 pips · **body %** = 20 ÷ 120 = **16.7%**.
   (It is a bearish candle: it closed below where it opened, with wicks on both sides — a weak
   "spinning top"-ish shape, and the mirror image of a bullish setup.)
2. Any four of: the order of events inside the period; the volume traded at each price; *why* the close
   happened where it did; what happens next; the higher-timeframe context; whether the move was driven by
   news.
3. The open candle is unfinished — its high, low, close and shape can still change, so a setup "forming"
   can vanish before the period ends. The system's rule: **triggers are evaluated on closed candles
   only**, and the trigger must name the candle (e.g. "the first H1 close above 1.1050").
4. **Bullish pin:** lower wick ≥ 2× body, upper wick ≤ 15% of range, body in the top third.
   **Bullish engulfing:** previous candle bearish, current bullish, and the current body covers the
   previous body (close > previous open, and open ≤ previous close).
5. **Inside bar:** the whole range fits inside the previous bar's range (compression — a pause).
   **Outside bar:** the range breaks both the previous high and the previous low (expansion — a
   resolution). They are opposites in meaning: one is a decision deferred, the other a decision taken.
6. **Morning star:** three bars — a strong bearish candle, then a candle with a small body, then a
   bullish candle that closes back above the **midpoint of the first candle's body**.
7. The **baseline** is what happened after a *typical* bar (with the same direction and forward window)
   over the same period. A pattern's hit rate is meaningless without it because part of the hit rate is
   simply the market's behaviour during the sample: if the market drifted up, then *any* long-side
   pattern looks good. Only the difference from the baseline is attributable to the pattern.
8. When one bar touches both barriers, the sample is counted as **adverse** (a loss), because bar data
   cannot reveal which barrier was touched first. It is correct because it biases the result **against**
   the pattern: a finding that survives a hostile assumption is far more credible than one that depends
   on a favourable guess.
9. Any four of: overlapping forward windows (non-independent samples); multiple testing (the best of 13
   looks good on noise); costs omitted; selection of instrument/period/definition after seeing results;
   no out-of-sample validation; intrabar path unknown; the pattern's definition drifting between studies.
10. You may conclude **nothing about the pattern** — you have a hypothesis worth one more test, from a
    sample far too small to carry 25 points of difference. The single next step is to **measure the same
    frozen definition on a different dataset** (another instrument or a non-overlapping period, with
    costs included in R). If the effect survives that, it becomes a candidate for a demo test; if it does
    not, that is a **successful** outcome — you spent an hour instead of an account.

---

## What this test is really measuring

Questions 1, 4, 5 and 6 measure whether you can define a candle **mechanically** — the precondition for
ever testing anything. Questions 2, 3 and 8 measure whether you understand what candle data *cannot* tell
you, which is what keeps a trader out of the "the market hunted my stop" trap. Questions 7, 9 and 10
measure the one habit that separates this curriculum from pattern-selling: **a number without a baseline,
a sample size and a cost model is not information.**

The uncomfortable conclusion of this lesson, stated plainly: on the evidence you just gathered, you have
no reason to believe any single candle pattern predicts anything. That is not a failure of the lesson —
it is the correct starting position, and it is a far better place to begin building from than a belief you
cannot support.
