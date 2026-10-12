---
id: PL-2349
title: A blocked item whose every recorded blocker has closed has no status to move to short of ready, which demands verify: and payoff:, so the session closing the blocker leaves status: blocked standing as a false claim - PL-R417's closure on 2026-10-11 left five that way, and PL-5XG1 and PL-ZYHX sat 15 and 8 days
priority: P2
effort: M
status: ready
classes: defect
feature: blocked-means-blocked
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_checks.py, .claude/skills/docket/modes/close-out.md, .claude/skills/docket/modes/triage.md, docs/items/PL-JHHC-a-decision-whose-answer-adds-a-commit-to-a-pull.md, docs/items/PL-LNNL-no-check-reads-a-markdown-document-as.md, docs/items/PL-QFCR-arming-tooling-and-gate-write-this-repository-s.md, docs/items/PL-RLS3-record-the-2026-instruction-file-measurements.md, docs/items/PL-VF3C-port-the-2026-09-25-multi-session-stress.md
deferred-from: v0.6.0 - filed after the gate froze, and a docket defect in how the queue records state, which the layout milestone does not clear
added: 2026-10-11
payoff: an item stops reading blocked the moment nothing blocks it, so released work reaches bin/docket next in the pull request that released it instead of waiting for a grooming pass
verify: grep -q 'def test_a_blocked_item_whose_every_blocker_has_closed_is_an_error' subprojects/docket/tests/test_checks.py
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

**Decided 2026-10-11: (b)** (project owner, 2026-10-11, ratified, over a
fifth `unblocked` status and over keeping the advisory as it is): no new
status; `bin/docket check` refuses a `blocked` item whose every item blocker
has closed, and the pull request that closes a blocker moves what it released.

**Generator check.** Read against `PL-6T44`'s head (closed 2026-09-20, misread
"An item's current queue state"): this is the same fact from the writer's
side, and not recorded as a live head - see **History** above for the count.

**Done when.** `bin/docket check` reports an error, not an advisory, for an
item at `status: blocked` whose `blocked-by` names only items and every one of
them is `done` or `dropped`; the message says to move it to `ready` with its
`verify:` and `payoff:`, or to record what really holds it in `blocked-by` (an
item for the condition, per `PL-0H5D`). The existing promotion test becomes
`test_a_blocked_item_whose_every_blocker_has_closed_is_an_error`. Milestone
blockers keep their advisory. `bin/docket next`'s "Blocked on paper only" line
and the close-time print in `bin/docket set` say the closing pull request moves
them, since the check will now refuse it otherwise. Close-out step 1
(`.claude/skills/docket/modes/close-out.md`) drops "candidate list ... nothing
promotes them for you" framing only where it implies the item may be left, and
says a released item leaves `blocked` in the closing pull request. The five
items stale on 2026-10-11 - `PL-JHHC`, `PL-LNNL`, `PL-QFCR`, `PL-RLS3`,
`PL-VF3C` - leave `blocked` in the same pull request, each to `ready` with its
`verify:` and `payoff:` written for the end state, or to a real blocker, so
`main` never carries the error.
