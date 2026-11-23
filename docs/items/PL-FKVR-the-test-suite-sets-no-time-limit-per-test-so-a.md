---
id: PL-FKVR
title: The test suite sets no time limit per test, so a fault that makes a loop run forever hangs the run until the CI job's own limit instead of failing one test
status: untriaged
added: 2026-11-23
filed-pr: 2281
---

**Problem.** The test suite sets no time limit per test, so a fault that makes a loop run forever hangs the run until the CI job's own limit instead of failing one test

**What happens.** No per-test time limit is set: `pyproject.toml` loads no timeout plugin, and CI's only limit is each job's `timeout-minutes`. Sorting `PL-00Y5`'s survivors on 2026-11-23 found a mutant of `_dropped` in `layout/sizing.py` (87) that makes `tests/unit/test_layout_sizing.py::test_a_tree_too_large_to_weigh_whole_drops_only_the_areas_that_clear_its_shortfall` loop forever. mutmut counts that as a kill only because it sets its own time limit.

**Why it matters.** A real fault of that kind would hang a pull request's checks until the job's limit, and the log would not name the test.

**What to do.** Research how comparable Python projects bound a test's run time, such as pytest-timeout, before choosing a limit, and check how it interacts with pytest-xdist and with the Qt tests.
