---
id: PL-SCB4
title: The store has no status for an item whose decision is made but whose work waits on a measurable condition, so it stays needs-decision and holds a gate open
priority: P2
effort: M
status: dropped
classes: infra
feature: docket-store
touches: subprojects/docket
added: 2026-09-13
closed: 2026-09-19
reason: PL-Z34C now sits at status: blocked with its fifteen blockers declared, is absent from bin/docket gate's 177 open entries and is not offered by bin/docket next, so both stated harms are gone (verified 2026-09-19).
---

**Problem.** The store has no status for an item whose decision is made but whose work waits on a measurable condition, so it stays needs-decision and holds a gate open

**Why it matters.** `PL-Z34C` is the live case, found working the Gate 1 decision
batch on 2026-09-13. Its decision is made — retire `verify_required_from` — and
it still cannot be worked, because its trigger is the grandfathered set reaching
zero and the set is 15. All three available statuses say something false:
`needs-decision` says the next step is a decision, which it is not, and
`bin/docket gate` counts it as Gate 1 debt on that basis, so a gate that must
clear before v0.5.0 is held open by an item whose question is answered; `ready`
invites a session to pick up work it will immediately put down; `blocked` was
refused by `docket check`, correctly, because `blocked-by` names an item and the
item that drains the set (`PL-J49T`) is already done.

**Not urgent, and the reason is worth recording.** `PL-Z34C` itself declined to
file this, "since nothing else in the store has wanted it". That is what changed:
the general shape — a decision recorded against a trigger nobody is tracking —
now has two instances, and the second one is what makes it a gap rather than a
one-off workaround.

**Where.** `subprojects/docket/src/docket/model.py` (the status set),
`checks.py` (what `blocked-by` accepts), `plan.py` (what `gate` counts as debt).

**Decision needed before any code.** Whether this is a new status or a field on
an existing one — a `blocked-by` that accepts a condition rather than an id would
reuse the machinery that already exists, and a new status would have to be taught
to every command that branches on one.
**Done when.** The decision above is recorded, the mechanism it chooses is
built with a test, and `PL-Z34C` (retire `verify_required_from` and its
grooming advisory once the grandfathered set reaches zero) carries the new
state - so `bin/docket gate` stops counting a Gate 1 entry as debt on the
strength of a question that is already answered, and `bin/docket next` stops
offering an item whose work cannot start.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground".

> **Two more from the second 2026-09-13 triage pass**, which folded in the two items that the first pass had to defer. It also folded in six items that merged in from other sessions while it ran. `PL-SCB4` (the store has no status for an item whose decision is made but whose work waits on a measurable condition) is wholly in the workflow lane. It is in exactly the position of the first thirty: captured after the 2026-09-06 freeze, `P2`, neither `safety` nor `science`, and apparatus held to `.claude/rules/apparatus-standard.md`'s lower bar. It is worth one extra sentence, because it is *about* this gate. `PL-Z34C` is the live case. Its question has been decided, and it keeps Gate 1 open because no status records that. Admitting the fix would not release `PL-Z34C` any sooner than deciding `PL-Z34C` on its own terms does.
