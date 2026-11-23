---
id: PL-FKVR
title: The test suite sets no time limit per test, so a fault that makes a loop run forever hangs the run until the CI job's own limit instead of failing one test
priority: P3
effort: S
status: done
classes: infra
touches: pyproject.toml, uv.lock, .claude/hooks/guard.py, docket.toml, tests/unit/test_guard.py, tests/unit/test_per_test_time_limit.py
added: 2026-11-23
closed: 2026-11-23
pr: 2308
filed-pr: 2281
payoff: a test that loops forever fails by name in minutes instead of hanging the checks until the job limit
tests: tests/unit/test_per_test_time_limit.py::test_the_configuration_sets_a_time_limit_for_each_test, tests/unit/test_per_test_time_limit.py::test_pytest_resolves_that_limit_with_the_method_that_fails_one_test, tests/unit/test_per_test_time_limit.py::test_a_test_that_never_ends_fails_by_name_and_the_run_finishes, tests/unit/test_guard.py::test_a_guard_puts_back_the_alarm_it_replaced
---

**Problem.** The test suite sets no time limit per test, so a fault that makes a loop run forever hangs the run until the CI job's own limit instead of failing one test

**What happens.** No per-test time limit is set: `pyproject.toml` loads no timeout plugin, and CI's only limit is each job's `timeout-minutes`. Sorting `PL-00Y5`'s survivors on 2026-11-23 found a mutant of `_dropped` in `layout/sizing.py` (87) that makes `tests/unit/test_layout_sizing.py::test_a_tree_too_large_to_weigh_whole_drops_only_the_areas_that_clear_its_shortfall` loop forever. mutmut counts that as a kill only because it sets its own time limit.

**Why it matters.** A real fault of that kind would hang a pull request's checks until the job's limit, and the log would not name the test.

**What to do.** Research how comparable Python projects bound a test's run time, such as pytest-timeout, before choosing a limit, and check how it interacts with pytest-xdist and with the Qt tests.

**Done when.** A per-test time limit is chosen after reading how comparable projects bound a test's run time, and a test shows that a test which loops forever fails with its own name in the log, under the parallel runner and the Qt tests.

**Generator check.** A one-off: a missing guard, found by one mutant.

**Reproduced 2026-11-23.** `pyproject.toml` names no timeout setting or plugin.

**Research, 2026-11-23.** pytest-timeout is the plugin that the item names, and its own description (the 2.4.0 release's package metadata, § "Timeout Methods") gives two methods. The `signal` method, the default where SIGALRM exists, schedules an alarm when a test starts and fails that test with `pytest.fail()` when it expires, so "the test run can complete normally". The `thread` method ends the whole process, so the results already collected and fixture teardown are lost. The same section warns that code under test which sets SIGALRM itself interferes with the `signal` method. NumPy passes `--timeout=600` in its Linux CI jobs and lists the plugin in its `test-core` dependency group (`.github/workflows/linux.yml` and `pyproject.toml` on NumPy's `main`, read 2026-11-23). PyPI's record of the plugin (read 2026-11-23) lists 2.5.0 as yanked, "accidental breaking change (probably)", so 2.4.0 is the newest that installs.

**Done 2026-11-23.** `pyproject.toml` adds `pytest-timeout>=2.4.0` to the `dev` group and sets `timeout = 300` in `[tool.pytest.ini_options]`, with the `signal` method left as the default. Its comment gives the measurement behind the number: on 2026-11-23, on `main`, with `-n 4` and another full check running, the four slowest tests took 124.6, 86.1, 66.9 and 66.0 seconds, so 300 seconds is about 2.4 times the slowest. `uv.lock` pins 2.4.0. `tests/unit/test_per_test_time_limit.py` checks that the setting is a whole number of seconds above zero and that a nested `pytest --collect-only` reports "timeout: 300.0s" and "timeout method: signal". Both fail with the setting removed. A third test, `test_a_test_that_never_ends_fails_by_name_and_the_run_finishes`, runs two endless tests under this repository's `pyproject.toml` with the limit cut to 2 seconds and two parallel workers, one of them after showing a Qt widget, and checks that each fails under its own name with "Failed: Timeout (>2.0s) from pytest-timeout." It takes about 4 seconds. With the `thread` method the run also reports two failures, but as crashed workers with no test's own report, and the test fails. The file imports no `anesthesia_sim`, so `docket.toml`'s `workflow_paths` lists it.

Checked by hand as well: a test blocked inside `QApplication.exec()` is not interrupted, because no Python runs there to take the signal. No test enters that loop today, and the comment says so. Under `pytest-xdist` the plugin runs inside each worker, and the unit and docket suites passed with it on, 11,167 tests in 295.6 seconds. The mutation run reads the same configuration from inside `mutants/`, and mutmut 3.8.0's own limit stops a looping mutant first in most cases; where the limit here fires first, the tool reports the mutant as killed rather than timed out, and `CAUGHT` in `tools/diff_mutation.py` counts both.

Found while doing it and fixed in this change: `.claude/hooks/guard.py`'s `_verdict` sets its own SIGALRM to stop a slow guard, the interference the plugin's description warns about. It replaced the plugin's handler and cancelled its alarm, so every test that ran a guard lost the limit for the rest of that test. `_verdict` now puts back the outer handler and the time left on the outer alarm, and an alarm that fell due while the guard ran fires a millisecond after it returns. `tests/unit/test_guard.py::test_a_guard_puts_back_the_alarm_it_replaced` fails on the old `guard.py`. The item's own search had covered `src/`, `tests/` and `tools/` only; `.claude/hooks/` is on pytest's path too.

Documents checked: `docs/VERIFICATION.md`, `docs/ARCHITECTURE.md`, `README.md` and `docs/worker.md` (none describes how long a test may run); and `docs/mutation-testing.md` (its account of mutmut's own time limits still holds).

**Blind review, 2026-11-23.** None was owed: the change touches the test configuration, the guard hook and their tests, and no simulator path.
