---
id: PL-T2Q2
title: With every frame failing on a paused trunk, the keyframe selector's Branch button stays live and opens a branch, because fork_at accepts a failed trunk's keyframe, and the next failing frame then halts the new run (found triaging PL-MMNX, 2026-10-17)
priority: P2
effort: M
status: needs-decision
classes: ux, defect
feature: every-control-restates-the-halt
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-17
---

**Problem.** With every frame failing on a paused trunk, the keyframe selector's Branch button stays live and opens a branch, because fork_at accepts a failed trunk's keyframe, and the next failing frame then halts the new run (found triaging PL-MMNX, 2026-10-17)

**Checked 2026-10-17.** This item was filed at 00:06 CDT, before `PL-MMNX`
closed at 10:39 CDT. `PL-MMNX`'s `_restate_fork_panel` restates both branch
controls on a halt, so the button may no longer stay live; that half needs
re-checking before work starts. The code half still holds:
`BranchedCase.fork_at` calls `SimulationController.resumed_at`, whose refusals
are a branch of a branch, a bad instant and a mismatched rebuild. Only
`resumed_here` refuses a failed run.

**Why it matters.** A learner who presses Branch on a failed trunk gets a new
run that halts at the next frame. The dashboard offers an action that cannot
succeed, beside controls that say the run has failed.

**Decision needed.** Should a trunk that has failed still offer its earlier
keyframes for a branch? A keyframe before the failure is a correct state, and
"go back and try something else" is what a branch is for. But when the failure
is a frame failure, the new branch is drawn by the same failing frame.

**Recommended.** Keep keyframes before a run failure branchable, since that is
the teaching use. When the halt is a frame failure, offer no branch, as
`_restate_fork_panel`'s fallback already does. This is a learner-visible
behaviour, so it is put to the owner.

**Done when.** The decided rule is pinned by a test that halts a trunk on a
failing frame and asserts what the keyframe selector offers.
