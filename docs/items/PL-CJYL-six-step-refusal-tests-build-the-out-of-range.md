---
id: PL-CJYL
title: Six step-refusal tests build the out-of-range SimulationStep inside pytest.raises, so the constructor raises before advance() or steps_per_tick() is called, the entry point they are named for is never exercised, and their "nothing moved" assertions cannot fail, while test_simulation_step.py's docstring says they still pin the refusal at each entry point
priority: P3
effort: S
status: ready
classes: test
feature: replay-findings
touches: tests/unit/test_uptake_system_failure.py, tests/unit/test_simulation.py, tests/unit/test_playback.py, tests/unit/test_simulation_step.py
added: 2026-10-25
payoff: a reader of the tests no longer credits each entry point with a step refusal that no test exercises
verify: ! grep -qF 'still pin them' tests/unit/test_simulation_step.py && ! grep -q 'def test_a_refused_maximum_simulation_step_leaves_the_run_untouched' tests/unit/test_uptake_system_failure.py
---

**Problem.** Each of these tests builds the step as `SimulationStep(...)` inside
the `pytest.raises` block. The tests are
`test_a_refused_maximum_simulation_step_leaves_the_run_untouched`,
`test_a_step_below_the_minimum_simulation_step_is_refused_and_changes_nothing`
and `test_an_invalid_step_is_a_configuration_error_and_changes_nothing`
(`tests/unit/test_uptake_system_failure.py`),
`test_rejects_a_step_above_the_maximum_simulation_step` and
`test_rejects_a_step_below_the_minimum_simulation_step`
(`tests/unit/test_simulation.py`), and
`test_a_step_outside_the_supported_range_is_refused`
(`tests/unit/test_playback.py`). The constructor raises first, so the
entry point is never called. The module docstring of
`tests/unit/test_simulation_step.py` still says "The tests that pinned them at each entry point still pin them".

**Why it matters.** A reader credits each entry point with a refusal these
tests no longer exercise. The docstrings also describe behaviour that is not
under test, such as "Elapsed time must not move for a step that was never
simulated". The tests should be renamed and moved to the constructor tests,
or should build the bad step before the block and assert on the constructor.

**Done when.** The six tests no longer carry names or docstrings that credit an entry point with a refusal they do not exercise: each is renamed for the constructor refusal it tests, or removed where `tests/unit/test_simulation_step.py` already covers it. The module docstring of `tests/unit/test_simulation_step.py` no longer says the entry-point tests still pin the refusals.

**Found by.** `PL-TBQS` reviewer replay on #1328, finding r03 F1. Checked
against main on 2026-10-25 by reading the six tests.
