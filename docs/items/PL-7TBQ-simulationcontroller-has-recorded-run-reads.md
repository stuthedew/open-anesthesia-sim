---
id: PL-7TBQ
title: SimulationController.has_recorded_run reads elapsed_s > 0.0, so it is True the instant a branch is made and before the learner has touched it
status: untriaged
added: 2026-09-14
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
