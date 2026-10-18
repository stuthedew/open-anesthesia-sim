---
id: PL-04KR
title: Pre-register the apparatus-convergence expectation on two causal signals, baselined 2026-09-19, so the owner's expectation that workflow inflow declines can fail loudly rather than be re-argued
priority: P2
effort: M
status: done
classes: infra, planning
feature: convergence-visibility
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/trend.py, subprojects/docket/tests/test_trend.py, docs/items
added: 2026-09-19
closed: 2026-10-18
pr: 1591
verify: grep -q '^### Checked at the third release' docs/items/PL-04KR-pre-register-the-apparatus-convergence.md
recurrences: 2026-09-23 PL-02C4 withdrawn 2026-09-23 PL-02C4
---

**Problem.** The project owner stated an expectation on 2026-09-19: with the
known generator root causes closed and no new user-requested functionality being
added, the rate of new workflow-lane issues should decline from here. They asked
for a sanity check on it, with the intent stated precisely — "to make sure we
don't need to investigate an unknown issue that is generating additional bugs
that we are just patching other than fixing the upstream issue, or an unknown
generator basically."

Nothing currently answers that. `bin/docket trend` reports closures,
effort-weighting and churn, and **no inflow term at all**, so the command whose
name promises this shows only the lagging half. `PL-WXKD` is the standing item
for the gap.

**What to watch, and what was rejected.** The owner explicitly ruled out backlog
counts and any product-to-workflow ratio — "I don't really care about the backlog
so much and it doesn't help me to say that we have a bunch open still". Two
causal signals instead:

[superseded 2026-10-11: re-entry is read from the triage-written `reenters:` field, not from paths; `PL-WXKD`] 1. **Re-entry rate** — new workflow items landing on a path that a *closed* item
   also touched, where the closure was within the preceding 30 days. Rising means
   fixes are not holding, which is the "patching rather than fixing upstream"
   case. **This is the signal that is currently structurally impossible to see**:
   of 623 attributed parent-child links in the store, 100% of children were filed
   in the very commit that closed the parent, median lag zero, nothing above zero.
   The existing attribution captures filed-while-working and never
   fix-did-not-hold.
[superseded 2026-10-11: sharing a mechanism is judgment and is not computed; `docket inflow` names a closed item three filings re-enter instead, `PL-WXKD`] 2. **Largest unexplained cluster** — open items sharing a mechanism with no
   `root-cause-of:` head above them. Growing means an unfound cause is
   accumulating instances. **27 on 2026-09-19** (`PL-G424`).

Rejected, with reasons: gross inflow ÷ closures, because a capture- or
triage-policy change moves it for reasons unrelated to generators and the
reassuring direction is the one it would show either way; release workflow share
and open-backlog counts, because closures lag generation by weeks — 151 open
items and 44 of 65 generator-explained items still open mean apparatus-heavy
releases continue well after generation falls; and raw path recurrence, which
`PL-WXKD` already refuted as arithmetic rather than regression at 90% on a
surface of 117 apparatus files. [superseded 2026-10-11: measured, 93-100% of every week's apparatus filings from 2026-08-31 name a path some item closed within the 30 days before, so the bound does not distinguish it; `PL-WXKD`] The 30-day bound on signal 1 is what
distinguishes it from that refuted metric: "this path came back within 30 days of
us closing something on it" is a statement about a fix, not about surface size.

**The baseline, measured 2026-09-19.** The window 2026-09-17 to 09-19 is
contaminated and excluded: it was a deliberate generator campaign, with six of
the seven recorded generators both recorded and closed on 09-19. Week 1 is also
excluded as the ground-up build period. The clean baseline is weeks 2-4.

```
self-generation rate (workflow lane)   0.696   multiplier 1/(1-r) = 3.29
inflow / closures, weeks 2-4           1.38, 1.54, 1.43   (week 1: 2.40)
new paths per filed item               1.16 -> 0.26 -> 0.21 -> 0.13
P1 workflow filings by week            0, 2, 1, 0
open workflow P1 band                  0
P3 share of workflow filings           17% -> 29% -> 24% -> 41%
largest unexplained cluster            27
re-entry rate                          not yet measurable - see signal 1
```

**The prediction, to be checked at the next three releases.** Re-entry rate flat
or falling once it can be measured; largest unexplained cluster not growing above
its post-sweep value; P1/P2 workflow filings staying at zero; new paths per filed
item staying at or below 0.13. If all hold, the owner's expectation was correct
and no tracking mechanism was needed. If any moves the wrong way, that is the
trigger to investigate, and which one moved says what to look for: re-entry
points at a fragile area, cluster growth at an unnamed cause.

**Two things whoever implements this must not get wrong.** Generator-campaign
filings need breaking out separately, or the next deliberate sweep reads as
regression and sends someone hunting a generator that does not exist — the
contamination this brief already had to exclude by hand. And 11 open items
declare another item's *file* as their `touches`, which would inflate the
re-entry rate for a bookkeeping reason; item-file paths need excluding.

**A reading taken 2026-09-21 confirms the contamination warning above before
the command exists.** Measured over the whole store by `added:` date, lane
assigned from `touches` with `docs/items`-only declarations excluded as
bookkeeping, apparatus share of classified filings by ISO week reads 57.0% ->
59.5% -> 63.3% -> **66.5%** for W35-W38 — a rise, and the shape that sends a
session hunting a generator. Dropping 2026-09-17 to 09-19, the window this
brief already excludes as a deliberate generator campaign, the same series
reads 57.0% -> 59.5% -> 63.3% -> **58.6%**: flat, not rising. The 7.9-point
swing on three days is the whole apparent regression, so the break-out this
brief asks for is not a refinement of the measurement, it is the difference
between the right answer and the wrong one. W39 is two days and n=37 and is
not read.

That share is **not a third signal and must not become one.** `CLAUDE.md`
§ "What this project is" says no ratio is tracked or enforced, and this brief's
two signals are deliberately causal rather than proportional. It is recorded
here only as the reading a session will take when it notices the apparatus lane
is busy — which is the re-argument-from-memory this item exists to end — and as
evidence that the exclusion is load-bearing rather than cautious.

**What it leaves standing.** Flat is not declining. The owner's 2026-09-19
expectation was that apparatus inflow *declines* as the functionality settles,
and four weeks of flat share neither confirms nor refutes it, because share is
not the claim. Both signals that are the claim remain unmeasurable while this
item is open, so the expectation is still in the unfalsifiable state
§ "Why it matters" below names.

**A first reading of signal 1, taken by hand on 2026-09-23.** The command
this item asks for still does not exist. Since `PL-KVDK` (2026-09-22), though,
triage writes a `**Generator check.**` line into every workflow-lane item, and
that line records re-entry directly. Of the 37 workflow- and crossing-lane
filings from 2026-09-22 and 09-23 that carry one, 14 name a closed item whose
fix did not reach them, either as a post-close instance of a head or as a
re-entry within 30 days: `PL-1P5V`, `PL-3W3P`, `PL-6SV4`, `PL-8GV1`, `PL-BBT8`,
`PL-DNZ0`, `PL-DSPM`, `PL-J16N`, `PL-1PBV`, `PL-59QW`, `PL-9VPH`, `PL-FD5Q`,
`PL-JD4L` and `PL-JLYG`. Two of the four captures still untriaged that day are
the same kind (`PL-58JD`, `PL-PZ6T`). Three of the heads closed on 2026-09-23
as `spent` (`PL-9RFP`, `PL-8YXJ`, `PL-J6HP`) each drew one such item the same
day, and `PL-1PBV` was filed ten minutes after `PL-9RFP` merged. One reading
cannot show a trend, and the trend is what the prediction is about. As a level,
though, it means more than a third of new workflow items are fixes that did not
hold, which is the case the prediction above says points at a fragile area. The
same pass found a cluster with no head, now recorded as `PL-WD5Z`, so signal 2
moved as well. Deliberately not counted as a signal: gross non-product filings
by day since the campaign read 97, 75, 69, 44 and 32 (the last is a partial
day). That series is falling, but it is gross inflow, which this brief rejects
as a signal.

**Staleness caveat on every number above.** `PL-LKGL` measured 32% of the
workflow lane dead or partly overtaken on 2026-09-12. The 151, the cluster sizes
and both rates are therefore upper bounds. The apparatus backlog review
commissioned 2026-09-19 will move them.

**Why it matters.** The expectation is currently unfalsifiable, which is the
worst of both states: it cannot be confirmed, so it gets re-argued from memory
in every session that notices the apparatus lane is busy, and it cannot fail,
so an actual unfound generator would go on producing instances with nothing
saying so. `CLAUDE.md` § "What this project is" settles the *level* question
("there is too much apparatus" stays refused) and says in the same breath that
it cannot settle the *trend* one - "Apparatus inflow should be declining now
that the functionality is settled, and if it is not, something is generating
work we should go and find" is named there as live, and this item is what it
points at. A pre-registered prediction with its numbers fixed before the
outcome is known is the only form that can lose; a measurement chosen
afterwards will agree with whoever chose it.

The half that is genuinely missing rather than merely unpublished is signal 1.
Of 623 attributed parent-child links, 100% of children were filed in the commit
that closed the parent - so the store records filed-while-working and has never
once recorded fix-did-not-hold. That is not a low reading of re-entry; it is no
reading at all, and it is the signal that would distinguish "we are patching
instances" from "we are fixing causes".

**Done when.** [superseded 2026-10-11 in part: the command is `bin/docket inflow`, which reports re-entry from `reenters:` rather than on the 30-day path bound and computes no cluster (`PL-WXKD`, project owner, ratified). What stands is the last two sentences: `bin/docket release` prints any prediction the last complete week broke, and each of the next three cuts' results is recorded here under a `### Checked at` heading, the third headed `### Checked at the third release`.] A command reports both signals over the store - re-entry rate on
the 30-day bound, and the largest open cluster carrying no `root-cause-of:`
head - with generator-campaign filings broken out separately and item-file
paths excluded from the re-entry surface, which are the two ways the brief
above says the numbers go wrong. The 2026-09-19 baseline in this item is what
the command's output is read against, and the prediction is checked at each of
the next three releases, with the result recorded here. If all four predictions
hold, this item closes having found nothing, which is the outcome it exists to
be able to report.

**How the three cuts below were read, 2026-10-18.** Each reading replays what
`bin/docket release` printed at that cut. It runs the tag's own copy of
`docket` over the tag's own store, with the reference date set to the tag's
commit date, and calls the same `_missed_expectations` that `release` calls.
The `bin/docket inflow --today DATE` table was read the same way. `bin/docket
inflow` (`PL-WXKD`) shipped in v0.5.24, so v0.5.24 is the first of the three
cuts.

### Checked at v0.5.24 (2026-10-12)

Silent: every prediction held. The last complete week was 2026-10-05 to 10-11.
It had 53 apparatus filings that no head explained and 62 filed by a head. It
named 4 new apparatus paths, which is 0.03 a filing against the 0.13 ceiling.
It had 15 re-entries against 18 the week before, so re-entry fell. Its 3 `P1`
filings were all on the generator tier, so none counted against the
prediction.

### Checked at v0.5.25 (2026-10-17)

Silent: every prediction held. The cut read the same week, 2026-10-05 to
10-11, because the week from 10-12 had not ended. The numbers were unchanged
except that one more filing in that week was counted under a head.

### Checked at the third release: v0.5.26 (2026-10-18)

Silent: every prediction held. The cut again read the week 2026-10-05 to 10-11,
because the week from 10-12 ends on 10-18 and a week counts as complete only
once it has ended. v0.5.27 and v0.5.28, cut the same day, read that week too.

### Result

**All three cuts held, but they checked one week, not three.** Five releases
were cut in six days, so the three checks this item asked for all read the
week of 2026-10-05 to 10-11. In that week the predictions held clearly: new
paths per filing fell to 0.03, re-entry fell, and no apparatus filing outside
the generator tier reached `P1`.

**The next week will miss two predictions, and the next cut will say so.**
Read with the reference date set to 2026-10-19, the first day after the week
of 2026-10-12 to 10-18 ends, `release` prints two misses for that week. It
names 24 new apparatus paths over 91 filings, 0.26 a filing, against the 0.13
ceiling. It also counts 2 `P1` apparatus filings outside the generator tier.

**What the two misses are made of, read by hand on 2026-10-18.** This is a
reading, not a verdict on whether a generator is behind it.

- The 2 `P1` filings are `PL-HQF5`, a `safety`-classed defect in the cardiac
  output a tissue group can be given, and `PL-4RL2`, a `science`-classed
  citation fix. Both are simulator work. Each counts as an apparatus filing
  only because it also declares a file under `.claude/rules/`. Each is `P1`
  because `docket check` pins `safety` and `science` work to `P1`, not because
  of anything in the apparatus. So this miss is a false alarm in how the
  prediction is counted. It is filed as its own item.
- Of the 24 new paths, 13 were first named on 2026-10-12 and 11 on 10-17 and
  10-18. Most are new files that a filing set out to create: new rules
  (`.claude/rules/plain-writing.md`, `.claude/rules/test-oracles.md`), new
  tools (`tools/fact_home_check.py`, `tools/diff_mutation.py`,
  `tools/new_prose.py`), their tests, a new skill directory
  (`.claude/skills/model-review`) and two test corpora under
  `subprojects/docket/tests/`. The owner asked for several of them, for
  example the plain-writing rule on 2026-10-17 (`PL-8ZTQ`). New mechanisms
  were allowed again once no head carried `generator: live`.

So the surface grew because new mechanisms were built on request, not because
defects arrived in new places. That is the reading the prediction's own
wording allows for: "If any moves the wrong way, that is the trigger to
investigate, and which one moved says what to look for." The two misses point
at a counting rule and at deliberate building. Neither points at an unfound
generator.

**Why the item closes.** Its done-when asks for the three cuts' results, and
they are recorded above. The mechanism the item exists for does not depend on
it staying open: `bin/docket release` checks the last complete week at every
cut and prints any prediction it broke. The false alarm in the `P1` count is a
separate item, so a later cut's miss can be read for what it is.
