---
id: PL-T2Q2
title: With every frame failing on a paused trunk, the keyframe selector's Branch button stays live and opens a branch, because fork_at accepts a failed trunk's keyframe, and the next failing frame then halts the new run (found triaging PL-MMNX, 2026-10-17)
priority: P2
effort: M
status: ready
classes: ux, defect
feature: every-control-restates-the-halt
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-17
payoff: a halted trunk offers a branch only where one can open and be drawn, so no Branch control can only fail
verify: grep -q "def test_a_trunk_halted_by_a_failing_frame_offers_no_branch" tests/integration/test_simulation_view.py && grep -q "def test_a_trunk_failed_on_its_own_step_keeps_its_earlier_keyframes_branchable" tests/integration/test_simulation_view.py
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

**Re-checked 2026-10-18 at `21174fd3`: the defect still holds.**
`_restate_fork_panel` calls `_refresh_fork_panel`, which offers
`BranchedCase.fork_points_s`. That list is the trunk's keyframes, and nothing
filters it on a failed trunk. Only `here_fork_point` goes to None. So after
`_halt_every_run` the keyframe selector's Branch button is still offered, and
`fork_at` still opens the branch. This was read from the code, not run.

**Decided 2026-10-18 in the product decision batch's design round: the
recommendation above, taken as an obvious call rather than put to the project
owner.** A trunk halted by the shared render path (`_halt_every_run`) offers no
branch at all: no keyframe, no mark and no "Branch here". A branch opened
there is drawn by the same failing frame and halts at once, so the control
can only fail, and `.claude/rules/expert-review.md` prefers an interface that
prevents an error to one that reports it. A trunk that failed on its own step
keeps the keyframes it recorded before the failure. Those are canonical
states, and "go back and try something else" is what a branch is for.
Keeping that is today's behaviour, and no defect argues against it. The
alternative, offering no branch on any failed trunk, was refused because it
removes that teaching use and fixes nothing that the render-path rule leaves
broken. The build decides how the case learns the halt's cause. The rule it
must hold is the one above.

**Done when** (decided form). A test halts a paused trunk on a failing frame
and asserts that the keyframe selector, the mark selector and "Branch here"
offer nothing. A second test fails a trunk on its own step and asserts that
its earlier keyframes are still offered and that a branch opens at one.
