---
id: PL-7TBQ
title: SimulationController.has_recorded_run reads elapsed_s > 0.0, so it is True the instant a branch is made and before the learner has touched it
priority: P2
effort: S
status: done
classes: defect, ux
feature: scenario-branching
milestone: v0.5.15
touches: src/anesthesia_sim/app/controller.py, tests/integration/test_controller.py, tests/unit/test_dashboard_frame.py
added: 2026-09-14
closed: 2026-09-27
pr: 1187
verify: grep -q 'def test_a_fresh_branch_holds_nothing_to_destroy' tests/integration/test_controller.py && uv run pytest tests/integration/test_controller.py
---

**Problem.** SimulationController.has_recorded_run reads elapsed_s > 0.0, so it is True the instant a branch is made and before the learner has touched it

**Measured 2026-09-14** while working `PL-ZMRT` (one simulated-time frame), by
an adversarial pass over the fork paths.

`SimulationSnapshot.has_recorded_run` is `self.elapsed_s > 0.0 or
bool(self.control_timeline)`, under a docstring saying it is "false for a run
that has been built and not yet touched, which is the state both a fresh
session and `reset()` leave". On a branch both halves of that are false: a
branch forked at 30.0 s reports `has_recorded_run` `True` with
`len(control_timeline) == 0`, and advanced 5 s and then `reset()` it still
reports `True`. The clock is the case's, so a branch's `elapsed_s` opens at the
fork and the `> 0.0` test can never say "untouched" for one.

**Its single reader is the destructive-act confirmation.**
`app/simulation_view.py` gates `_start_new_case` against `_confirm_new_case` on
this property, so a branch with nothing to lose gets the confirmation that
warns about losing something - which is the precise failure the docstring says
the property exists to prevent ("a confirmation that fires in both cases states
something untrue in the second").

**Bounded today, and not by this property.** `set_agent` refuses on a branch
outright, so the learner meets a false confirmation followed by a refusal
rather than a discarded case. That makes it wrong rather than dangerous.

**It predates `PL-ZMRT`.** `PL-J2TD` made a branch's clock the case's, which is
correct and is not what should change. The fix is in the property: "untouched"
is a statement about what the learner has done to *this* run, so it wants the
run's own opening rather than zero - `elapsed_s > opened_at_s`, or the
controller answering it directly - not a relaxation of the clock.

**Verified 2026-09-14.** `app/controller.py:478-484`. `has_recorded_run` is
documented as "Whether this run holds anything that starting over would
destroy" - "false for a run that has been built and not yet touched" - and a
branch is built already standing at the fork instant, so its elapsed time is
greater than zero before the learner has done anything to it.

**Why it matters.** `:737-738` says `SimulationSnapshot.has_recorded_run` "is
what tells it whether this call would cost anything", so the flag gates a
destructive-action confirmation. On a branch it is True immediately, which means
the learner is warned about losing work they have not done - and a confirmation
that fires when there is nothing to lose is the one that gets clicked through,
so it costs the warning its meaning on the runs where there *is* something to
lose. `.claude/rules/expert-review.md` asks for interfaces that prevent errors;
a warning trained to be dismissed is the opposite.

**Done when.** `has_recorded_run` is false for a branch that has been forked and
not yet touched, and true once it has advanced past its own opening or recorded
a setting change of its own - measured against the branch's opening instant
rather than against zero. `tests/integration/` covers a fresh branch.

**Closed 2026-09-27.** Re-confirmed against `4dd559fe` before the fix. A branch
forked at 60.0 s read `has_recorded_run` `True` with an empty timeline, and it
still read `True` after 5 s of advance and a `reset()`. `SimulationSnapshot` now
carries `began_at_s`, which is the value `SimulationController.began_at_s`
gives, and the property counts elapsed time from there rather than from zero.
Five tests in `tests/integration/test_controller.py` pin the behaviour. The
fresh-branch, bookmark-branch and reset cases fail against the old comparison.

Since filing, the consequence has narrowed. `PL-QRD1` replaced a branch's agent
selector with the agent chip, so the false confirmation described above cannot
be reached from the dashboard today. The property was still wrong against its
own docstring, and the fix is for whichever reader asks it about a branch
next.
