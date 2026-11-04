---
id: PL-CJGH
title: docket inflow counts a deliberate sweep recorded only as a feature: as ordinary inflow, so PL-K88Z's one-source-of-truth inventory gave 29 filings and 13 re-entries in the week of 2026-10-19 with +head at 0; no field records that an item was filed by a sweep
priority: P3
effort: M
status: done
classes: defect
feature: convergence-visibility
milestone: v0.6.15
touches: subprojects/docket/src/docket/inflow.py, subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_inflow.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_vcs_silence.py, subprojects/docket/README.md, tools/generator_check.py, .claude/skills/docket/modes/triage.md, docs/items/PL-K88Z-inventory-every-second-copy-of-a-shared-fact.md
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-11-03
closed: 2026-11-03
pr: 1998
payoff: a week the owner spends sweeping on purpose stops reading as rising inflow and failed fixes in the convergence report
verify: grep -q 'def test_a_sweep_s_filings_are_counted_apart' subprojects/docket/tests/test_inflow.py
---

**Problem.** docket inflow counts a deliberate sweep recorded only as a feature: as ordinary inflow, so PL-K88Z's one-source-of-truth inventory gave 29 filings and 13 re-entries in the week of 2026-10-19 with +head at 0; no field records that an item was filed by a sweep

**Reproduced 2026-11-03.** `bin/docket inflow --no-fetch` reports 117 filings,
29 re-entries and `+head` 0 for 2026-10-19..10-25. Read through
`docket.model`'s parser, 40 items in either lane were filed that week under
`one-source-of-truth`, and 13 of them carry `reenters:`. `docket.inflow` keeps
a filing out of the ordinary count only where an open head's `root-cause-of:`
names it (`_filed_by_head`). `PL-K88Z`, the inventory that filed them, has no
`root-cause-of:`, so its filings count as ordinary inflow. They also feed the
list of closed items that three filings re-enter, which names `PL-5DZ8` through
`PL-4S6C`, `PL-TSXD` and `PL-N4FP`, all of them from the same sweep.

**Why it matters.** The `+head` column exists so that a deliberate sweep does
not read as regression, and for a sweep recorded only as a feature it does not
work. A week the owner spent finding second copies on purpose then reads as a
week of rising inflow and failed fixes. The three-filings list can also point
at a fix that held, because a sweep found the instances it was asked to find.

**Done when.** `bin/docket inflow` counts a deliberate sweep's filings apart
from ordinary inflow, as it already does for a head's, and leaves them out of
the three-filings re-entry list. A test in `subprojects/docket/tests/test_inflow.py`
shows a sweep's filings counted apart. Before adding a field, check whether the
fact is already recorded, for example by the sweep's id leading the commit
that filed them (`vcs.leading_ids`). Read that record if it exists, and write
one only where none does. `subprojects/docket/README.md` says how a sweep
records itself.

**Generator check.** One-off. The column's rule keys on one record of a sweep,
`root-cause-of:`, and a sweep can be recorded another way. No other item
misreads the same fact.

**The generator pause does not hold this.** Since #1987 merged on 2026-11-03,
`bin/docket generators` marks `PL-9KSJ` and `PL-1ZZ0`, two guard heads, "still
generating", so the pause is on. The work is on
`subprojects/docket/src/docket/inflow.py`, which `docket.toml` lists in
`generator_paths`. It fixes a defect in the existing machinery that finds
generators, which the pause never holds, even while a head is live.

## Worked, 2026-11-03

**The record.** Git already records which item's work filed each item: the
commit that added the file leads with that item's id. `tools/generator_check.py`
read it in its own `creation_parents`, so the reading moved into
`docket.vcs.filing_parents` and both callers use it. Nothing recorded that an
item is a sweep, and no proxy can tell one from a busy close-out, so the item
records it in a new field, `sweep:`, prose saying what the sweep looks for.
`PL-K88Z` carries it now.

**The count.** `docket inflow` gives the sweep's filings their own `+sweep`
column, filed between the sweep's `added:` and `closed:`, and leaves them out of
`filed`, `re-entry` and the list of closed items that three filings re-enter. A
filing a head also names counts under `+head` only. The command asks git only
when some item records a sweep. Where git cannot answer, the column prints `?`
and the report says why, and a release that prints a miss says the counts
include the sweep's filings.

**What the brief overstated.** Not all 29 `one-source-of-truth` apparatus
filings that week came from `PL-K88Z`. Its commit filed 9 of them, 5 with
`reenters:`. The rest came from the design round's commit (`PL-2LB5`) and from
captures made while fixing the findings (`PL-LGDV`, `PL-TSXD`, `PL-JS6P` and
others). Those are ordinary inflow under the capture rule. So the week now
reads 108 filed, 24 re-entries and 9 under `+sweep`. `PL-5DZ8` stays in the
three-filings list, because `PL-4S6C`, `PL-Q80R` and `PL-N4FP` still re-enter
it, and none of them is the sweep's.

**One behavior change outside inflow.** `creation_parents` kept the newest
commit that added an item file. 25 items on `main` were added twice, by a
restore or a recovery, and for 13 of them the two commits lead with different
ids. `filing_parents` keeps the oldest, the commit that produced the item, so
those 13 spawn counts in `tools/generator_check.py` now credit the item whose
work filed them.

**A limit, documented in the README.** A pull request that closes a sweep beside
other items leads its squash commit with all their ids, so what those items'
work filed in it counts as the sweep's too.
