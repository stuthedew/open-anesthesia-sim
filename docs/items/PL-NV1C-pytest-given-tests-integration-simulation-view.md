---
id: PL-NV1C
title: pytest given tests/integration/simulation_view/X, then tests/integration/test_run_surfaces.py, then tests/integration/simulation_view/Y on one command line fails Y with fixture 'application' not found, so a session's targeted run can fail for an order of paths
priority: P3
effort: S
status: ready
classes: defect
touches: tests/integration/simulation_view/conftest.py, tests/integration/test_run_surfaces.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no learner sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-22
payoff: a targeted test run passes or fails on the tests, not on the order the paths were typed
---

**Problem.** pytest given tests/integration/simulation_view/X, then tests/integration/test_run_surfaces.py, then tests/integration/simulation_view/Y on one command line fails Y with fixture 'application' not found, so a session's targeted run can fail for an order of paths

**Found 2026-11-22** by the worker building `PL-CPF2` and `PL-57LD`. The same files run in the order simulation_view X, simulation_view Y, then `tests/integration/test_run_surfaces.py` pass, so the failure depends on which conftest the run collects first, not on the tests.

**Why it matters.** A session running a targeted set of tests can see a failure that is not in the tests, and spend time on it, as the `PL-CPF2` worker did.

**Done when.** A test or a documented run shows the three files pass in either order on one command line.

**Generator check.** The `application` fixture is defined separately in at least ten test modules and once in `tests/integration/simulation_view/conftest.py`, so which definition a test gets depends on what pytest collected first. One fact, the shared Qt application fixture, held in many places; no head states it. One-off until a second reader is found.
