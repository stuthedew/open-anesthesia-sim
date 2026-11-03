---
id: PL-CJGH
title: docket inflow counts a deliberate sweep recorded only as a feature: as ordinary inflow, so PL-K88Z's one-source-of-truth inventory gave 29 filings and 13 re-entries in the week of 2026-10-19 with +head at 0; no field records that an item was filed by a sweep
priority: P3
effort: M
status: ready
classes: defect
feature: convergence-visibility
touches: subprojects/docket/src/docket/inflow.py, subprojects/docket/src/docket/model.py, subprojects/docket/tests/test_inflow.py, subprojects/docket/README.md
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-11-03
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
