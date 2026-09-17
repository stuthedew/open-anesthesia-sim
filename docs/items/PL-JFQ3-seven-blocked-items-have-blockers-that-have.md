---
id: PL-JFQ3
title: Seven blocked items have blockers that have closed, and since PL-ZF2G promoting one is what returns an anticipated safety finding to the debt gate
priority: P2
effort: M
status: ready
classes: planning, docs
feature: debt-gate
touches: docs/items
added: 2026-09-16
not-delegable: the deliverable is a per-item judgment recorded in seven item files - whether each was blocked on something nobody wrote into `blocked-by` - and no command can tell a promotion that was reasoned from one that was typed
---

**Problem.** Seven blocked items have blockers that have closed, and since PL-ZF2G promoting one is what returns an anticipated safety finding to the debt gate

**What was found.** `bin/docket check` reports seven items as "every blocker has
closed; it is ready to promote" - `PL-5NR5`, `PL-LPLD`, `PL-MBP6`, `PL-QR6Q`,
`PL-QRD1`, `PL-W7H9` and `PL-Z3V5`, measured 2026-09-16. The advisory is not new
and nothing about it is broken; what is new is that one of them now has a
consequence beyond its own band.

**Why `PL-ZF2G` changes the weight of it.** `check_gate_reentries` now exempts
an item from the `safety`/`science` gate advisory only where `anticipated` and
`status: blocked` hold together, so the promotion is the event that returns such
a finding to the gate. `PL-W7H9` (`docs, safety, anticipated`) is blocked on
`PL-8PSW`, which is `done`. Promoting it is therefore not only tidying a status:
it is the step that lets the gate see a `safety` finding whose hazard may now be
live, which is the whole mechanism `PL-ZF2G` was filed to install.

**What this is not.** Not a defect in the advisory, which fires correctly and
names exactly the right items, and not a proposal to make `status` follow its
blockers automatically - `PL-ZF2G` considered resolving blockers inside
`check_gate_reentries` and refused it, because it would put a second copy of
`checks.py`'s resolution logic in the tool that reads the store rather than
reasons about it. This is the grooming pass that mechanism assumes somebody
runs.

**The judgment each one needs.** Promotion is not automatic even where the
blockers have closed: an item may have been blocked on a second thing nobody
wrote into `blocked-by`, and for `PL-W7H9` specifically the question is whether
`PL-8PSW` closing actually made its hazard live or merely removed one
prerequisite. Read each item before changing its status; the advisory says the
edge is clear, not that the work is startable.

**Found 2026-09-16** while implementing `PL-ZF2G`.

**Where.** `docs/items/`, the seven items named above.

**Why it matters.** `bin/docket next` reads `status`, so a blocked item whose
blockers have all closed is startable work that nobody is ever offered. Seven of
them is a second queue behind the queue. One carries more than that: `PL-W7H9`
is `docs, safety, anticipated`, blocked on `PL-8PSW`, which is `done` - and since
`PL-ZF2G` the promotion is the *event* that returns an anticipated safety finding
to the debt gate. So the grooming pass nobody runs is what holds a safety finding
outside the gate built to catch it, which is the mechanism working exactly as
designed and reaching nobody.

**Done when** each of the seven - `PL-5NR5`, `PL-LPLD`, `PL-MBP6`, `PL-QR6Q`,
`PL-QRD1`, `PL-W7H9`, `PL-Z3V5` - has been read and either promoted out of
`blocked`, or left blocked with the real blocker written into `blocked-by`; and
`PL-W7H9` records whether `PL-8PSW` closing made its hazard live or merely
removed one prerequisite. Read each item before changing its status: the advisory
says the edge is clear, not that the work is startable.
