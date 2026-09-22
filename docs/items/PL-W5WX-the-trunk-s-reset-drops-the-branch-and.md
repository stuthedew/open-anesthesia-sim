---
id: PL-W5WX
title: The trunk's Reset drops the branch and everything it simulated with no statement and no confirmation, and docs/MODEL.md does not say whether the exemption it grants Reset reaches a run the learner did not aim at
priority: P2
effort: S
status: needs-decision
classes: ux, docs
feature: reset-aftermath
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/run_view.py, docs/MODEL.md, tests/integration/test_simulation_view.py
added: 2026-09-22
---

**Problem.** The trunk's Reset drops the branch and everything it simulated with no statement and no confirmation, and docs/MODEL.md does not say whether the exemption it grants Reset reaches a run the learner did not aim at

**Found 2026-09-22** while working `PL-WG73` (the comparison lock naming a
control that does not exist), which is the item that put the sentence "Run 1's
Reset ends it and starts the case over" on screen. That caption is now the only
place a learner is told, and it is shown only while the branch control is
locked - so a learner who never opens the branch panel presses the trunk's
Reset with nothing said at all.

**Why it matters.** `docs/MODEL.md` § "Agent-change behavior" states it as a
requirement on the interface rather than on the controller: "the interface must
not discard a run holding anything - any elapsed simulated time, or any
recorded control change - without first stating that it will be discarded and
obtaining the user's confirmation", because "nothing in this application
persists them, and there is no undo". `format_case_discard_warning` and the
new-case dialog are that requirement discharged for the paths it was written
about.

The same section ends by exempting Reset - "Reset is therefore also the way to
make a change of agent free" - and that exemption is sound for what it was
written under: pressing Reset *is* the learner asking for that run to be
discarded. What it was not written under is branching. `RunView._handle_reset`
calls `controller.reset()` and emits `case_restarted` with no confirmation
anywhere on the path, and `SimulationView._handle_case_restarted` then drops
every branch: one press on Run 1 destroys Run 2's elapsed time and recorded
control changes, which the learner did not ask for and cannot recover.

**Decision needed: which way it resolves, and it is the project owner's.**
Either the interface states and confirms before a Reset takes a *second* run
with it - the existing discard-warning path is the precedent and the wording
already exists - or `docs/MODEL.md` says why the exemption reaches a run the
learner did not aim at. Leaving the specification silent is the one outcome
that should not stand, because the requirement above is written generally
enough to read as covering this and the code does not.

**Verified 2026-09-22** against `src/anesthesia_sim/app/run_view.py`
`_handle_reset`, `src/anesthesia_sim/app/simulation_view.py`
`_handle_case_restarted`, and `docs/MODEL.md` § "Agent-change behavior";
`tests/integration/test_simulation_view.py::test_resetting_the_trunk_ends_the_comparison`
is the test that records the behavior as intended.

**Not classed `safety`.** Nothing here displays a wrong or misattributed
clinical value; what is lost is simulated work. It is the same human-factors
band as `PL-WG73`.

**Recommendation** (session, 2026-09-22): confirm, and say so in
`docs/MODEL.md`. The exemption's own reasoning is what decides it - "pressing
Reset *is* the learner asking for that run to be discarded" is true of the run
the button sits on and false of every other run on screen, so the exemption
stops where the press stops. The existing `format_case_discard_warning` path
already states what is lost in the terms the display uses for it, which is the
second bullet of the requirement, and a branch has exactly the two quantities
that bullet is about: elapsed simulated time and recorded control changes. The
cheaper half is the specification either way - one sentence in § "Agent-change
behavior" saying whether the exemption is the *button's run* or *any run the
press takes with it* - and it is worth writing even if the confirmation is
declined, because the silence is what let this ship.

The cost of confirming is a dialog on a gesture learners make often. That is
answered by the same exemption the section already grants: a run holding
nothing is exempt, so the trunk's Reset would confirm only when a branch is
drawn *and* that branch holds something - which is precisely the case where
something is lost, and is never the ordinary start-over.

**Done when.** The project owner has chosen, and `docs/MODEL.md` § "Agent-change
behavior" says whether Reset's exemption reaches a run the press was not on. If
the answer is to confirm, the trunk's Reset states and confirms before it takes
a branch holding elapsed time or recorded control changes, and a test in
`tests/integration/test_simulation_view.py` holds it.

**Premise re-read 2026-09-22 (`PL-14QR`, triage).** `RunView._handle_reset` still goes straight
from `self.controller.reset()` to `self.case_restarted.emit()`, with nothing
between them.
