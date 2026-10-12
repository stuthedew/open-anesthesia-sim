---
id: PL-Y2SL
title: A learner who pauses the trunk can branch there only if it stopped on a mark or a setting changed at that instant, where the owner wants the paused point to be the default place to branch, with marks and setting changes still offered
priority: P2
effort: M
status: done
classes: feature
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/core/run_definition.py, docs/ARCHITECTURE.md, docs/MODEL.md, tests/integration/test_controller.py, tests/integration/test_simulation_view.py, tests/unit/test_dashboard_frame.py, tests/unit/test_chart_frame.py, docs/items/PL-0LG6-simulationview-add-run-leaves-no-frame-owed-so.md, docs/items/PL-08SS-simulationview-handle-fork-and-handle-halt-fork.md
added: 2026-10-12
closed: 2026-10-12
pr: 1453
payoff: a learner who pauses to think can try something else from that instant in one press, without marking it first
verify: grep -q 'def test_a_paused_trunk_branches_where_it_stands' tests/integration/test_controller.py
---

**Problem.** A learner who pauses the trunk can branch there only if it stopped on a mark or a setting changed at that instant, where the owner wants the paused point to be the default place to branch, with marks and setting changes still offered

**Asked for by the project owner, 2026-10-12**, replying to `#1451`: "Allow
branch from current paused point. Make default behavior. Can also branch from
bookmark, or change. But if I pause I should be able to branch from there too".

**Why it matters.** Pausing is how a learner stops to think, and the paused
instant is the decision point they are looking at. Today it is not on offer at
all unless a mark or a setting change sits on it, so trying an alternative from
there takes two detours - mark the instant, then find the mark in the selector.

**What exists.** Three doors: `resumed_at` (a keyframe - induction or a setting
change), `resumed_at_halt` (the crossing the run is standing on) and
`resumed_at_mark` (a time bookmark the run has passed, `PL-W4XQ`). A plain pause
at any other instant offers nothing, so a learner who pauses to think and wants
to try something else from there has to mark the instant first and then pick
the mark from the selector.

**The model needs no new construction.** The clock always stands on a whole
number of steps, and the bookmark fork's construction - the state from
`RunDefinition.state_at`, the branch's definition opened at the keyframe at or
before the fork - reproduces the trunk exactly at any reached step instant
(`docs/MODEL.md` § "What this requires of a branch"). So a fourth door,
`SimulationController.resumed_here()` kept by `BranchedCase.fork_here()`, forks
where the trunk stands, with the crossing reconstructed for the step ending
there as `_resume_point_at_mark` already does. The same door covers a halt, and
reconstructing the crossing there instead of reading the halt's record would
also close `PL-2N43`.

**Recommended: a "Branch here" button shown whenever the trunk is paused,
replacing the halt-only button, with the selector kept for marks and setting
changes.** The paused point is the default act because it is the one control
labelled with the instant the learner is looking at; the selector stays the way
to go anywhere else. A button rather than a selector entry selected by default,
because the paused point ends at the next step, which is the lifetime `PL-TYWQ`
gave a control of its own (project owner, 2026-09-21, ratified, over one list
that grows a row while the run is halted): a row that appears on pause and
leaves on resume changes the selector under a reader who looked away, and a
default selection that jumps to it moves a choice the reader made. Labelled
"Branch here: 1h23m" on a plain pause and keeping "..., stopped on your mark" on
a halt; not offered while the run is going, on a failed run, or on a trunk with
nothing recorded yet, where the selector's induction entry already covers it.

**Answered 2026-10-12**: the button, as recommended above (project owner,
2026-10-12, ratified, over a "here" row at the top of the selector, selected by
default).

**Build plan, written before the session reset that followed the answer.**
What reading the code settled, so the build does not derive it again:

- **One door for where the trunk stands: `resumed_here()`, kept by
  `BranchedCase.fork_here()`, replaces `resumed_at_halt()` and
  `fork_at_halt()` rather than joining them**, so the paragraph above calling
  it a fourth door is amended: three doors remain - `resumed_at` (a keyframe),
  `resumed_at_mark` (a passed time mark) and `resumed_here` (where the paused
  trunk stands, a halt included). The halt door has no caller once its button
  goes, and keeping it would keep `PL-2N43`'s defect alive in a second door to
  the same instant; `PL-2N43` rides as a rider and closes with this.
- **The fork** is `self._state.elapsed_s`, which is `_instant_after` of
  `self._state.step_count` bit for bit; the state is `RunDefinition.state_at`
  there and the stretch `segment_at(fork_s)`. The crossing is reconstructed for
  the step ending there by a helper extracted from `_resume_point_at_mark`
  (none at step 0), so both doors read one rule.
- **It refuses** a branch (every door's reason), a running run (where it
  stands moves with each step, so the instant a label showed need not be the
  fork), a failed run (`RunStatus.failure_reason`: a failure must not be
  presented as a pause) and the run's opening (amended below). **Not the
  supported run length**: a branch at a halt
  on the limit is tested behaviour
  (`test_a_branch_forked_at_a_halt_on_the_supported_run_length_reads_as_stopped_there`).
- **One predicate**: a `here_fork_point` property, `HereForkPoint(fork_s,
  stopped_on_mark)` or None, answered from the same private check the door
  raises from, so the offer and the door cannot disagree;
  `BranchedCase.here_fork_point` reads the trunk's.
- **`fork_offer` takes `here: HereForkPoint | None` in place of `halt`**, and
  `ForkOffer.halt_offered`/`halt_label` become `here_offered`/`here_label`.
  Not offered while comparing; labelled `HERE_FORK_LABEL_TEMPLATE`, "Branch
  here: {instant}", on a plain pause and the ratified
  `HALT_FORK_LABEL_TEMPLATE` when `stopped_on_mark`.
- **Amended in the build: the run's opening is refused by the model, not
  hidden by the frame.** This plan had `fork_offer` hide the button at instant
  0. That would leave the door wider than its offer there, which is the
  disagreement the one predicate exists to rule out, so `_refusal_here`
  refuses a run at step 0 as well - nothing is recorded there, and
  `resumed_at` already opens a branch at the opening - and `fork_offer` has no
  rule about instants of its own.
- **`ForkPanel.halt_button` becomes `here_button`**, and
  `SimulationView._handle_halt_fork` becomes `_handle_here_fork`, through
  `fork_here`.
- **Tests**: about 42 references to the halt door in
  `tests/integration/test_controller.py`, 22 in
  `tests/integration/test_simulation_view.py`, 15 in
  `tests/unit/test_dashboard_frame.py` and 1 in `tests/unit/test_chart_frame.py`.
  Two change meaning rather than name:
  `test_a_run_not_standing_on_a_bookmark_has_no_instant_to_fork_at` becomes the
  positive case, `test_a_paused_trunk_branches_where_it_stands` (this item's
  `verify:`), and `test_resuming_past_a_bookmark_withdraws_the_fork_it_offered`
  becomes the running refusal.
- **Docs**: `docs/ARCHITECTURE.md`'s list of doors, § "Where a branch may be
  taken" and the learner-control bullets; the `resumed_at_halt()` mention in
  `docs/MODEL.md` § "What this requires of a branch"; a docstring mention in
  `src/anesthesia_sim/core/run_definition.py`. `ROADMAP.md`'s mentions are
  v0.5.0's record and stay.
- **Reversed in the build, on the adversarial review's evidence: the
  supported run length is refused too.** The bullet above kept it because a
  branch at a halt on the limit is tested behaviour. But the button is offered
  at every stop, so every run reaching 24 h offered "Branch here: 24h", and
  the branch it took could never step, its own Reset returned it to 24 h, and
  the comparison lock then left only the trunk's Reset, which discards the
  case (reproduced 2026-10-12). A run at the limit is stopped rather than
  paused, by `RunStatus.supported_limit_reason`'s own words, so refusing it
  is the request read as written. The tested behaviour survives through the
  doors that still fork there: the two limit tests now fork through
  `resumed_at_mark`.
- **Decided in the build, on the same review: the selector's button reads
  "Branch".** It was "Branch here" (`TAKE_FORK_LABEL`), directly above "Branch
  here: 1h23m" in the same style, and a press of the wrong one - reproduced:
  paused at 2 min, the top button branched at 0 s - locks the panel until the
  trunk's Reset discards the case. "From [0s] [Branch]" names its instant in
  the selector beside it, and "here" is left to the paused point. One clearly
  better option rather than a close call, so taken and reported rather than
  asked; a one-line revert if the owner prefers other words.

**Done when.** Paused anywhere with something recorded, a learner sees "Branch
here: 1h23m" at the paused instant, and pressing it branches there reproducing
the trunk element-wise; on a halt it keeps the ratified "..., stopped on your
mark" wording; marks and setting changes stay offered in the selector beside
it; and `docs/ARCHITECTURE.md` describes the door and the control.
