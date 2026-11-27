---
id: PL-NV1C
title: pytest given tests/integration/simulation_view/X, then tests/integration/test_run_surfaces.py, then tests/integration/simulation_view/Y on one command line fails Y with fixture 'application' not found, so a session's targeted run can fail for an order of paths
priority: P3
effort: S
status: done
classes: defect
touches: tests/integration/simulation_view/conftest.py, tests/integration/test_run_surfaces.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-22
closed: 2026-11-27
pr: 2340
payoff: a targeted test run passes or fails on the tests, not on the order the paths were typed
---

**Problem.** pytest given tests/integration/simulation_view/X, then tests/integration/test_run_surfaces.py, then tests/integration/simulation_view/Y on one command line fails Y with fixture 'application' not found, so a session's targeted run can fail for an order of paths

**Found 2026-11-22** by the worker building `PL-CPF2` and `PL-57LD`. The same files run in the order simulation_view X, simulation_view Y, then `tests/integration/test_run_surfaces.py` pass, so the failure depends on which conftest the run collects first, not on the tests.

**Why it matters.** A session running a targeted set of tests can see a failure that is not in the tests, and spend time on it, as the `PL-CPF2` worker did.

**Done when.** A test or a documented run shows the three files pass in either order on one command line.

**Generator check.** The `application` fixture is defined separately in at least ten test modules and once in `tests/integration/simulation_view/conftest.py`, so which definition a test gets depends on what pytest collected first. One fact, the shared Qt application fixture, held in many places; no head states it. One-off until a second reader is found.

**Done 2026-11-27.** The cause was pytest's and not this repository's. With the paths `simulation_view/X`, `test_run_surfaces.py`, `simulation_view/Y` on one command line, pytest 9.1.1 collected `tests/integration/` a second time for the file given on its own, which made a second node for `tests/integration/simulation_view/`. The conftest's fixtures stayed bound to the first node, and pytest 9 matches a conftest fixture to a test by that node, so `Y` found no `application`. Its own `_torn_down_views`, which is autouse, did not run for `Y` either, with no error. A probe of four files with no Qt in them gave the same failure on pytest 9.1.1 and passed on 8.0.0, 8.4.2 and 9.2.0. pytest's changelog for 9.2.0 lists the fix as issue 14635: "Fixed fixture resolution failures when specifying multiple test paths on the command line that share common parent directories" (read 2026-11-27 from the changelog on pytest's main branch).

So `pyproject.toml` now asks for `pytest>=9.2.0`, with the reason in a comment beside it, and `uv.lock` holds 9.2.0, released 2026-10-27. pytest 9.2.0 moved `ApproxScalar`, which `tests/conftest.py` wraps to refuse a tolerance below the spacing of floating-point numbers, from `_pytest.python_api` to `_pytest.approx`. The import follows it.

**Documented run.** On 9.2.0, `pytest -q tests/integration/simulation_view/test_simulation_view_halt.py tests/integration/test_run_surfaces.py tests/integration/simulation_view/test_simulation_view_loops.py` gives 50 passed. On 9.1.1 the same command gave 18 passed and 32 errors, all in `test_simulation_view_loops.py`, each "fixture 'application' not found".

**Generator check, answered.** The brief counted the `application` fixture in ten test modules and one conftest. The duplicates did not cause this failure, and a conftest fixture is what pytest 9.2.0 now resolves correctly, so they are left as they are.
