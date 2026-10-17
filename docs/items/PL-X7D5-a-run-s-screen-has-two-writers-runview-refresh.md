---
id: PL-X7D5
title: A run's screen has two writers - RunView.refresh from a drawn frame and RunView.present_halt from a hand-picked subset of controller state - and nothing owes a frame when the run changes outside present, so each widget missing from the subset, and each path that stops or changes a run without a frame, leaves the screen stating an old run: the cause of PL-1YDD, PL-DTJQ, PL-MMNX, PL-T995, PL-G3K7 and PL-0LG6 (found at the 2026-10-17 triage pass)
priority: P1
effort: L
status: needs-decision
classes: safety, refactor
feature: every-control-restates-the-halt
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/test_simulation_view.py
added: 2026-10-17
root-cause-of: PL-1YDD, PL-DTJQ, PL-MMNX, PL-T995, PL-G3K7, PL-0LG6, PL-85LJ
generator: live - four reviews of the run view in ten days (PL-V2HC's, PL-85LJ's, PL-Y2SL's, PL-VN6M's) each found a widget or stop path the halt list or a frame request missed, and each widget added later is another
misread: Which widgets state a run's current state, and that each is restated on every path that changes it
---

**Problem.** A run's screen has two writers - RunView.refresh from a drawn frame and RunView.present_halt from a hand-picked subset of controller state - and nothing owes a frame when the run changes outside present, so each widget missing from the subset, and each path that stops or changes a run without a frame, leaves the screen stating an old run: the cause of PL-1YDD, PL-DTJQ, PL-MMNX, PL-T995, PL-G3K7 and PL-0LG6 (found at the 2026-10-17 triage pass)

**The mechanism, read 2026-10-17.** `RunView.refresh` writes every widget a
run shows from a drawn frame and its snapshot. `RunView.present_halt`, the one
writer that runs when no frame can draw, writes a list chosen by hand: the
status word, the transport, the notice banner, and since `PL-85LJ` the four
setting controls. Nothing states which widgets say what the run currently is,
so each one left off that list stays on the last frame after a halt
(`PL-1YDD` the agent identity, `PL-DTJQ` the control-change panel, `PL-MMNX`
the fork panel, which `_halt_every_run` never reaches). And nothing makes a
frame owed when a run changes outside `SimulationView.present`, so a path that
stops or changes a run without asking for one leaves every widget behind
(`PL-T995` a run stopping itself in `RunView.step_tick`, `PL-0LG6`
`SimulationView.add_run`, and `PL-G3K7` the legend written ahead of a frame
that then fails). `PL-85LJ`, closed, was the first member: its fix added one
more entry to the hand-picked list, which is why the list kept producing.

**Not members.** `PL-08SS`, `PL-F2T2` and `PL-M3M2` share the feature but not
the fact: each is slot code that reads the snapshot, or lets a raise out,
outside the halt gate, which is where the halt is stated rather than which
widgets it restates.

**Why it matters.** `PL-T995` is reachable today: a learner's own bookmark
halt leaves the screen reading "Running" with Pause live and a clock one step
behind, which is the stale-state presentation failure `CLAUDE.md`'s
safety-critical standard names. The rest need a failing frame, but each review
of this view finds another widget the list missed, and every widget or stop
path added later is another place to miss, so fixing the members one at a time
pays the same review again.

**Decision needed.** What shape makes "every widget states the run as it is"
true by construction rather than by a list. **Recommended:** one record per
run of what its screen states that is not a compartment value (status,
transport, notice, agent identity, settings, control timeline, fork offer),
built from the controller without a snapshot, and written by both `refresh`
and `present_halt` through one method, so a widget is added to the record or
is not on screen; and every path that changes a run's state outside `present`
- a self-stop in `step_tick`, `add_run`, a request that changes the selection
- asks for a coalesced frame, so the record is restated on the next tick. The
alternative, keeping the two writers and a test that enumerates the widgets,
catches an omission only where the test's list is itself complete, which is
the list that has already failed. The choice is internal structure and is the
design round's to take; it reaches every member's code, so the round puts the
size and the risk of breaking the run view to the owner before building.

**Done when.** The decided shape is built; each open member closes under it
with the regression test its brief names; and a test drives a halt, a
self-stop and a failed frame through the app's real timers and reads every
widget the record carries against the controller.

**Generator check.** A generator: one fact - which widgets state a run's
current state, and that each is restated on every path that changes it -
misread by six open items and one closed, with no head's `misread:` stating it
(`bin/docket generators --misread`, 2026-10-17). Live, because four reviews in
ten days (`PL-V2HC`'s, `PL-85LJ`'s, `PL-Y2SL`'s and `PL-VN6M`'s) each handed
it new members.

**Design round requested 2026-10-17** (project owner, in the triage session):
claim this item, read its members' briefs (`PL-1YDD`, `PL-DTJQ`, `PL-MMNX`,
`PL-T995`, `PL-G3K7`, `PL-0LG6`), run the round from the marked
recommendation, and put the refactor's size and risk to the owner before
building anything. Not started: the session that was asked reset for length
first.
