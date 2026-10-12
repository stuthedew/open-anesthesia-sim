---
id: PL-Y2SL
title: A learner who pauses the trunk can branch there only if it stopped on a mark or a setting changed at that instant, where the owner wants the paused point to be the default place to branch, with marks and setting changes still offered
status: untriaged
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/simulation_view.py, docs/ARCHITECTURE.md, tests/integration/test_controller.py, tests/integration/test_simulation_view.py, tests/unit/test_dashboard_frame.py
added: 2026-10-12
---

**Problem.** A learner who pauses the trunk can branch there only if it stopped on a mark or a setting changed at that instant, where the owner wants the paused point to be the default place to branch, with marks and setting changes still offered

**Asked for by the project owner, 2026-10-12**, replying to `#1451`: "Allow
branch from current paused point. Make default behavior. Can also branch from
bookmark, or change. But if I pause I should be able to branch from there too".

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

**Done when.** Paused anywhere with something recorded, a learner sees "Branch
here" at the paused instant, and pressing it branches there reproducing the
trunk element-wise; marks and setting changes stay offered beside it; and
`docs/ARCHITECTURE.md` describes the fourth door and the control.
