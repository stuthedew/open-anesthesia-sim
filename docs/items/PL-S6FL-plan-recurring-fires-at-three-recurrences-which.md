---
id: PL-S6FL
title: plan.recurring fires at three recurrences, which is a cluster of four items, where the generator rule it borrows MIN_ROOT_CAUSE_ITEMS from counts three items - so the slug-rename cluster that was recorded as a textbook generator peaks at two and never fires
priority: P2
effort: S
status: done
classes: infra
feature: recurrence-signal
milestone: v0.5.0
touches: subprojects/docket/src/docket/plan.py
added: 2026-09-20
closed: 2026-09-20
pr: 794
payoff: makes the generator-candidate signal fire on a three-item cluster, which is what the rule it borrows its threshold from means - the slug-rename cluster was invisible to it
verify: grep -q 'def test_the_floor_is_two_recurrences_because_the_item_is_the_first_filing' subprojects/docket/tests/test_plan.py
---

**Problem.** `plan.recurring` gated on three recurrences, which is a cluster of
four items, where the generator rule it borrows `MIN_ROOT_CAUSE_ITEMS` from
counts three items.

**The off-by-one, verified in the code rather than argued.**
`model.recurrence_count` returns `len({found.identifier for found in
recurrences_of(item) if found.identifier})` - the count of *distinct other
filings* absorbed onto an item. So an item carrying N recurrences is a cluster
of N+1 items, itself included. `CLAUDE.md` defines a generator as the root
cause of three or more **items**, so the equivalent recurrence count is two.
Gating on three demanded a fourth filing.

**What it cost, measured.** Replaying the recorded clusters, the slug-rename
cluster - `PL-LBR6` with `PL-5QLP` and `PL-QMC0`, three filings, recorded as a
generator by hand and the cluster that motivated `PL-TZ7T` - peaks at two and
never fired. A textbook generator was invisible to the machinery built to find
one.

**Closed by `PL-DGP0`'s commit**, which derives `MIN_RECURRENCES` as
`MIN_ROOT_CAUSE_ITEMS - 1` rather than writing a second number down, so the
code expresses the reasoning instead of restating a coincidence. That also
keeps the single-threshold property the original case wanted; it was right
about the principle and wrong about the arithmetic.

**Decision (project owner, 2026-09-20, ratified**, over the literal three
`PL-X5JR`'s design specified.) The owner has said they were agreeing with
recommendations on this rather than specifying, so this is a ratification and
carries a ratification's bar: reopenable on ordinary evidence.

**It was diagnosed twice, independently, which is the feature's own case.**
This item and `claude/recurrence-signal-feature-3hnynt`'s `52c6d698` reached
the same off-by-one within the hour, from opposite ends - one from the roadmap
side, one from the code. Two sessions paid for one diagnosis, in the very
feature built to stop that happening, and neither could see the other because
the detection only warns at `bin/docket new` and neither filing declared the
other's path. `PL-THLT`'s working-tree key is what would have caught it.
