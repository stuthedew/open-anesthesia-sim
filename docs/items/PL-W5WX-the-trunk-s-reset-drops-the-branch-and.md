---
id: PL-W5WX
title: The trunk's Reset drops the branch and everything it simulated with no statement and no confirmation, and docs/MODEL.md does not say whether the exemption it grants Reset reaches a run the learner did not aim at
status: untriaged
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

**So the question is which way it resolves, and it is the project owner's.**
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
