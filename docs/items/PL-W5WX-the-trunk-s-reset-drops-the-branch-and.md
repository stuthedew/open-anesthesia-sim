---
id: PL-W5WX
title: The trunk's Reset drops the branch and everything it simulated with no statement and no confirmation, and docs/MODEL.md does not say whether the exemption it grants Reset reaches a run the learner did not aim at
priority: P2
effort: S
status: done
classes: ux, docs
feature: reset-aftermath
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/formatting.py, docs/MODEL.md, docs/ARCHITECTURE.md, tests/integration/test_simulation_view.py, tests/unit/test_dashboard_frame.py, tests/unit/test_formatting.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-14QR's 2026-09-22 triage pass
added: 2026-09-22
closed: 2026-10-18
pr: 1578
payoff: a Reset never throws away a branch's simulated work without first saying so and asking
verify: grep -q "def test_resetting_the_trunk_asks_before_dropping_a_branch_that_holds_work" tests/integration/test_simulation_view.py
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

**Premise re-read 2026-10-18 at `21174fd3`, in the product decision batch's
design round.** `RunView._handle_reset` still goes from
`self.controller.reset()` to `self.case_restarted.emit()` with no question
asked. `SimulationView._handle_case_restarted` still rebuilds the case on the
trunk and removes every branch it drew. `docs/MODEL.md` § "Agent-change
behavior" still states the discard requirement and still ends with Reset's
exemption, with no word on a run the press was not on. The question and the
recommendation above stand unchanged and are put to the project owner,
because the answer decides whether a learner meets a dialog on a common
gesture.

**Answered 2026-10-18: confirm** (project owner, 2026-10-18, ratified,
over no dialog with `docs/MODEL.md` saying the exemption covers every run the
press takes with it). Stuart tapped "Confirm first" on the product decision
batch's card at 03:59Z. The build does three things. The trunk's Reset states
what each branch it would drop holds and asks before dropping it, reusing
`format_case_discard_warning`'s wording. It asks only when a branch is drawn
and holds elapsed simulated time or a recorded control change, so an ordinary
start-over sees no dialog. Declining leaves every run as it was. And
`docs/MODEL.md` § "Agent-change behavior" says that Reset's exemption covers
the run the button is on and no other run.

**Done when** (decided form). The trunk's Reset confirms before it drops a
branch holding elapsed time or recorded control changes, and does not ask when
no branch holds anything. A test in `tests/integration/test_simulation_view.py`
holds both cases and the decline. `docs/MODEL.md` § "Agent-change behavior"
states that the exemption stops at the button's own run.

**Built 2026-10-18 under "confirm".** `RunView.ask_before_reset` lets the
dashboard give the trunk's view a question to ask before its Reset.
`SimulationView._trunk_reset_question` returns one only where a drawn branch
holds work, by `has_recorded_run`, through `dashboard_frame.branch_at_stake`. A
branch whose snapshot refuses a value is asked about too, since what it holds
cannot be read. The question is `dashboard_frame.trunk_reset_question`, shown
in the existing `NewCaseDialog`. Its warning is
`formatting.format_branch_discard_warning`, which shares its wording with
`format_case_discard_warning` and states the branch's fork and the instant it
has run to, as the case clock shows them. Keeping the branch is the default
button, and declining leaves every run as it was. `docs/MODEL.md` §
"Agent-change behavior" now says that Reset's exemption covers the run whose
button was pressed and no other run. `docs/ARCHITECTURE.md` names the hook.

The integration tests are
`test_resetting_the_trunk_asks_before_dropping_a_branch_that_holds_work` (for
elapsed time and for a control change),
`test_declining_the_trunks_reset_leaves_every_run_as_it_was` and
`test_confirming_the_trunks_reset_starts_the_case_over_without_the_branch`.
`test_resetting_the_trunk_ends_the_comparison` now also asserts that a branch
holding nothing asks nothing. Against the code before the fix, each new
integration test fails with `AttributeError: 'RunView' object has no attribute
'_reset_dialog'`. A variant that needs no new interface, `len(view.runs) == 2`
after the press, fails there because the old Reset dropped the branch at once
(inferred from `test_resetting_the_trunk_ends_the_comparison`, which asserted
that behavior). Unit tests in `tests/unit/test_dashboard_frame.py` and
`tests/unit/test_formatting.py` pin every line of the question as literals.
