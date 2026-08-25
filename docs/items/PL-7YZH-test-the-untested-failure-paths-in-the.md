---
id: PL-7YZH
title: Test the untested failure paths in the scientific core
priority: P1
effort: M
status: ready
classes: safety
touches: tests/unit/test_alveolar.py, tests/unit/test_blood.py, tests/unit/test_circuit.py, tests/unit/test_tissue.py, tests/unit/test_patient.py, tests/unit/test_parameters.py, tests/unit/test_controller.py, tests/unit/test_simulation_view.py
added: 2026-08-25
---

**Problem.** Seventeen uncovered lines in the package are `raise` statements
or exception handling - the capacity, range and validation guards that stop a
bad input becoming a plausible-looking number. Nothing currently proves any of
them still fires. Reproduce the list with:

```
uv run pytest --cov=src/anesthesia_sim --cov-report=json -q
```

then read `coverage.json` for missing lines that are `raise` or `except`
statements. Measured on the v0.2.3 tree they are:

| File | Lines | Guard |
| --- | --- | --- |
| `core/alveolar.py` | 42, 96, 106 | volume validation, `blood_uptake_l` type, blood transfer exceeding alveolar capacity |
| `core/blood.py` | 47 | `agent_amount_l` exceeding venous blood capacity |
| `core/circuit.py` | 159 | `agent_amount_l` exceeding circuit capacity |
| `core/tissue.py` | 34, 43, 63 | empty name, `perfusion_fraction` above 1, capacity |
| `core/patient.py` | 45 | tissue perfusion fractions not summing to 1 |
| `core/parameters.py` | 117, 124, 136, 150 | empty string, non-integer `schema_version`, non-numeric field, fraction above 1 |
| `app/controller.py` | 293 | `circuit_volume_l` smaller than the agent already stored |
| `app/simulation_view.py` | 109 | `AGENT_COLOR_SCHEMES` not matching the built-in agents |
| `app/simulation_view.py` | 1162, 1168 | `_halt_run`'s swallowed render failure |

**Why it matters.** Overall coverage is 96%, which is exactly why this never
surfaced: these lines sit in modules that are well covered in aggregate, so
the number stays high while the failure branch beneath it is never exercised.
`CLAUDE.md` requires boundary, invalid-input and pathological-input tests for
safety-critical paths, and these guards *are* the "prefer an obvious failure
to a plausible-looking number" mechanism - they are what stands between a
malformed parameter file or an out-of-range capacity and a displayed
concentration a clinician might read. An untested guard is one refactor away
from being an unreachable guard, and nothing would fail.

**Where.** The tests, not the source: the guards themselves are believed
correct. Add invalid-input cases alongside the existing nominal tests for each
module in the table.

**Note on `_halt_run`.** `app/simulation_view.py:1160-1168` swallows an
exception from `_refresh_and_render` on purpose, and both the `noqa` and the
comment explaining it are right: the run is already stopped, and a frozen
display over a stopped simulation is at worst uninformative, where one over a
*running* simulation is actively misleading. What is missing is a test that
the path behaves that way - that a render failure during a halt leaves the
controller stopped and does not propagate. Do not "fix" the suppression.
(The `noqa` there is itself inert under the current ruleset; that is PL-69J3's
subject, not this item's.)

**Done when.** Every line in the table above is exercised by a test that
asserts the specific exception type and the condition that triggers it, and a
coverage run reports no uncovered `raise` or `except` line in
`src/anesthesia_sim`.
