---
id: PL-LHBY
title: A branch halted on a learner's mark reports nothing, because the marks panel draws standings from the reference run only
priority: P1
effort: M
status: ready
classes: defect, safety
feature: two-run-attribution
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/qt_widgets.py, tests/integration/test_simulation_view.py, tests/unit/test_dashboard_frame.py
added: 2026-09-20
payoff: stops the screen asserting a mark was reached by a run that provably could not reach it, and stops a branch halting at a learner's mark with nothing on screen saying why
verify: grep -q 'def test_a_branch_halted_on_a_mark_says_so' tests/integration/test_simulation_view.py
---

**Problem.** A branch halted on a learner's mark reports nothing, because the marks panel draws standings from the reference run only

**Why it matters.** `_refresh_view` passes one snapshot to the marks panel -
`self._refresh_bookmarks(snapshots[0])` - and `bookmark_panel` renders that
run's `bookmark_standings`. The *set* of marks is the same on every displayed
run, which is what that method's docstring argues and what
`test_every_displayed_run_carries_the_same_marks_after_an_add_and_a_removal`
asserts. The *standings* are not: `SimulationController._bookmark_standings`
passes `opened_at_s=(0.0 if self._opened_from is None else
self._opened_from.elapsed_s)`, and a branch starts with empty
`_reached_instants_s` and `_reached_crossings`. So the panel presents one
run's answer as the case's, in both directions.

**Reproduced offscreen against the merged tree, 2026-09-20**, by the
adversarial review of `#784` and again by two independent verifiers:

- *Silent negative.* A MAC target of 0.50 ×MAC on Alveolar; trunk to 1m with a
  fresh-gas-flow keyframe; fork at 1m; the branch's delivered concentration
  raised and started. The branch halts at 114.7 s on the crossing. On screen
  its status word reads "Paused", its notice banner is empty, and the targets
  row reads `Alveolar 0.50 ×MAC` with no standing - because the trunk is
  `still_running` for that target. The single-run control with the identical
  mark reads `Alveolar 0.50 ×MAC · reached`. So the one on-screen indication
  that a run stopped at a mark the learner set exists for a lone run and
  vanishes for a branch: the halt is indistinguishable from a Pause.
- *False positive.* A time bookmark at 30 s that the trunk reached; continue
  to 1m; fork at 1m. The branch's own standing is `before_this_branch` - it
  can never reach that mark - yet the row reads `30s – check · reached`.

**The safety reading.** `CLAUDE.md` names the correct number under the wrong
patient context as a failure of the value, and a mark's standing is a claim
about *which run* got there. The false positive is the worse half: the screen
asserts `reached` of a mark the displayed branch provably cannot reach.
`MarkStanding.BEFORE_THIS_BRANCH` and its rendering exist in
`app/bookmarks.py` precisely so a learner is not told something false about an
inherited mark, and no screen this change makes reachable can display it.

**Done when.**

1. A mark's standing is drawn per displayed run and named by `run_label` while
   two runs are shown, keeping today's single unnamed standing for one run.
2. `BEFORE_THIS_BRANCH` is reachable on screen.
3. A regression test covers both the silent negative and the false positive.

## Re-checked 2026-09-20 against `main` after `PL-3K9B` landed

**The defect is unchanged and was verified directly:**
`SimulationView._refresh_view` still calls `self._refresh_bookmarks(snapshots[0])`,
and `SimulationController._bookmark_standings` still computes from the run's own
`opened_at_s`, `_reached_instants_s` and `_reached_crossings`. One run's answer
is still presented as the case's.

**One number in the reproductions above may have moved, and was not re-run.**
`PL-3K9B` (#805) added `PASSED` as a fifth `MarkStanding` and decides a *time*
bookmark's standing from the run's own clock. The false-positive reproduction
used a time bookmark at 30 s with a fork at 60 s and recorded the branch's own
standing as `before_this_branch`; under `PL-3K9B` a branch whose clock stands at
60 s is at-or-behind that mark, so its standing is now most likely `PASSED`.
**That changes which wrong word the panel shows, not whether it shows one** -
the trunk reads `reached`, the branch reads something else, and the panel
renders only the trunk's. The MAC-target half is untouched by `PL-3K9B`, which
moved time bookmarks alone.

Re-run both halves before writing the regression test, and correct the standing
named above rather than trusting it. It is recorded as unverified deliberately:
this item exists because a brief asserted something about standings that was
true of the mark set instead, and repeating that shape here would be the same
error one layer down.
