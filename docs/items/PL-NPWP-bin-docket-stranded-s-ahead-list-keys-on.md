---
id: PL-NPWP
title: bin/docket stranded's ahead list keys on textual difference between the base's copy and a branch's, so a branch holding a stale copy is reported forever and no amount of recovery can empty the list - which is the completion test PL-DZM1 was written against
priority: P2
effort: M
status: ready
classes: defect
feature: stranded-report-fidelity
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-21
payoff: stranded's list can reach empty again, so a row in it means somebody has work to recover rather than that a fork is old
verify: grep -q 'def test_a_branch_copy_identical_to_the_bases_is_not_reported_ahead' subprojects/docket/tests/test_vcs.py
---

**Problem.** bin/docket stranded's ahead list keys on textual difference between the base's copy and a branch's, so a branch holding a stale copy is reported forever and no amount of recovery can empty the list - which is the completion test PL-DZM1 was written against

**Measured 2026-09-21.** `bin/docket stranded` reported 7 items the default
branch holds and a branch edits, across 5 distinct refs. Three of those refs -
carrying 5 of the 7 items - are not on the remote at all: it holds 7 heads, and
those three survive only as this checkout's own remote-tracking pointers, which
`fetch_remote` refuses to prune on purpose (`PL-HKF4`). Diffing three of the
reported copies against the base's shows the branch copy is the *shorter* one in
every case, by 14, 48 and 75 lines: the base has grown past a fork, which is not
an edit the base is missing.

**Why it matters.** This is the second compounding-friction test in `CLAUDE.md`
- an advisory being routed around. The list cannot reach empty by any action a
reader can take, because a copy forked before the base moved differs textually
forever, so every run prints rows that mean nothing and the reader learns to
skim a report whose whole purpose is to be read when it is rare. `PL-DZM1` was
written against emptying this list as its completion test, which no amount of
recovery can satisfy. The direction of the error is the quiet one: a real
stranded edit arrives in a list already full of false ones.

**Done when.** A branch copy that differs from the base's only because the base
moved on is not reported as ahead, so a checkout with nothing genuinely stranded
prints an empty list; and a test in `subprojects/docket/tests/test_vcs.py` drives
a base that has advanced past an untouched branch copy.
