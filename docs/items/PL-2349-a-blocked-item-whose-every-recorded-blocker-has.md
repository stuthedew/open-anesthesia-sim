---
id: PL-2349
title: A blocked item whose every recorded blocker has closed has no status to move to short of ready, which demands verify: and payoff:, so the session closing the blocker leaves status: blocked standing as a false claim - PL-R417's closure on 2026-10-11 left five that way, and PL-5XG1 and PL-ZYHX sat 15 and 8 days
status: untriaged
feature: blocked-means-blocked
touches: subprojects/docket/src/docket/checks.py, .claude/skills/docket/modes/close-out.md
added: 2026-10-11
---

**Problem.** A blocked item whose every recorded blocker has closed has no status to move to short of ready, which demands verify: and payoff:, so the session closing the blocker leaves status: blocked standing as a false claim - PL-R417's closure on 2026-10-11 left five that way, and PL-5XG1 and PL-ZYHX sat 15 and 8 days

**Evidence, 2026-10-11.** `bin/docket check` names seven items "every blocker
has closed; it is ready to promote". Five were released today by `PL-R417`
(the last live generator head) closing in #1392: `PL-JHHC`, `PL-LNNL`,
`PL-QFCR`, `PL-RLS3`, `PL-VF3C`. The closing session followed close-out step 1
as far as the store let it - it read each one and wrote "Nothing else holds
it" into the brief - and then left `status: blocked`, because the four open
statuses (`untriaged`, `ready`, `needs-decision`, `blocked`;
`docket.model.OPEN_STATUSES`) offer nothing between waiting and committed:
`_check_item` in `subprojects/docket/src/docket/checks.py` refuses `ready`
without a `verify:` command and a `payoff:` line, and none of the five carries
either. The other two are older and plainly stale: `PL-5XG1` since `PL-V1Y7`
closed 2026-09-26, `PL-ZYHX` since `PL-40SJ` and `PL-YXFF` closed 2026-10-03.
The project owner's question that raised it: "shouldn't all be at least marked
unblocked once no longer blocked?"

**History - this is `PL-6T44`'s fact, read from the writer's side.** `PL-6T44`
(closed 2026-09-20, `root-cause-of: PL-JFQ3, PL-8G48, PL-CHQY`) found three
grooming passes caused by stale `blocked` statuses and fixed the *readers*:
`next` and the close-time print now name the candidates, and deliberately do
not rank or promote them, because 7 of 13 measured were held by something
`blocked-by` did not say (`plan.promotable`'s docstring). That made the stale
state visible; nothing made it leave. `PL-0H5D` (ratified 2026-09-21) then
settled that a holding condition `blocked-by` cannot express gets an item of
its own to block on - so `status: blocked` with every blocker closed is now
always a false statement, never an inexpressible true one. Not recorded as a
live generator head: two items reached the store from this mechanism since
`PL-6T44` closed (`PL-0H5D`, `PL-MXTY`), and its cost shows as stale state
rather than item inflow.

**Decision needed.** How a blocked item leaves `blocked` once nothing blocks it.

- **(a) A fifth status, `unblocked`** - the owner's proposal. Cheap and honest
  at the moment of closure, and never fails a pull request. But the item is
  still unstartable (`next` cannot offer an item without `verify:`), so the
  pile it sits in is the same unshaped pile under a truer name; every reader
  of status - `next`, `wave`, `gate`, the lanes, and the `anticipated`
  exemption from the debt gate, which ends on leaving `blocked` - has to learn
  a fifth value; and nothing ever moves an item out of it.
- **(b) Refuse the false state instead of naming it.** `bin/docket check`
  turns "`status: blocked`, every item in `blocked-by` closed" from the
  advisory it is into an error, so the pull request that closes a blocker
  cannot go green until each item it released has moved: to `ready`, with its
  `verify:` and `payoff:` written, or to the real holding condition in
  `blocked-by` (an item for it, per `PL-0H5D`). No new status; the judgment
  stays the session's, and only the falsehood is refused - the shape
  `PL-JNWS` gave a `needs-decision` item left standing beneath its answer.
  Milestone blockers stay advisory: scoping is not a closure.
- **(c) Keep the advisory and the close-out rule as they are.** Already
  measured: it produced today's seven.

**Recommendation: (b).** It is the only option under which the store tells the
truth *and* the released item reaches `next`; (a) fixes the label and not the
outcome. What it costs: the session closing a blocker pays a few minutes per
released item, often outside its own area; the pull request that adds the
error must clear every current stale item first, or `main` goes red; and two
branches - one closing an item, one adding `blocked-by` on it - can each pass
alone and leave `main` red after both merge, which is rare and fixed by the
next session's disposition. Where `verify:` depends on a design the building
session has not chosen (`PL-JHHC`), the command is written for the end state,
not the shape.

**Why it matters.** `status` is the one field every reader of the queue takes
at its word. Left false, the released work is invisible to `bin/docket next`
for as long as nobody grooms it, and the advisory that names it repeats every
run - the "earns its place every run" failure `CLAUDE.md` retires checks for.

**Done when.** The decision above is recorded, and under (b): `bin/docket
check` errors on a `blocked` item whose every item blocker has closed, with a
test; close-out step 1 and the triage mode say a released item leaves
`blocked` in the closing pull request; and no item on `main` is in that state.
