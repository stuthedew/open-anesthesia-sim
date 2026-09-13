---
id: PL-4ZK8
title: bin/docket concurrent offers a batch containing needs-decision and in-flight items, so a fan-out cannot hand it out as-is
priority: P2
effort: S
status: needs-decision
classes: defect
feature: parallel-sessions
touches: subprojects/docket
added: 2026-09-07
---

**Problem.** bin/docket concurrent offers a batch containing needs-decision and in-flight items, so a fan-out cannot hand it out as-is

**What was observed.** A bare `bin/docket concurrent` on 2026-09-07 returned
"A batch that can be worked at once (32 items, best-first)". Of those 32,
`PL-483K` was in flight (marked `[IN FLIGHT]` in the line, so that half is
visible) and at least seven were at `status: needs-decision` — `PL-DXQC`,
`PL-B32L`, `PL-WGXJ`, `PL-JW39`, `PL-KFWL`, `PL-KRS6`, `PL-H1JD` — with
nothing in the batch line saying so.

**Why it matters.** "Can be worked at once" is read as "can be started at
once", and a needs-decision item cannot be started: its next step is the
project owner's answer, which is the same wrong answer `PL-JW39` records
against `docket next`. The consequence lands hardest on the case the command
is best for — a session picking several items to hand to several sessions —
because there the wrong pick is not one session's detour but N of them, and
the batch is exactly what a fan-out would paste. Whether a batch should hide
such items or mark them is the decision: `[IN FLIGHT]` is already the marking
precedent, and hiding would make the count disagree with `docket list`.

**Found while** picking four gate entries to spin up as parallel sessions on
2026-09-07 — the batch could not be used as the answer, so the four were
chosen by reading the 95 open gate entries' front matter by hand.
**Done when.** `bin/docket concurrent`'s batch either excludes `needs-decision`
and in-flight items or marks each of them the way `[IN FLIGHT]` already marks
one; the choice is recorded in the command's own docstring with its reason; and
a test pins it. The decision has to respect both costs the brief names: hiding
them makes the batch count disagree with `bin/docket list`, and marking them
leaves a fan-out filtering the list it was handed. `PL-7B3G` is sequenced behind
this answer, because whether it still has two axes to build depends on which
way this goes.

**Decision needed.** Should `bin/docket concurrent`'s batch hide `needs-decision` and in-flight items, or mark them the way `[IN FLIGHT]` already marks one?
