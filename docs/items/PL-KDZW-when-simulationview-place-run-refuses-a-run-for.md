---
id: PL-KDZW
title: When SimulationView._place_run refuses a run for a missing unconditional value, the run's transport row, banner, readouts and record are already in the shared layouts and stay there, so a refused branch from add_run leaves frozen widgets that no slot will ever refresh or remove
priority: P3
effort: S
status: done
classes: defect
feature: replay-findings
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py
added: 2026-10-25
closed: 2026-10-31
pr: 1895
payoff: a layout defect fails visibly instead of leaving a frozen second run on screen
verify: grep -q 'def test_a_run_refused_for_a_missing_unconditional_value_leaves_no_widgets' tests/integration/test_simulation_view.py
---

**Problem.** `_place_run` puts every holder into the shared layouts (`app/simulation_view.py`). It then calls `_require_unconditional_values`, and only after that adds the run to `_runs` and `_slots`. When the check raises, nothing removes the holders. On the branch path, `BranchedCase` has already kept the branch.

**Why it matters.** A layout defect would leave a plausible second run on screen. Its clock would be frozen at the fork, and its delivered and 1 MAC lines would be blank. That is a stale value instead of an obvious failure. The refusal should run before placement, or remove the holders as `_remove_run` does.

**Done when.** A run that `_place_run` refuses leaves none of its widgets in the shared layouts. `tests/integration/test_simulation_view.py` has `test_a_run_refused_for_a_missing_unconditional_value_leaves_no_widgets`.

**Found by.** `PL-TBQS` reviewer replay on #1585, findings r03 F3 and r05 F2, checked against main on 2026-10-25 by reading `_place_run`.

**Built (2026-10-31).** The region check reads where the run's widgets are, so it cannot run before they are placed. When it refuses the run, `_place_run` now removes the run the same way `_remove_run` removes a dropped branch, taking out its holders and its readings in the trunk's panels, and then raises. A branch that `BranchedCase` kept but the dashboard never drew is already dropped at the trunk's next Reset (`_handle_case_restarted`).
