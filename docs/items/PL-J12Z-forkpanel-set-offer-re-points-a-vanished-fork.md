---
id: PL-J12Z
title: ForkPanel.set_offer re-points a vanished fork instant at induction instead of clearing the selection, so Branch here forks somewhere the learner did not choose
priority: P2
effort: S
status: done
classes: defect, ux
feature: branch-run-set-integrity
milestone: v0.5.0
touches: src/anesthesia_sim/app/qt_widgets.py, tests/integration/test_simulation_view.py
added: 2026-09-20
closed: 2026-09-20
pr: 788
payoff: stops Branch here opening a branch at induction when the learner chose a decision point that has since collapsed
verify: grep -q 'def test_a_vanished_fork_instant_leaves_nothing_selected' tests/integration/test_simulation_view.py
---

**Problem.** ForkPanel.set_offer re-points a vanished fork instant at induction instead of clearing the selection, so Branch here forks somewhere the learner did not choose

**Why it matters.** `ForkPanel.set_offer` rebuilds the selector whenever the
trunk's keyframes change and restores the reader's selection with
`setCurrentIndex(max(self.point_selector.findData(selected_s), 0))`.
`findData` answers `-1` when the instant is gone, and `max(-1, 0)` is `0` -
which is induction. So a learner who selected a decision point that has since
stopped being a keyframe is left with *induction* selected, and "Branch here"
opens a branch at a case instant they never chose.

It is reachable in ordinary use and does not need a reset: a keyframe collapses
when a setting is returned to its previous value at the same instant, which is
what a learner does when they change their mind about a dial while paused.
`CLAUDE.md`'s standard is explicit that a default must not be silently
substituted where doing so could produce a plausible but incorrect clinical
result, and the branch instant is what every later comparison is read against.

**Found 2026-09-20** by the adversarial review of `#784`, and reproduced:
trunk paused at 60 s, fresh gas flow raised to 6 L/min (keyframe at 60 s),
"1m" selected, flow returned to its previous value - `fork_points_s` goes from
`(0.0, 60.0)` to `(0.0,)` and `selected_instant_s()` returns `0.0` with no
notice shown.

**Done when.**

1. A selection whose instant is no longer offered leaves the control with
   nothing selected rather than with induction selected.
2. Pressing the button in that state says so, rather than branching.
3. A regression test covers it.

**Not classed `safety`, and the line is worth stating.** Nothing displayed is
numerically wrong or wrongly attributed: the branch really does open at
induction, its curve is drawn from induction, and `chart_frame`'s run frame
marks the branch point where it actually is. A reader who looks sees the truth.
The defect is that a control did something other than what was selected, which
is a correctness and usability failure rather than a misleading value - so it
is `defect, ux` at `P2`, and `P1` keeps meaning "a clinician could be misled".

`PL-K5NY`, filed beside it, *is* `safety`-classed, and the difference is the
test: there the displayed run carries the wrong patient context, which
`CLAUDE.md` names as a safety failure in terms.
