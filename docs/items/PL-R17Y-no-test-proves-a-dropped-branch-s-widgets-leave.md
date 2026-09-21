---
id: PL-R17Y
title: No test proves a dropped branch's widgets leave the dashboard; the trunk-Reset test asserts Python-side state only
priority: P2
effort: S
status: ready
classes: test
feature: branch-display-tests
touches: tests/integration/test_simulation_view.py
added: 2026-09-20
payoff: catches a dropped branch whose chrome stays on screen around a run that no longer exists
verify: grep -q 'def test_a_dropped_branchs_widgets_leave_the_dashboard' tests/integration/test_simulation_view.py
---

**Problem.** No test proves a dropped branch's widgets leave the dashboard; the trunk-Reset test asserts Python-side state only

**Found 2026-09-20** by the adversarial review of `#784`, and upheld against
refutation. `PL-VKJW` is what made two runs reachable from a shipped entry
point for the first time, so this is that change's to answer rather than a
pre-existing gap.

**Why it matters.** `SimulationView._remove_run` does real widget work: it stops
the run's timers, disconnects `presentation_requested`, and then calls
`setParent(None)` and `deleteLater()` on each of the eight widgets in
`_RunSlots.placed` and on the `RunView` itself. Its docstring says why that
matters - "the widgets deleted here are ones the view would write on its next
refresh". None of it is asserted.

`test_resetting_the_trunk_ends_the_comparison` is the test that covers the drop.
It checks `len(view.runs) == 1`, that a new `case` was built with no branches,
`view._legend._run_count == 1`, and the surviving run's name and the fork
panel's controls. A dropped branch whose header badge, transport row, notice,
sidebar panels, off-scale line, wash-in line, readouts and parameter section all
stayed parented in their shared layouts would satisfy every one of those
assertions, and the learner would see a second run's chrome around a run that no
longer exists.

**The title overstates one clause and the correction matters for whoever takes
it.** That test does assert widget state - `_run_name_text.isHidden()`,
`_fork_panel.take_button.isHidden()`, `lock_text.isHidden()`. What it never
asserts is anything about the *departed* branch's widgets, which is the gap.
Read the item as "no test proves the dropped branch's widgets leave", not as
"the test reads no widgets".

**Verified 2026-09-20** against `src/anesthesia_sim/app/simulation_view.py`'s
`_remove_run` and `_place_run`, and the body of
`test_resetting_the_trunk_ends_the_comparison` in
`tests/integration/test_simulation_view.py`.

**Done when.** A test takes a fork, resets the trunk, and shows the branch's
placed widgets are gone from the shared layouts they were put into - the
splitter sections included, which is `PL-RS3Z`'s half of the same count read
from the other direction.
