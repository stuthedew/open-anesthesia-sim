---
id: PL-LQ19
title: Reset on a case-less dashboard's first run deletes every other run, because _handle_case_restarted is connected without checking that a case exists
priority: P2
effort: S
status: done
classes: defect, ux
feature: branch-run-set-integrity
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py
added: 2026-09-20
closed: 2026-09-20
pr: 788
payoff: stops Reset on one run silently destroying another run's recorded history on any dashboard the case does not own
verify: grep -q 'def test_resetting_a_case_less_dashboards_first_run_keeps_the_others' tests/integration/test_simulation_view.py
---

**Problem.** Reset on a case-less dashboard's first run deletes every other run, because _handle_case_restarted is connected without checking that a case exists

**Why it matters.** `SimulationView` admits a dashboard with no case - that is
what every test builds and what the constructor still documents - and on one of
those the runs are independent trunks rather than a trunk and its branches.
Pressing Reset on the first of them now destroys the second: `_place_run`
connects `RunView.case_restarted` to `_handle_case_restarted` for whichever run
is placed first, with no test that a case exists, and the handler's only guard
is `len(self._runs) == 1`. Reset is the gesture a learner reaches for to start
one run over, and it silently takes the other run's recorded history with it.

Unreachable from `main()`, which always passes a case - but `SimulationView` is
the dashboard's public class, `add_run` is public beside it, and the two-trunk
shape is the one `PL-QRD1`'s own guard was written about. A defect that is
merely unreachable today is the shape this project has been bitten by before:
`PL-QRD1` sat unreachable for five days and became reachable the moment an
entry point was built.

**Found 2026-09-20** by the adversarial review of `#784`, and reproduced
against real widgets under the offscreen platform before being filed: two
independent finders reached it from different directions, and a scratch script
showed `len(view.runs)` going 2 to 1 on a single click of run 1's Reset.

**Done when.**

1. Reset on a case-less dashboard's first run leaves every other run on the
   dashboard, with its history intact.
2. A branch is still dropped when the trunk of a real case is reset.
3. A regression test covers the first, since nothing did.
