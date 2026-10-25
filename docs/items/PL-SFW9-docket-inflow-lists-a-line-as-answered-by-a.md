---
id: PL-SFW9
title: docket inflow lists a line as answered by a successor head whatever the successor's status, so a line re-entered after its successor closed spent still reads as settled, where a no-successor answer is reopened by three later filings; PL-5DZ8 read as answered by PL-4S6C (done) while PL-TSXD re-entered it (found recording PL-N4FP)
priority: P1
effort: S
status: done
classes: defect
feature: one-source-of-truth
milestone: v0.6.3
touches: subprojects/docket/src/docket/inflow.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_inflow.py, subprojects/docket/README.md
added: 2026-10-24
closed: 2026-10-25
pr: 1757
payoff: a mechanism that starts producing again after its successor head closed shows up as open in docket inflow, instead of being found only by a session reading items by hand
verify: grep -qE 'def test_[a-z_]*successor[a-z_]*(closed|after)' subprojects/docket/tests/test_inflow.py
impairs-generators: inflow.analyze builds successors from every head whose reenters names a line, whatever that head's status, and counts no filings after the head closed, so a line re-entered after its successor closed reads as settled and no generator is recorded
---

**Problem.** docket inflow lists a line as answered by a successor head whatever the successor's status, so a line re-entered after its successor closed spent still reads as settled, where a no-successor answer is reopened by three later filings; PL-5DZ8 read as answered by PL-4S6C (done) while PL-TSXD re-entered it (found recording PL-N4FP)

**Why it matters.** `docket inflow` is how the queue learns that a closed head's fix did not hold. `inflow.analyze` treats a line as answered by a successor head whatever that head's status, and it counts no filings made after the successor closed. The `answered` branch for a `no-successor:` answer does count them, through `_reentered_after`. So a mechanism that starts producing again after its successor closes reads as settled, and no generator is recorded for it. `PL-5DZ8`'s line is the worked case. It reads "successor PL-4S6C (done), PL-N4FP (done)". Yet `PL-TSXD`, added 2026-10-19, re-entered it after `PL-4S6C` closed on 2026-10-12. `PL-N4FP` was found only because a session read the items by hand.

**Reproduced 2026-10-24.** `bin/docket inflow` lists `PL-5DZ8  by PL-4S6C, PL-Q80R, PL-TSXD, PL-N4FP` with `successor PL-4S6C (done), PL-N4FP (done)`, and nothing marks the line as open again. In `subprojects/docket/src/docket/inflow.py`, the `successors` comprehension in `analyze` has no `_reentered_after` test, while `answered` has one.

**Done when.** A line whose successors have all closed lists as open again once `MIN_ROOT_CAUSE_ITEMS` filings re-enter it after the last successor closed, just as a `no-successor:` answer does. A test in `subprojects/docket/tests/test_inflow.py` pins this.

**Generator check.** This is a defect in the machinery that finds generators, so it is recorded as `impairs-generators:` and ranks with a generator.
