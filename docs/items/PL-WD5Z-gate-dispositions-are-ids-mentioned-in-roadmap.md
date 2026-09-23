---
id: PL-WD5Z
title: Gate dispositions are ids mentioned in ROADMAP.md prose rather than a field on the item, a second store of queue state that four items filed 2026-09-22 and 09-23 each disagree with (PL-58JD, PL-59QW, PL-FD5Q, PL-VFJ3), after three heads each fixed a reader of it
priority: P2
effort: L
status: needs-decision
classes: refactor, infra
feature: gate-disposition-store
touches: ROADMAP.md, subprojects/docket/src/docket/roadmap.py, tools/doc_check.py, .claude/skills/docket/modes/triage.md, docs/items
added: 2026-09-23
root-cause-of: PL-58JD, PL-59QW, PL-FD5Q, PL-VFJ3
generator: live - every debt capture made while a gate is frozen owes a new prose entry in ROADMAP.md, so each capture adds text that can narrate stale status, be mis-parsed or be forgotten; four members arrived 2026-09-22 and 09-23, three within a day of PL-J6HP's spent verdict on a reader of the same record
---

**Problem.** A debt item's gate disposition (declined to a later gate,
deferred, or cleared by the milestone itself) is recorded as the item's id
appearing in a `ROADMAP.md` subsection, inside sentences written for a human
reader. The item file does not carry it. So the disposition is queue state
held in a second store beside the items, and each way the two stores can
disagree has become an item of its own:

- **A second place to write**, which the triage mode never mentions: `#953`
  followed the mode, went red in `checks` on eleven debt captures with no
  v0.6.0 entry, and its fix commit then marked the items it led with as in
  flight (`PL-VFJ3`).
- **Status narrated in prose that nothing re-reads** when the item moves:
  `PL-YZJD`'s deferral entry still read "At `needs-decision`" with the item
  `done`, found by comparing all 27 deferral entries by hand (`PL-59QW`).
- **Parsed back out by a regex over whole subsections**, so a sentence saying
  an item was *absent* disposed of it (`PL-58JD`). That is the `_declined_ids`
  shape `PL-H6VQ` measured in `tools/doc_check.py` on 2026-09-20, now in
  `docket.roadmap`, where `PL-J6HP` gathered the gate readers.
- **A question answered from the wrong section**: `bin/docket wave` counts
  five of v0.6.0's own Required-scope items as outside work the gate waits on
  (`PL-FD5Q`).

**Generator check.** One mechanism shared by four open items that no head
names. Three closed heads worked on readers of this same record: `PL-HWW1`
(Required scope, 2026-09-19), `PL-2T03` (the release train, 2026-09-19) and
`PL-J6HP` (gate facts parsed once in `docket.roadmap`, closed 2026-09-23 as
`spent`). Each fixed how the prose is read, and none changed the fact that it
is prose. `PL-FD5Q`, `PL-58JD` and `PL-59QW` all landed within a day of
`PL-J6HP`'s `spent` verdict. Sharing a file is not sharing a mechanism, so the
claim is narrower than "`ROADMAP.md`". It is that a disposition is an id
*mentioned* in prose rather than a field on the item it disposes of.

**Why it matters.** It is `live` because every debt capture made while a gate
is frozen owes a new entry (`PL-VFJ3`), and this item's own capture owed one.
So the mechanism's inflow tracks capture volume, which is the busiest flow the
workflow lane has. It is also a dead end already refused under another name. A
disposition list in a shared document is "one shared queue document", which
this project rejected because "it serializes every writer, which is the
property one-file-per-item exists to buy" (`subprojects/docket/src/docket/model.py`).
A branch that captures debt during a freeze and a branch that triages it both
have to write the same subsection.

**Decision needed.** Where a gate disposition lives. There are three routes:

1. **On the item.** A front-matter field carries the disposition and its
   reason, and `docket set` writes it. `ROADMAP.md`'s Declined subsections are
   then rendered from the field or reduced to a pointer. `docket check` can
   require the field of a debt capture made during a freeze, which retires
   `PL-VFJ3`'s instruction instead of adding one, and there is nothing left to
   narrate (`PL-59QW`) or mis-parse (`PL-58JD`). Cost: every existing entry
   has to be migrated (`PL-H6VQ` counted 97 prose-only dispositions on
   2026-09-20), the gate section of `ROADMAP.md` changes shape, and the new
   field is admitted under the `PL-6Q9L` pause only because it fixes a live
   generator.
2. **Structured lines in `ROADMAP.md`.** Each entry gets its own line and the
   disposition is the id that leads it, with prose after the id and no
   narrated status. This keeps the gate readable in the document the owner
   reads, and it fixes the parse (`PL-58JD`). It leaves the second place to
   write (`PL-VFJ3`) and the narration (`PL-59QW`) to checks, which is the
   pattern the three heads above already followed.
3. **Keep the representation and fix the four instances.** This is the
   cheapest route today. On the evidence of three heads, the expected outcome
   is more members.

**Recommended: route 1.** It is the only route that removes the second store
rather than guarding it, and it is the answer the project already gave for
every other kind of queue state. Route 2 is the fallback if the gate should
stay readable in `ROADMAP.md` itself. It costs a second store held together by
checks, which is where the current members came from.

**Done when.** The owner has chosen a route, and the choice is recorded here
with its kind (ratified or specified). Under route 1 or 2, the four members
close through the change, and a debt capture made during a frozen gate cannot
land without a disposition, enforced by a check rather than by instruction.
Under route 3, the four close as instances, and this verdict is re-read at the
next member.
