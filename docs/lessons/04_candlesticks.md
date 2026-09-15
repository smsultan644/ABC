# LESSON 4 — Candlesticks: Reading a Candle as Information, Not as a Symbol

**Level:** 4 (Chart literacy)
**Estimated time:** 2 sessions of 60–75 minutes, plus the field exercise (which takes longer and is the
point of the lesson)
**Prerequisites:** Lessons 1–3 passed. You can size a trade, you know what a spread costs, and you have
a demo account in MT5 with your own captured instrument specifications.
**What you will be able to do afterwards:** read the anatomy of any candle precisely; explain what a
candle does and does not contain; classify twelve shape families with mechanical rules instead of
opinion; and — the part that actually changes behaviour — **measure a pattern's behaviour on real data
and report the failures as carefully as the successes**.

> **The rule for this lesson.** No pattern is "bullish" or "bearish" until it has been measured. Until
> then, a shape is a description of the past N bars, nothing more. Every claim you write in your
> notebook from today must be labelled **FACT** (what the candle contains), **INTERPRETATION** (what you
> think it means) or **SCENARIO** (what you think happens next).

---

## 1. Anatomy: four numbers, and everything they imply

A candle is a compressed record of one period. It contains exactly four numbers and one time label:

| Element | Meaning | What you can say about it |
|---|---|---|
| **Open** | where the period started | the first traded price of the period |
| **High** | the highest price traded | the extreme in one direction |
| **Low** | the lowest price traded | the extreme in the other direction |
| **Close** | the last traded price | the price everyone agreed on at the end |
| **Time** | which period this is | H1, H4, D1 … the timeframe is part of the data |

Everything else people say about candles — "buyers overwhelmed sellers", "the bulls won" — is
**interpretation**. The four numbers are the **facts**. This distinction is not academic; §6 shows what
happens to your statistics when you confuse the two.

### The derived quantities you will use constantly

```
body        = |close − open|                     the "agreement" part of the period
range       = high − low                         the total distance travelled
upper wick  = high − max(open, close)            the distance explored and rejected, upward
lower wick  = min(open, close) − low             the distance explored and rejected, downward
body %      = body ÷ range                       how one-sided the period was
```

Worked example — because you should be able to do this in your head:

```
open 1.1000   high 1.1060   low 1.0890   close 1.1050

body   = |1.1050 − 1.1000| = 0.0050   (50 pips)
range  = 1.1060 − 1.0890   = 0.0170   (170 pips)
upper  = 1.1060 − 1.1050   = 0.0010   (10 pips)
lower  = 1.1000 − 1.0890   = 0.0110   (110 pips)
body % = 0.0050 ÷ 0.0170   = 29%
```

**What you may conclude:** during this period, price moved 170 pips in total, spent most of the
downside excursion recovering, and closed 150 pips above its low. That is a **FACT** statement.
**What you may not conclude:** "buyers are in control" — that is an interpretation, and the next period
is free to contradict it.

The calculation is not a homework exercise; it is the input to every pattern rule below, and to your
stop placement (a stop placed inside the lower wick of the candle below you is inside noise by
construction).

---

## 2. What a candle does *not* contain (the part most courses skip)

A candle tells you four facts about one period. It does **not** tell you:

1. **The order of events inside the period.** A candle with a 110-pip lower wick could have gone down
   first then up (a rejection) or up then down then up (a grind). You cannot tell from the candle, and
   the two have different meanings. This is the single most important limitation, and it is why
   "intrabar" analysis needs the lower timeframe — see the **PLATFORM** exercise in §8.
2. **How much volume traded at each price.** FX has no central volume; your platform's "tick volume" is
   a count of price updates, not size. **FACT:** the number exists. **INTERPRETATION:** what it means
   about participation.
3. **Whether the close was "strong" because buyers bought, or because sellers stopped selling.** The
   price is the same either way; the story differs.
4. **What happens next.** Obvious, and yet every pattern book is implicitly a claim about this, made
   from a handful of charts.
5. **The timeframe's context.** A huge H1 candle is an ordinary 20-minute move inside an H4 candle.

### The "future candle" trap (the habit this lesson breaks)

The candle you are looking at right now is **not finished**. If it is 14:20 and you are on H1, the
14:00 candle has another 40 minutes to run: its high, low, close and even its shape will change. A pin
bar at 14:20 can become a marubozu at 14:59.

This matters because "the setup formed" depends on which candle you mean:

* **Closed candles** are facts. Decisions are made on closed candles.
* **The open candle** is a hypothesis in progress. It can invalidate a setup that your eyes just
  confirmed — which is precisely how beginners enter early, get filled at a worse price, and then
  watch the pattern complete in the direction they abandoned.

**The rule this system enforces:** an entry trigger must name the candle it waits for, and the
checklist ("has the trigger objectively occurred?") is answered only by closed candles. Write it as
*"entry on the close of the first H1 candle that closes above 1.1050"* — not *"when it looks like it's
breaking out"*.

---

## 3. What the timeframe is really telling you

The same market, four windows — one price series sliced differently:

| Timeframe | One candle is | Useful for | Dangerous because |
|---|---|---|---|
| M15 | 15 minutes | execution detail, entries | noise dominates; a "pattern" appears every few minutes |
| H1 | 1 hour | intraday structure, session play | session bias; the Asian lull looks like a pattern |
| H4 | 4 hours | the working timeframe for this course | few signals; patience required |
| D1/W1 | 1 day / 1 week | bias, levels, context | too slow to trade from directly for a beginner |

Two consequences you should internalise now:

* **A pattern's meaning depends on the timeframe on which it forms.** A bullish pin bar on W1 at a
  multi-month low and a bullish pin bar on M5 in the middle of a range are the same shape and different
  questions. **FACT:** the shape. **INTERPRETATION:** the significance.
* **Higher-timeframe candles are made of lower-timeframe candles.** The H4 hammer that looks decisive is
  a sequence of H1 candles, one of which is a big range candle you could have been whipsawed by. When
  you later drop to a lower timeframe for entry precision, you are looking at the *ingredients* of the
  candle that gave the signal.

**This course's working set:** bias on **D1/H4**, execution on **H4/H1**, and only those. Not because
other timeframes are wrong, but because a beginner needs one consistent lens before adding another.

---

## 4. The twelve shape families, defined mechanically

Opinions vary; the definitions below are the ones this project implements in code, so you can check any
claim with `python main.py candles --rules`. Where the literature disagrees, the disagreement is usually
about thresholds — which is itself the lesson: **a pattern you cannot define precisely is a pattern you
cannot test.**

### A. One-bar shapes

| # | Name | Mechanical rule | What it is (not what it means) |
|---|---|---|---|
| 1 | **Doji** | body ≤ 10% of range | open and close nearly equal: the period resolved where it began |
| 2 | **Marubozu** | body ≥ 90% of range | one-sided period, almost no wicks: it closed near its extreme |
| 3 | **Spinning top** | body 10–35%, both wicks ≥ 25% of range | two-sided period, both extremes rejected |
| 4 | **Bullish pin** (hammer) | lower wick ≥ 2× body, upper wick ≤ 15% of range, body in the top third | price traded far below and closed back up |
| 5 | **Bearish pin** (shooting star) | upper wick ≥ 2× body, lower wick ≤ 15% of range, body in the bottom third | price traded far above and closed back down |

### B. Two-bar shapes

| # | Name | Mechanical rule | What it is |
|---|---|---|---|
| 6 | **Bullish engulfing** | previous bearish; current bullish; current body covers the previous body (close > prev open, open ≤ prev close) | a full retracement of the previous period *by the close* |
| 7 | **Bearish engulfing** | mirror image | as above, downward |
| 8 | **Inside bar** | high < previous high AND low > previous low | compression: the whole period fits inside the last one |
| 9 | **Outside bar** | high > previous high AND low < previous low | expansion: the period breaks both previous extremes |

### C. Three-bar shapes

| # | Name | Mechanical rule | What it is |
|---|---|---|---|
| 10 | **Morning star** | strong bearish candle, then a small body, then a bullish candle closing above the **midpoint** of the first candle's body | a failed continuation followed by a reversal attempt |
| 11 | **Evening star** | mirror image | as above, downward |
| 12 | **Three soldiers / three crows** | three consecutive candles in one direction, each closing beyond the last, each body ≥ 50% of range | sustained one-way pressure — the same definition, two directions |

**Notice what is absent:** no shape on this list says anything about *where* it occurred. That is
deliberate, because location is a separate variable, and it is the one beginners under-weight the most.

---

## 5. The rule that matters more than the shape: location

The same pin bar can be:

| Where it forms | What it tells you (interpretation) | Why it differs |
|---|---|---|
| after a long move, at a level that has rejected price three times | a candidate exhaustion signal | it is where sellers/buyers previously had orders |
| in the middle of a quiet range, at no level | noise | no participant has a reason to act there |
| immediately before a high-impact release | an accident waiting to happen | the news, not the candle, will decide |
| at the session open, in the first 15 minutes | an artefact of thin liquidity | the "rejection" may be a spread artefact |

**The professional framing:** a candle is evidence about **who failed to hold a price**, and evidence is
only meaningful where price has a reason to be contested — at levels, at session extremes, around news,
inside a trend or at its end. A shape in a vacuum is a shape in a vacuum.

This is also why this course teaches structure (Lesson 5) and levels (Lesson 6) **before** it lets you
build any pattern-based setup: without a context, pattern statistics degrade into curve-fitting the past.

---

## 6. Why a pattern alone is not a strategy — and how to test that claim honestly

Here is the exercise that matters, and it is deliberately dull.

### Step 1 — Define the pattern precisely, in advance

Write it down using the mechanical rules in §4, *and* the direction you will trade, *and* the forward
window you will measure. Example:

> *"bullish_pin (lower wick ≥ 2× body, upper wick ≤ 15% of range, body in the top third) on H4.
> Direction: long. Measure the next 20 H4 bars."*

Writing it before measuring is what prevents the most common form of self-deception: finding the
definition that happens to look best on the period you already know.

### Step 2 — Measure what happened, including the ugly cases

For each occurrence, record:

* did price rise or fall over the next 20 bars (**signed return**),
* how far it went in your favour before reversing (**maximum favourable excursion, MFE**),
* how far it went against you first (**maximum adverse excursion, MAE**),
* whether **+1R was reached before −1R**, where R is the signal candle's own range.

That last statistic is the one that matters, because it is the question you actually have. And the
honest way to compute it has a subtle rule: **when a single bar touches both barriers, bar data cannot
tell you which came first, so the sample is scored as an adverse outcome.** That bias runs *against* the
pattern, which is the only acceptable direction for a bias to point.

### Step 3 — Compare with the baseline, or you have measured nothing

This is the step almost every pattern article skips: **what happened after *all* bars with a direction,
over the same period?** If a pattern reaches +1R before −1R 47% of the time and the baseline over that
period is 46%, the pattern contributed one percentage point — which at a few dozen samples is
indistinguishable from luck. The baseline is the only thing that converts a number into a finding.

### Step 4 — Report the sample-size reality next to the number

Every result in this course is reported with its caveats, because a percentage without a sample size is
not information:

| Occurrences | What you may say |
|---|---|
| fewer than 30 | "I have a hypothesis" — nothing else |
| 30–100 | "suggestive, with wide error bars" — differences under ~8 points are noise |
| 100–300 | "worth a demo test" — if it holds on other instruments and periods |
| 300+ out-of-sample, costs applied | "a candidate edge" — still not a guarantee |

And four traps that inflate every pattern statistic ever published:

1. **Overlapping windows.** If occurrences are 5 bars apart and you measure 20 bars forward, the windows
   share data. They are not independent observations, and the effective sample is much smaller.
2. **Multiple testing.** Test 13 patterns on one dataset and the best one will look good even on random
   data — that is arithmetic, not trading. (You will see this for yourself in the code exercise.)
3. **Costs omitted.** A pattern with a 0.05R edge is destroyed by a 0.07R round-trip cost. Always
   compute cost in R for the stop you would actually use.
4. **Selection.** You chose the instrument, the period and the definition — usually *after* seeing what
   worked. The only partial defence is testing on data you have not seen, in other words out-of-sample.

---

## 7. The tools for this lesson

Two commands. The first lists the objective rules; the second measures them on **data you supply**
(this project never invents or downloads market data by itself):

```bash
python main.py candles --rules

# one pattern, on your own file
python main.py candles --file data/raw/EURUSD_X_1d.csv --pattern bullish_pin --forward 20

# every pattern at once, with the baseline comparison
python main.py candles --file data/raw/EURUSD_X_1d.csv --forward 20
```

If you have no file yet, the optional `market` command downloads free practice data — clearly labelled as
practice data, not your broker's feed:

```bash
python main.py market --symbols EURUSD=X,GBPUSD=X --period 5y --interval 1d
python main.py candles --file data/raw/EURUSD_X_1d.csv --pattern bullish_pin --forward 20
```

**What the output looks like, and how to read it.** On synthetic random-walk data (a fair coin, no
edge) the tool reports something like:

```
  occurrences   : 14
  hit rate (signed forward return > 0) : 35.7%
  baseline for the same period         : 51.5%
  P(+1R before -1R)             : 21.4%
  same barrier test, baseline          : 46.7%
  difference vs baseline: -25.3 percentage points.
  ! 14 occurrences is a HYPOTHESIS, not evidence.
  ! These figures are GROSS: no spread, commission, swap or slippage is applied.
  ! You chose this file, this instrument and this period.
  ! A pattern is not a strategy.
```

Read that carefully, because it is the most valuable output in this lesson. On pure noise, a pattern
looked **25 points worse than a coin flip**. That is what small samples do: they manufacture dramatic
findings in whatever direction the last few bars happened to go. If you had opened a chart, found your
pin bars by eye, and read the story of each one, you would have written a confident paragraph about
"rejection wicks" and it would have been fiction.

---

## 8. Exercises

### Exercise A — The anatomy drill (30 minutes)

Take ten closed candles from your own chart (H4, EURUSD). For each, write: body, range, upper wick,
lower wick, body %, and the pattern name(s) it matches from §4. Then verify with:

```bash
python main.py candles --rules          # the exact definitions
```

Any candle you classified differently, write down *why* — the thresholds you used and the ones the code
used. The disagreement is the learning; the agreement teaches nothing.

### Exercise B — The intrabar exercise (20 minutes, **PLATFORM**)

Find a completed H4 candle with a long lower wick. Now open the **M15** chart for the same period and
answer: did price go down first then up, or up, then down, then up — or oscillate? Then ask the question
the candle hid: **would your stop have survived the path, not just the destination?** Do this three
times. This single exercise prevents more stop-hunting paranoia than any explanation of "liquidity
grabs".

### Exercise C — The field tally (the core exercise, 60–90 minutes)

This is the exercise from the curriculum, and it is deliberately unglamorous.

1. Choose **one** instrument and **one** timeframe you will actually trade (suggested: EURUSD, H4).
2. Take a **defined period** in advance — for example the last 200 H4 candles — and write it down.
3. Find **20** bullish pin bars *or* bullish engulfing candles (pick one; do not switch midway).
4. For each one, record: date/time, the shape's numbers (body %, wick ratio), and **what happened in the
   next 20 candles** in three columns: up/down/flat, MFE, MAE.
5. **Count the failures as carefully as the successes.** A tally that reports "18 wins out of 20" is a
   tally you did not do honestly; make sure you have looked at every chart, including the ones that
   embarrassed the pattern.
6. Report the hit rate, the median MFE, the median MAE — **and** the same numbers for 20 randomly chosen
   candles in the same period (your own baseline).

**Deliverable:** a table of 20 rows plus your baseline row, with a one-paragraph conclusion that must
contain the words "sample", "cost" and "not yet".

### Exercise D — The code version (30 minutes)

Reproduce Exercise C with the tool and compare:

```bash
python main.py market --symbols EURUSD=X --period 5y --interval 1d
python main.py candles --file data/raw/EURUSD_X_1d.csv --pattern bullish_pin --forward 20
python main.py candles --file data/raw/EURUSD_X_1d.csv --pattern bullish_pin --forward 20 --bias short
```

Answer, in writing:

1. How many occurrences did the code find in your period, and how close is that to your manual count?
   (A large gap usually means you and the code disagree about the definition — which one is better?)
2. Is the pattern's hit rate above or below the baseline? By how many percentage points?
3. Run the same command on a **second** dataset (different instrument or period). Does the ranking
   survive? (Almost always: no. Explain why that is expected.)
4. Run `--pattern all`. Which pattern looks best? Now explain, using §6's multiple-testing trap, why
   that finding is nearly worthless on its own.

### Exercise E — The trap drill (15 minutes)

Write down, in one sentence each, a concrete way that each of these could fool you in the next month:
the open (unfinished) candle, a pattern found "by eye" after the fact, a 12-occurrence statistic, and a
pattern that worked on the one instrument you checked.

---

## 9. Short test (answers hidden)

1. Define body, range, upper wick, lower wick and body % for `open 1.2000, high 1.2060, low 1.1940,
   close 1.1980` — give all five numbers in pips and the body percentage.
2. Name four things a candle does **not** tell you.
3. Why is the "open" candle dangerous as a trigger, and what is the rule this system uses instead?
4. State the mechanical rules for a bullish pin bar and a bullish engulfing candle.
5. What is the difference between an inside bar and an outside bar, and what does each represent?
6. What is the "morning star" shape, mechanically?
7. What does the baseline hit rate mean, and why is a pattern's hit rate meaningless without it?
8. In the barrier test, what happens when one bar touches both +1R and −1R, and why is that the correct
   choice?
9. Give four reasons why published pattern statistics are usually overstated.
10. You measure a pattern with 14 occurrences and it shows a 25 percentage point advantage over the
    baseline. What may you conclude, and what is the single next step?

**Pass standard:** 8 of 10, **and** Exercise C delivered. The test measures understanding; Exercise C
measures whether you can do the thing.

---

## 10. Deliverable and progress

Add to your journal:

1. The **anatomy drill** table (Exercise A) with your disagreements noted.
2. The **intrabar note** (Exercise B): three examples where the H4 candle hid the path that would have
   taken out a reasonable stop.
3. The **field tally** (Exercise C) — 20 rows plus baseline, with the honest conclusion.
4. The **code comparison** (Exercise D) — occurrences, hit rate vs baseline, and what happened on the
   second dataset.
5. Your written definition of the one pattern you will study further, **frozen today** with the date.
   From now on, that definition may only change through a documented review (Lesson 27), never because a
   chart looked convincing.

```bash
python main.py quiz --category technical_analysis --n 8 --interactive
python main.py progress
```

**Next:** Lesson 5 — market structure: swing points, trends, ranges and transitions, with the blind
classification exercise and the scoring that makes it honest. Structure is what turns a pattern from a
shape into a context, and context is where your first real edge will come from — or, more likely, where
you will first discover that you do not have one yet.

**One closing reminder.** Nothing in this lesson identifies a tradeable opportunity. It teaches you to
measure shapes honestly, which is the skill that will protect you from every subsequent claim — including
claims made by people who are certain, and including future claims made by yourself.
