---
id: PL-PV6H
title: show on an id that exists only on a branch no live hold names, such as a stranded capture the digest lists, still prints only 'no item matching', since PL-140X points at the branch only where a hold names the id
priority: P3
effort: S
status: done
classes: defect
feature: one-snapshot
milestone: v0.5.12
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-26 triage pass
added: 2026-09-26
closed: 2026-09-26
pr: 1059
payoff: show on an id the digest lists as only on a branch names that branch and how to recover it instead of a dead end, for about 0.3 s on a miss
verify: grep -q 'def test_show_names_the_branch_of_a_stranded_id_no_hold_names' subprojects/docket/tests/test_cli.py
---

**Problem.** show on an id that exists only on a branch no live hold names, such as a stranded capture the digest lists, still prints only 'no item matching', since PL-140X points at the branch only where a hold names the id

**Found 2026-09-26** while closing `PL-140X` (show names the branch holding an
item absent here). `PL-140X` scoped the pointer to an id a live hold names, and
`cli._say_held_elsewhere` stays silent otherwise, so the ordinary typo costs no
ref walk. On this checkout the session-start digest lists `PL-0T5X` and
`PL-7XGR` under "Only on a branch, not in this checkout", and `bin/docket show`
on either prints only `no item matching` and exits 1: no live hold names them,
so the new lines do not fire. `bin/docket stranded` is where they are read.

**Why it matters.** The digest names these ids and `show` is the command a
session reaches for next, so it is the same dead end `PL-140X` removed for held
ids. Whether the not-found path should pay a stranded read on every miss to
cover it is the judgment this item leaves to triage.

**Reproduced 2026-09-26 against 78b1a02b.** `PL-0T5X` and `PL-7XGR` have since reached this checkout, so they no longer show it. `bin/docket stranded --no-fetch` now lists `PL-H2V3`, `PL-WXPR` and `PL-Z909` as only on a branch, and `bin/docket show` on each prints only `no item matching` and exits 1.

**Decided at triage 2026-09-26, by measurement: the miss pays the stranded read.** `bin/docket stranded --no-fetch` took 0.98-1.00 s over three runs across 23 branch refs. A run that loads the store and asks git nothing (`bin/docket status --no-git`) took 0.67-0.72 s, so the ref walk itself costs about 0.3 s. A miss costs 1.05-1.16 s today, and a hit 1.05-1.12 s. The not-found path is the error path, so about 0.3 s more there is cheap for the pointer. A hit pays nothing, and a typo still gets the single line, because the walk finds no file. This is the read without a fetch. A fetch on every miss would cost the network, and nothing here decides one.

**Done when.** `bin/docket show` on an id that exists only on a branch no live hold names prints that branch and the recover line `stranded` gives, and still exits 1. A typo still prints only `no item matching`. A test in `subprojects/docket/tests/test_cli.py` holds both.

**Generator check.** One-off sibling of `PL-140X` (closed 2026-09-26), which scoped this out so a typo would cost no ref walk, and filed it. The fact, where an id absent from this checkout lives, is already read by `stranded`, which `show` consults only for held ids. No head's `misread:` states it.
