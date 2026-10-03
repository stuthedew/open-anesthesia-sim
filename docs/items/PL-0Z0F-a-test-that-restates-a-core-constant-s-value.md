---
id: PL-0Z0F
title: A test that restates a core constant's value passes while the constant moves, and PL-T5J5 found eight by hand at 48 h: perturb each supported_ranges constant on a schedule and fail a test that breaks without importing it
status: untriaged
feature: one-home-for-constants
touches: tools, .github/workflows/drift.yml, tests
added: 2026-10-03
---

**Problem.** A test that restates a core constant's value passes while the constant moves, and PL-T5J5 found eight by hand at 48 h: perturb each supported_ranges constant on a schedule and fail a test that breaks without importing it

**Why it matters.** PL-T5J5 found eight tests holding the 24 h limit as text or literal by setting `MAXIMUM_ELAPSED_SIMULATION_TIME_S` to 48 h and reading which tests broke: 9 of 3,670 failed and 8 of the failures were spurious. That method is deterministic and nobody runs it twice. A test that restates a constant passes on every run until the constant moves, then fails for a reason that is not a defect, which is the one kind of failure that trains a session to edit the test rather than the code.

**Shape.** A scheduled job in `.github/workflows/drift.yml`, not `quality.yml`: one full suite per constant is too slow for a gate on every push. For each public constant in `core/supported_ranges.py`, run the suite with the constant replaced by a distinct wrong value (a `conftest.py` fixture reading one environment variable) and collect the failing tests; a failing test that does not import the constant by name is reported. A test that should fail, such as the pin at `tests/unit/test_supported_ranges.py:169`, imports the name and passes the filter. Standard library plus pytest.

**Done when.** The job runs on its schedule, reports zero restating tests on `main`, and a deliberately restated test on a branch is named in its output.

**Generator check.** Serves PL-40SJ's family from the tests' side; not a head of its own.
