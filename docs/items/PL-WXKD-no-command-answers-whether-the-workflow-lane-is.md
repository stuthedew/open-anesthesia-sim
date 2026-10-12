---
id: PL-WXKD
title: No command answers whether the workflow lane is converging: docket trend reports the workflow/product balance, so a session asked whether accumulation is slowing re-derives filed-per-closed, surface saturation and severity mix by hand at full context
priority: P2
effort: M
status: done
classes: infra
feature: convergence-visibility
milestone: v0.5.24
touches: subprojects/docket/src/docket/inflow.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/trend.py, subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_inflow.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, .claude/skills/docket/modes/triage.md, docs/items, CLAUDE.md
added: 2026-09-17
closed: 2026-10-12
pr: 1420
verify: grep -q 'def test_a_reentry_is_counted_in_the_period_it_was_filed' subprojects/docket/tests/test_inflow.py && grep -rqE '^reenters: PL-' docs/items
---

**Problem.** No command answers whether the workflow lane is converging: docket trend reports the workflow/product balance, so a session asked whether accumulation is slowing re-derives filed-per-closed, surface saturation and severity mix by hand at full context

**Measured 2026-09-17, in answer to "is the accumulation slowing?".** Every
number below came from a throwaway script over `docs/items/`, at full session
context. None of it is reachable from any shipped command, so the next session
asked the same question pays the same cost.

Periods are 7 days anchored at 2026-08-23, the first `added` date. The last is
5 days, so rates are normalised per day where the count is compared.

| period | filed/day | closed/day | filed per closed |
| --- | --- | --- | --- |
| 08-23 | 3.6 | 1.4 | 2.50 |
| 08-30 | 34.3 | 25.0 | 1.37 |
| 09-06 | 15.3 | 11.4 | 1.34 |
| 09-13 | 31.2 | 20.6 | 1.51 |

Rolling 7-day filed-per-closed: 3.00, 1.49, 1.79, 1.58. **Plateaued, not
falling.** This is gross inflow over closures in a window, so it is an upper
bound on `PL-CSHL`'s 0.69, which counts only items attributable to the work on
a given item. The two are not comparable and neither refutes the other.

**Surface saturation** — cumulative distinct apparatus paths named by a filed
item, store paths (`docs/items`, `docs/WORKING_NOTES.md`, `docs/dead-ends.md`)
excluded:

| through | cumulative paths | new that period | filed | new paths per item |
| --- | --- | --- | --- | --- |
| 08-23 | 29 | 29 | 25 | 1.16 |
| 08-30 | 92 | 63 | 240 | 0.26 |
| 09-06 | 114 | 22 | 107 | 0.21 |
| 09-13 | 134 | 20 | 156 | 0.13 |

134 distinct paths against 117 apparatus files in the tree: the surface has
been covered. This is the measure that distinguishes exhaustion from failure,
and it is the one nothing reports.

**Why a raw recurrence rate misleads.** 90% of items filed in the last period
name a path some already-closed item had touched, which reads as fixes not
holding. It is arithmetic: 528 workflow items over 117 files is 4.5 items per
file, so past week two every finding *must* be a return visit. A convergence
report has to pair recurrence with saturation or it will accuse the lane of
regression it has no evidence for.

**Severity decay**, share of each period's workflow filings:

| period | P1 | P2 | P3 | defect | P3 share |
| --- | --- | --- | --- | --- | --- |
| 08-23 | 0 | 19 | 4 | 28% | 17% |
| 08-30 | 2 | 160 | 69 | 52% | 30% |
| 09-06 | 1 | 87 | 19 | 64% | 18% |
| 09-13 | 0 | 82 | 70 | 53% | 46% |

Open workflow backlog: 160 items, 0 P1, 79 P2, 81 P3.

**What the command should report**, at minimum: filed-per-closed rolling;
new-paths-per-item; the P1/P2/P3 mix of filings, not of the backlog; and the
count blocked on an owner decision, which on this date is 33 of 160 open
workflow items and is the binding constraint rather than throughput.

**Care needed on the denominator.** `docs/items` appears in only 65 of 528
workflow items' `touches`, so excluding store paths changes little here — but
it must be excluded explicitly, because the store sits inside `workflow_paths`
and every capture made while doing something else would otherwise count as
apparatus work. `docket trend` already makes this exclusion for churn; the
same rule applies.

**Not a health score.** `docs/dead-ends.md` records open-backlog ratio as
refuted (`PL-03XH`). This reports rates and composition, and must not
reintroduce a single number standing for the lane's health.

**Why it matters.** "Is the accumulation slowing?" is the question that decides
whether the apparatus lane is converging or is whack-a-mole, and `CLAUDE.md`
answers an objection to the *balance* while saying nothing about the *rate*. The
numbers above cost a throwaway script at full session context, and the next
session asked the same question pays the same cost from scratch - which is
exactly `CLAUDE.md`'s "work left to the model is re-derived at full context in
every session that needs it". The decidable half here is large: filed-per-closed,
new-paths-per-item and the severity mix of filings are all arithmetic over the
store. Only reading the result is judgment.

[superseded 2026-10-11: the decided Done-when is under "Answered" at the end] **Done when.** One command reports, for the workflow lane, rolling
filed-per-closed, new distinct apparatus paths per item filed with store paths
excluded, the P1/P2/P3 mix of each period's *filings* rather than of the
backlog, and the count blocked on an owner decision - no single composite score,
per `docs/dead-ends.md` on the open-backlog ratio - and a test under
`subprojects/docket/tests/` pins the store-path exclusion and the rate
normalisation for a short final period.

## Raised to P2, and what the command should report (project owner, 2026-09-19)

The project owner asked for this three times in one conversation, in their own
words: "Is there a way to keep track of that at least a little going forward
primarily as a sanity check to make sure that the trend of new workflow issues is
decreasing over time as expected ... mostly make sure that we aren't missing
anything like an unknown generator of bugs that needs to be addressed." An item
the owner has asked for three times is not a `P3`.

**Two constraints they stated, which narrow this item's original scope.** No
ratio is to be tracked or enforced, and backlog counts are explicitly not wanted:
"I don't really care about the backlog so much and it doesn't help me to say that
we have a bunch open still." So `filed-per-closed` and `severity mix` as this
brief first framed them are context at most, not the headline.

**What to report instead — two causal signals, with `PL-04KR` holding the
baseline they are measured against:**

[superseded 2026-10-11: path recurrence reads 93-100% every week; re-entry is the triage-written `reenters:` field, under "Answered"] 1. **Re-entry rate** — new workflow items landing on a path that a *closed* item
   also touched, where that closure fell within the preceding 30 days. Rising
   means fixes are not holding. This is the signal the store currently cannot
   show at all: of 623 attributed parent-child links, 100% of children were filed
   in the commit that closed the parent, so the existing attribution sees
   filed-while-working and never fix-did-not-hold. Exclude item-file paths — 11
   open items declare another item's file as their `touches` and would inflate it
   for a bookkeeping reason.
[superseded 2026-10-11: sharing a mechanism is judgment and is not computed; a closed item three or more filings re-enter is named instead] 2. **Largest unexplained cluster** — open items sharing a mechanism with no
   `root-cause-of:` head above them. 27 on 2026-09-19 (`PL-G424`). Growing means
   an unfound cause is accumulating instances.

**Report it at release time, silent when the trend matches expectation.** A
per-session advisory would fire every run and become the noise `CLAUDE.md`
already says is a defect in a check. And break generator-campaign filings out
separately, or the next deliberate sweep reads as regression — the 2026-09-17 to
09-19 window had to be excluded from `PL-04KR`'s baseline by hand for exactly
that reason.

**Do not re-propose raw path recurrence.** This item already refuted it: 90%
recurrence on a surface of 117 apparatus files is arithmetic, not regression. [superseded 2026-10-11: measured, it does not] The
30-day bound on signal 1 is what makes it a statement about a fix rather than
about surface size.

## Built 2026-10-11, and the one question it leaves

**Built, the same under any answer below:** `bin/docket inflow`
(`subprojects/docket/src/docket/inflow.py`, rendered by `render.format_inflow`,
tests in `subprojects/docket/tests/test_inflow.py`). One row per 7-day period
(or `--by day`), counting apparatus filings - an item whose `touches` name a
path under `workflow_paths`, whatever its lane (`PL-4NZ7`), with `items_dir`
and `notes_file` left out of that test and of the path count. Columns: `filed`
and `/day` (divided by the days the period has, so a short final period
compares); `+head`, the members a head's `root-cause-of:` names that were filed
while that head was open, which is the campaign break-out `PL-04KR` asks for,
read from the record rather than from a hand-cut window; the P0-P3 mix of
`filed`, untriaged shown as `-`; and new apparatus paths with `/item`. First
reading, 2026-10-11:

| week from | filed | /day | +head | P1 | P2 | P3 | new paths | /item |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 08-24 | 73 | 10.4 | 0 | 2 | 55 | 11 | 46 | 0.63 |
| 08-31 | 268 | 38.3 | 2 | 7 | 185 | 70 | 53 | 0.20 |
| 09-07 | 110 | 15.7 | 6 | 4 | 87 | 19 | 27 | 0.23 |
| 09-14 | 208 | 29.7 | 27 | 5 | 139 | 60 | 27 | 0.11 |
| 09-21 | 225 | 32.1 | 79 | 5 | 115 | 93 | 38 | 0.12 |
| 09-28 | 70 | 10.0 | 63 | 8 | 26 | 34 | 13 | 0.10 |
| 10-05 | 46 | 6.6 | 60 | 1 | 3 | 42 | 2 | 0.02 |

The break-out is load-bearing: `PL-R417`'s sweep filed 57 of the 60 `+head`
filings in the last week, so folding them in would read 106 filings where 46
arrived unexplained.

**Decided in the session, each with one clearly correct option:**

- **Path re-entry is refused, the 30-day bound included.** The brief's claim
  that the bound "is what makes it a statement about a fix rather than about
  surface size" was measured and does not hold: 93-100% of every week's
  apparatus filings from 2026-08-31 name a path some item closed within the
  previous 30 days - 75%, 97%, 95%, 97%, 97%, 100%, 100% by week at the
  declared paths, and 75%, 97%, 93%, 97%, 97%, 100%, 100% at file granularity
  alone. A column that reads the same every week changes no decision.
- **The largest unexplained cluster is not computed.** Sharing a mechanism is
  judgment - `PL-G424`'s 27 came from a manual clustering pass - and
  `CLAUDE.md` refuses a tool that guesses at the judgment half.
- **No owner-blocked count and no filed-per-closed ratio.** The owner ruled
  out backlog counts and ratios on 2026-09-19 (above); closures are already
  `bin/docket trend`'s.

**The question.** The re-entry signal - the one the owner's "unknown
generator" check rests on - has a record already, but in prose: since
`PL-KVDK` every apparatus item's triage writes a `**Generator check.**` line
saying whether it re-enters a closed fix or is a post-close instance of a head,
and about 113 item files carry re-entry wording there today. `root-cause-of:`
does not carry it: members filed after their head closed number 2 in the whole
store, against `PL-04KR`'s hand count of 14 of 37 in two days. Reading that
prose with a regex is the "sharper heuristic" `.claude/rules/apparatus-standard.md`
refuses.

**Recommendation:** record it as a field the triage generator check writes -
`reenters: PL-XXXX`, naming the closed item or head whose fix should have
covered this one - and have `inflow` count it per period beside `filed`, and
name any closed item that three or more filings re-enter as a generator whose
fix did not hold (triage.md's own rule for three post-close instances). Backfill
it once from the existing `**Generator check.**` lines, by a subagent reading
them, so the trend has history from 2026-09-22 rather than starting empty. It
costs a field in `model.py` and `checks.py`, a sentence in
`.claude/skills/docket/modes/triage.md`, and the one-off backfill. The
alternative is to ship `inflow` without a re-entry column, which leaves the
owner's question answered by hand.

**Still to build after the answer:** the re-entry column and its test; the
release-time report, silent while `PL-04KR`'s pre-registered expectations hold
(new paths per item at or below 0.13, no P1 apparatus filings, re-entry not
rising); the Done-when and `verify:` rewritten in the decided form, since the
current `verify:` names a test this build did not write; and `PL-04KR`'s
sentence that the 30-day bound distinguishes its signal 1 from raw recurrence
marked superseded by the measurement above.

### Answered (project owner, 2026-10-11, ratified, over recording the field going forward only and over shipping `inflow` without a re-entry column)

The recommendation above, whole: a `reenters: PL-XXXX` field the triage
generator check writes, backfilled once from the existing `**Generator check.**`
lines by a subagent reading them, counted by `inflow`.

**Done when.** `bin/docket inflow` reports, per period, the columns built
2026-10-11 plus the count of filings carrying `reenters:`, and names any closed
item that three or more filings re-enter as a generator whose fix did not hold;
`reenters:` is parsed in `model.py`, validated in `checks.py` (it must name an
item that exists and was closed before the filing), and asked for by the
generator check in `.claude/skills/docket/modes/triage.md`; the backfill has
written it on every item whose generator-check line names a closed fix that did
not reach it; at release time `inflow` prints only where one of `PL-04KR`'s
pre-registered expectations fails (new paths per filing above 0.13, a P1
apparatus filing, re-entry rising); and a test under
`subprojects/docket/tests/test_inflow.py` pins the re-entry count and the
three-re-entry naming.

### Built after the answer, 2026-10-11

`reenters:` is a list field (`model.py`, written by `bin/docket set
--reenters`), and `reentry_faults` holds each id to a `done` item closed on or
before the filing's `added:`. **`done`, not merely closed:** a `dropped` item
shipped no fix, so it cannot be a fix that did not hold. Triage's generator
check (`.claude/skills/docket/modes/triage.md`) now asks for the field on both
of its fix-did-not-hold outcomes, the post-close head instance and the
re-entry. `inflow`'s `re-entry` column counts it over `filed` only, the filings
no head explained, so a sweep's members cannot read as fixes failing; the
three-re-entry naming counts the same population.

The release-time report sits in `docket release` itself, printed under the
notes in a dry run and a cut alike, not as a step in `release.md`: in code it
cannot be skipped. It reads the last complete week (the last one that ended
before today, since the week still being filed into reads low) and prints only
the predictions that week broke. Three calls made while building it, each with
one clearly correct option:

- **The band test leaves out the generator tier.** Since 2026-09-21 a head
  recording `generator: live` is raised to `P1` by rule and keeps it once spent,
  and an `impairs-generators:` item ranks with it. `PL-04KR`'s baseline (0, 2,
  1, 0 `P1` filings a week) predates that. From 09-28 to 10-11, heads and such
  items were 8 of the 9 `P1` apparatus filings, so counting them would have
  every cut report a generator that has already been found and ranked. `P0`
  counts with `P1`.
- **`P1` only, not `PL-04KR`'s "P1/P2 ... staying at zero".** `P2` apparatus
  filings were never zero: 3 to 185 a week in the table above. Read literally,
  that prediction had already failed when it was written.
- **Rising means more re-entries in the last complete week than the week
  before**, by count; the weeks compared are both seven days long.

What a cut would print on 2026-10-11 is one line: the week of 09-28 had one
`P1` apparatus filing outside the generator tier. That filing is `PL-0YYV`, a
`safety`-classed simulator refactor whose only apparatus path is
`.claude/rules/core-domain.md`. It counts under `PL-4NZ7`'s population (any
filing naming an apparatus path, whatever its lane) and is reported as that
population defines it. The line stops appearing once the week of 10-05 becomes
the last complete week.

**`recurrences:` is a different fact and stays separate.** It is written by
`bin/docket new` on the *matched* item when a title match finds the same
defect filed again, and the matched item may still be open. `reenters:` is
triage's judgment, written on the new item, that a shipped fix failed to reach
it.

`PL-04KR`: its two path and cluster signals and the 30-day-bound sentence are
marked superseded, with this item as the reason. Its Done-when keeps its last
two sentences, the three release checks recorded in its file, and its
`verify:` now names the third of those checks instead of `test_trend.py`'s
`test_the_re_entry_rate`, which this design will never write.

**The backfill, 2026-10-12.** A subagent read the `**Generator check.**`
paragraph of all 475 files carrying one: 293 in full, and 182 that use none of
the words for re-entry, closing, instances, siblings, recurrence or fixes. It
wrote `reenters:` on 89, through `bin/docket set`, so `docket check` validated
each one, and the diff is 89 one-line additions. I spot-checked four against
their lines. Two calls, each with one clearly correct option:

- **`PL-ZYHX` gets none.** Its line names `PL-LN69` "closed as spent", but
  `PL-LN69` was dropped as "answered rather than built", so it shipped no fix.
  `done` stays the rule: 51 of 55 heads are `done` and 3 `dropped`.
- **The 20 `PL-R417` sweep members phrased "the gap closed PL-X's fix left"
  get none.** Their lines stop short of saying re-entry, and all 20 were filed
  while `PL-R417` was open, so `inflow` counts them under `+head` and none of
  them could move a re-entry count. The other 10 skipped lines are
  ambiguous about which item was re-entered, and are left unwritten for that
  reason.

First reading with the column: 33, 19 and 11 re-entries in the weeks from
09-21, 09-28 and 10-05, falling. Eight closed items are named as re-entered by
three or more filings. Three of them already have a successor head
(`PL-4Q9B` by `PL-MT3R`, `PL-9HD1` by `PL-HXJY`, `PL-WFFX` by `PL-979D`); the
five without one are `PL-4097`. A cut on 2026-10-12 prints nothing: the week of
10-05 had fewer re-entries than the week before, 0.02 new paths a filing, and
its one `P1` is a head.
