---
id: PL-FCM3
title: bin/docket wave reports 'N waiting on work outside it' without naming or counting those items, so the gate understates what clearing it costs
priority: P2
effort: S
status: done
classes: defect, infra
feature: gate-remaining-cost
touches: subprojects/docket/src/docket, subprojects/docket/tests
added: 2026-09-20
closed: 2026-09-20
payoff: makes the beat say what clearing the gate actually costs, instead of reporting 4 items when it is 1 plus 13 prerequisites
verify: grep -q 'def test_the_gate_sizes_the_work_its_entries_wait_on_outside_it' subprojects/docket/tests/test_roadmap.py
---

**Problem.** bin/docket wave reports 'N waiting on work outside it' without naming or counting those items, so the gate understates what clearing it costs

**Why it matters.** The gate's whole job is to say what clearing it costs, so
the project can decide whether to start the milestone. `bin/docket wave` prints
`172 cleared, 4 open - 1 this gate can clear, 3 waiting on work outside it`,
which a reader takes as four items of work. Measured 2026-09-20 by walking
`blocked-by` transitively over open items from the four open entries: it is one
startable item plus **13 off-gate prerequisites**, all at depth 1. The line
names the hole and never sizes it, so the number a reader acts on is wrong by an
order of magnitude and nothing in the output says so.

**What the same measurement rules out.** None of the 13 is an oversight in the
freeze. Zero carry a debt class (`defect`, `safety`, `science`, `refactor`,
`perf`) and none is at `needs-decision`, so the membership rule excluded every
one of them deliberately. The fix is therefore *reporting*, not membership:
admitting them would put `PL-Z7LY` (pan the chart window) and eleven others into
a debt gate, which is `ROADMAP.md`'s own "do everything before doing anything"
failure. Twelve of the 13 are `PL-Z34C`'s blockers and are the grandfathered
`verify:` set, which clears as a side effect of ordinary work rather than by
being pushed.

**Done when.** `bin/docket wave` prints, for the entries it reports as waiting
on work outside the gate, how many distinct open prerequisites they have and
their ids, so the beat carries the real remaining cost. The walk is over
`blocked-by` on open items only.
