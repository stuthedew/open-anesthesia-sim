---
id: PL-54V0
title: resumed_at refuses an unkeyframed instant with a reason resumed_at_halt disproves
status: untriaged
classes: safety, docs
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, tests/integration/test_controller.py
added: 2026-09-21
---

**Problem.** `SimulationController._resume_point_at` refuses a fork at an
instant the run holds no keyframe for, and the message gives the reason as
"opening there would restart from two propagations where the run took one and
would not reproduce it element-wise". Since `PL-B8MK`, `resumed_at_halt` forks
at exactly such an instant and *does* reproduce the parent element-wise, by
opening the definition at the keyframe at or before it. So the refusal's stated
reason names a construction the program no longer has to use.

**Why it matters.** The refusal itself is still right - a fork is taken where a
run stands, and `resumed_at` is the control-event door - but the reason is what
a reader learns the constraint from. An error message on a safety-critical path
that teaches a constraint the code beside it disproves is the presentation half
of the safety standard: the right refusal with the wrong explanation. It also
invites the wrong fix, since a reader who believes the stated reason will try to
record a keyframe at the fork, which is the route `PL-B8MK` measured and refused
because marking a run would change it.

**What the message should say instead** is why `resumed_at` is the wrong door
rather than why the arithmetic cannot be done: the run is not standing at that
instant, so there is no live state to seed a branch from and no step count to
continue, and a fork at a mark is reached through `resumed_at_halt`.

**Found by `PL-Z3W6`**, which asserted the arithmetic both ways in
`tests/reference/test_canonical_evaluation.py` and so had both routes in front
of it. Not fixed there: `src/anesthesia_sim/app/controller.py` is outside that
item's `touches`, and a changed error string wants the test that pins it changed
in the same commit, which is the close-out shape `PL-K4R5` describes.

**Where.** `src/anesthesia_sim/app/controller.py` (`_resume_point_at`), and
`tests/integration/test_controller.py`, which pins the current string.
