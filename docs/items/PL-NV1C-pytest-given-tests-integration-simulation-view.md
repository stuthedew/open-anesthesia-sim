---
id: PL-NV1C
title: pytest given tests/integration/simulation_view/X, then tests/integration/test_run_surfaces.py, then tests/integration/simulation_view/Y on one command line fails Y with fixture 'application' not found, so a session's targeted run can fail for an order of paths
status: untriaged
added: 2026-11-22
---

**Problem.** pytest given tests/integration/simulation_view/X, then tests/integration/test_run_surfaces.py, then tests/integration/simulation_view/Y on one command line fails Y with fixture 'application' not found, so a session's targeted run can fail for an order of paths

**Found 2026-11-22** by the worker building `PL-CPF2` and `PL-57LD`. The same files run in the order simulation_view X, simulation_view Y, then `tests/integration/test_run_surfaces.py` pass, so the failure depends on which conftest the run collects first, not on the tests.
