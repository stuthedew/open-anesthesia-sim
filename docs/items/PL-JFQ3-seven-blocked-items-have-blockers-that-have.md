---
id: PL-JFQ3
title: Seven blocked items have blockers that have closed, and since PL-ZF2G promoting one is what returns an anticipated safety finding to the debt gate
status: untriaged
feature: debt-gate
added: 2026-09-16
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

