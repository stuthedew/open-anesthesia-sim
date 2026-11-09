---
id: PL-FCM3
title: bin/docket wave reports 'N waiting on work outside it' without naming or counting those items, so the gate understates what clearing it costs
priority: P2
effort: S
status: done
classes: defect, infra
feature: gate-remaining-cost
milestone: v0.4.34
touches: subprojects/docket/src/docket, subprojects/docket/tests
added: 2026-09-20
closed: 2026-09-20
pr: 761
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

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground". This item is also named in paragraphs quoted in the brief of `PL-Z34C`.

> - PL-FCM3 (S) `bin/docket wave` reports how many gate entries wait on work outside the gate and never names or counts those items, so the beat understates what clearing the gate costs - measured 2026-09-20 as 1 startable entry plus 13 off-gate prerequisites — closed in v0.4.34
