---
id: PL-LBNN
title: Since PL-CZXN no check measures whether a branch weakens a test of the apparatus: the owner's 2026-10-24 answer on PL-7FPD covers the simulator's tests of what the interface displays, and the assertion check PL-CZXN removed read the apparatus tests as well
priority: P3
effort: M
status: dropped
classes: defect
touches: tools/diff_mutation.py
added: 2026-10-24
closed: 2026-10-24
reason: Reopens PL-CZXN's ratified 2026-10-19 decision, which named this gap when it was taken, with no new evidence: no weakened apparatus test has been observed, the apparatus standard prices one at a session's cost, and the owner's 2026-10-24 answer on PL-7FPD reopened only the display half on safety grounds
---

**Problem.** Since PL-CZXN no check measures whether a branch weakens a test of the apparatus: the owner's 2026-10-24 answer on PL-7FPD covers the simulator's tests of what the interface displays, and the assertion check PL-CZXN removed read the apparatus tests as well

Split from `PL-7FPD` while triaging it on 2026-10-24. `PL-7FPD`'s title names both halves of the gap. The owner's answer, relayed by the coordinator, brings back a check for the simulator's tests of what the interface displays, so `PL-7FPD`'s done-when now covers only the simulator half. This item keeps the apparatus half on record, so that it is not lost when `PL-7FPD` closes. A weakened apparatus test costs a session rather than a patient, which is why `.claude/rules/apparatus-standard.md` holds those tests to a lower bar. mutmut mutates only `src/`, so the mutation check cannot reach the apparatus as it stands.

**Why it matters.** `PL-CZXN`'s ratified decision (project owner, 2026-10-19) already weighed this gap. Its brief says, under "What it does not cover, said so the trade is visible", that "a test of the apparatus ... is no longer measured by any check: the old check covered both". The owner's 2026-10-24 answer on `PL-7FPD` reopened only the display half, on safety grounds. `.claude/rules/apparatus-standard.md` says a weakened apparatus test costs a session rather than a patient, and no instance of one has been observed since.

**Done when.** Not to be done: see the reason.

**Generator check.** A one-off: a coverage trade that a ratified decision accepted, not a reader misreading a fact.
