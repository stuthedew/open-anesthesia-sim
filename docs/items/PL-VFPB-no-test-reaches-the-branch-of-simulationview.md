---
id: PL-VFPB
title: No test reaches the branch of SimulationView._require_unconditional_values that refuses a declared value inside the layout container, because both cases of the refusal test fail through the "outside the region" branch first, so deleting that branch leaves the suite green
priority: P3
effort: S
status: ready
classes: test
feature: replay-findings
touches: tests/integration/test_simulation_view.py
added: 2026-10-25
payoff: the one check that stops the unconditional region from moving into a closable Area is under test
verify: grep -q 'def test_a_region_placed_inside_the_layout_container_is_refused' tests/integration/test_simulation_view.py
---

**Problem.** The guard refuses a widget that is outside the region (`app/simulation_view.py`). It also refuses one that sits inside the Areas. `test_a_run_whose_region_lacks_a_declared_value_is_refused` points ONE_MAC at a View in the Areas, and that View is outside the region, so the test fails through the first branch (`tests/integration/test_simulation_view.py`). The second branch guards against the region itself ending up inside the layout container.

**Why it matters.** That branch is the only check against a future change that moves the region into an Area, where a learner could close it. A case that places the region, or a widget already in it, inside `_areas` would exercise it.

**Done when.** `tests/integration/test_simulation_view.py` has `test_a_region_placed_inside_the_layout_container_is_refused`, which puts the region, or a widget already in it, inside `_areas` and fails if the second branch of `_require_unconditional_values` is deleted.

**Found by.** `PL-TBQS` reviewer replay on #1585, finding r02 F3, checked against main on 2026-10-25 by reading the guard and the test.
