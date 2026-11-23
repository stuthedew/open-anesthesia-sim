---
id: PL-FKVR
title: The test suite sets no time limit per test, so a fault that makes a loop run forever hangs the run until the CI job's own limit instead of failing one test
priority: P3
effort: S
status: ready
classes: infra
touches: pyproject.toml, uv.lock
added: 2026-11-23
filed-pr: 2281
payoff: a test that loops forever fails by name in minutes instead of hanging the checks until the job limit
---

**Problem.** The test suite sets no time limit per test, so a fault that makes a loop run forever hangs the run until the CI job's own limit instead of failing one test

**What happens.** No per-test time limit is set: `pyproject.toml` loads no timeout plugin, and CI's only limit is each job's `timeout-minutes`. Sorting `PL-00Y5`'s survivors on 2026-11-23 found a mutant of `_dropped` in `layout/sizing.py` (87) that makes `tests/unit/test_layout_sizing.py::test_a_tree_too_large_to_weigh_whole_drops_only_the_areas_that_clear_its_shortfall` loop forever. mutmut counts that as a kill only because it sets its own time limit.

**Why it matters.** A real fault of that kind would hang a pull request's checks until the job's limit, and the log would not name the test.

**What to do.** Research how comparable Python projects bound a test's run time, such as pytest-timeout, before choosing a limit, and check how it interacts with pytest-xdist and with the Qt tests.

**Done when.** A per-test time limit is chosen after reading how comparable projects bound a test's run time, and a test shows that a test which loops forever fails with its own name in the log, under the parallel runner and the Qt tests.

**Generator check.** A one-off: a missing guard, found by one mutant.

**Reproduced 2026-11-23.** `pyproject.toml` names no timeout setting or plugin.
