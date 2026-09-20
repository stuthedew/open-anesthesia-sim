---
id: PL-6T44
title: docket next and wave read status: blocked literally, so an item whose blockers have all closed ranks as unstartable while docket check already prints it as promotable
priority: P2
effort: S
status: done
classes: defect
feature: docket-store
milestone: v0.4.34
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_plan.py
added: 2026-09-17
closed: 2026-09-20
pr: 769
payoff: stops the queue reading as more stuck than it is by naming, where work is chosen, the blocked items whose blockers have all closed - the one that unblocked three more of v0.5.0's own scope was invisible to docket next
verify: grep -q 'def test_an_item_whose_every_blocker_has_closed_is_reported_promotable' subprojects/docket/tests/test_plan.py
root-cause-of: PL-JFQ3, PL-8G48, PL-CHQY
---

**Problem.** docket next and wave read status: blocked literally, so an item whose blockers have all closed ranks as unstartable while docket check already prints it as promotable

**Why it matters.** It makes the current milestone read as more stuck than it
is, at exactly the moment a session is deciding what to work on. Measured
2026-09-17: `bin/docket wave` reports v0.5.0 — the case you can branch as "19
closed, 7 open" and five of those seven carry `status: blocked`, so `bin/docket
next` offers only `PL-MN4J` and `PL-49R8` from the whole of the milestone's
Required scope. But `PL-LPLD`'s sole blocker `PL-25KS` and `PL-W7H9`'s sole
blocker `PL-8PSW` both closed in v0.4.26, and `bin/docket check` says so
outright — "PL-LPLD: every blocker has closed; it is ready to promote", the
same for `PL-W7H9` and five others. `PL-LPLD` is the head of the chain the
bookmark half of the milestone sits behind (`PL-LPLD` → `PL-CTD7` → `PL-B8MK`
→ `PL-Z3W6`), so the one item that unblocks three more of the milestone's own
scope was invisible to the command that ranks work.

**The two halves are already computed; nothing joins them.** `check` derives
"every blocker has closed" from the same store `next` and `wave` read, so this
is not new analysis — it is one reading not reaching the other two. A session
that runs `next` without also running `check` never learns the item is
startable, and `next` is the command the workflow prescribes for picking.

**Decision needed.**

1. `next` and `wave` treat a `blocked` item whose `blocked-by` ids have all
   closed as startable, and say so in the reason line ("was blocked; every
   blocker closed"). Ranks it where it belongs without editing the store.
2. They leave the ranking alone but name the promotable ids in the same output
   `check` does, so the reader sees them at the moment of choosing.
3. Promotion stays a grooming action and the advisory is made an error, which
   forces the flip before the next `make check` passes.

Option 1 changes no item file and needs no pass to be run; option 3 puts a
queue edit in front of unrelated work. Weigh 1 against 2 on whether a
recomputed status should override what an item declares.

**Found by.** A "what should we do next" session on 2026-09-17, which reached
the answer only by reading `blocked-by` on all five and resolving each root by
hand.

**Done when.** `bin/docket next` and `bin/docket wave` account for an item whose
`blocked-by` ids have all closed in whichever way the decision above settles -
ranked as startable with the reason line saying so, or named in their own output
the way `bin/docket check` already names them - and a test under
`subprojects/docket/tests/` drives an item all of whose blockers are closed.

## Evidence for the decision above, measured by the `PL-8G48` pass (2026-09-20)

**The decision is not answered here.** What follows is the count option 1 rests
on, produced by working a whole batch of the advisory by hand.

`bin/docket check` named four items as "every blocker has closed; it is ready to
promote". Read against the tree, **one of the four was promotable**:

| item | what the tree said | disposition |
| --- | --- | --- |
| `PL-8PS6` | carrier exists, slot specified and empty | `ready`, `P1` |
| `PL-439V` | the work had already landed inside `PL-FG9D` | `done` |
| `PL-WZVZ` | no second machine, and its surface is deferred by a standing rule to `PL-TH35`/`PL-R1WQ` | stays `blocked`, re-pointed |
| `PL-CTD7` | a user-facing question was written into it after its last triage | `needs-decision`, `P1` |

`PL-JFQ3`'s nine, measured the same way four days earlier, came to five
startable, three blocked on something nobody had written down, and one already
done by another item. **Across both passes: 13 items, 6 genuinely startable.**

**What that number is evidence about.** Option 1 makes `next` and `wave` rank a
`blocked` item whose blockers have all closed *as startable*. On this evidence
that ranks roughly half of them wrongly - and the three failure modes are not
symmetrical. An item that is already `done` or that needs a decision is a wasted
pick a session recovers from in minutes. `PL-WZVZ` is the expensive one: it
would have been ranked startable **and** pulled to `P1`, because leaving
`blocked` is what ends the `anticipated` exemption - so a recomputed status
would have put an unbuildable item into the top band and the debt gate without
anybody deciding to. That is the specific cost of "a recomputed status
overriding what an item declares", which the `Decision needed.` above names as
the axis to weigh 1 against 2 on.

**It is not evidence that the advisory is wrong**, and the distinction matters.
"Every blocker has closed" was true for all four; what it cannot see is whether
anything *else* holds the item, which is the judgment three of these four
needed. Option 2 - name the promotable ids in `next` and `wave` without
re-ranking them - is the option this measurement does not argue against.

**One `blocked-by` edge that would have survived any of the three options:**
`PL-WZVZ` now names `PL-TH35` and `PL-R1WQ`, and `PL-CTD7`'s closed edge is
cleared. Both were written by hand, by the session that read the tree.

## Decision, and one half of the premise that did not survive contact (2026-09-20)

**Option 2, and the title's claim about `wave` was wrong.**

**`wave` never read `status` and needs no change.** `roadmap.py` contains no
literal `status == "blocked"` comparison - `gate_status` is not even given item
statuses, only `closed_ids`, `known_ids` and each item's `blocked-by`, and
`_blockers_outside` skips a blocker that has closed. `format_wave` reads no
status either. The behaviour this item asks for on that side already exists and
has been pinned by a test since `PL-9SH6`:
`test_a_blocker_that_has_already_closed_holds_nothing` in
`subprojects/docket/tests/test_roadmap.py`, whose docstring records the same
hour-long stale `blocked` that prompted this item. What the 2026-09-17 reading
saw was `wave` counting five genuinely open gate entries, which is correct; it
does not distinguish them, and `next` is where that mattered.

So the defect is `plan._startable`'s `status != "blocked"` alone - one filter,
not two commands. `checks.py` says so in its own comment on
`_ready_with_an_open_blocker`: "`plan.py` filters on `status != 'blocked'` and
never opens `blocked_by`".

**Option 2 was taken on the evidence already in this item**, which the
`PL-8G48` pass measured and which argues against option 1 rather than for it:
6 of 13 items reached this way were genuinely startable, and ranking the other
7 would have put `PL-WZVZ` - unbuildable, with no second machine - into `P1`
and onto the debt gate, because leaving `blocked` is what ends the
`anticipated` exemption. Option 3 was refused for the reason the brief gives:
it puts a queue edit in front of unrelated work. A recomputed status does not
override what an item declares; the ids are named where the choosing happens
and a person still reads each against the tree.

This was a session's call rather than the project owner's: the consequence is
one internal structure of the apparatus, no learner sees it, and the
safety-critical standard does not reach it. Reopen it on ordinary evidence.

**What landed.** `plan.promotable` is the one reading, and `checks.py` now
derives its "every blocker has closed" advisory from it rather than computing
the same set a second time, so the advisory and the ranking cannot disagree.
`cli._say_promotable` prints the ids on both of `next`'s paths - including the
empty ranking, which is the case it exists for: a lane whose whole remainder is
stale `blocked` said "Nothing is ready to start" and named nothing.

Milestone blockers are deliberately left out: they clear when a scoping round
happens, which takes the roadmap to answer. `PL-162Y` is whether `next` should
name those too.

**Measured on a scratch store, 2026-09-20.** Before: `next` printed "2 grooming
advisory(ies) pending" and no id, while `check` printed "PL-BBBB: every blocker
has closed; it is ready to promote". After: `next` names `PL-BBBB` on both
paths.
