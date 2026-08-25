---
id: PL-7QS3
title: Cover the patient's perfusion-sum guard
priority: P2
effort: S
status: ready
classes: test, infra
feature: core-guard-coverage
touches: tests/unit/test_patient.py
verify: uv run pytest --cov=anesthesia_sim.core.patient --cov-fail-under=100
added: 2026-08-25
---

**Problem.** One guard in `core/patient.py` never executes under the test suite. Line 45
raises `SimulationConfigurationError("tissue perfusion fractions must sum to
1")` when the fractions miss 1.0 by more than `FLOW_FRACTION_TOLERANCE`.
Coverage confirms it as unreached.

**Why it matters.** These are the guards that stop a misconfigured simulation
from running and producing a plausible but wrong clinical value. An untested
guard is a guard nobody has confirmed fires — it can be broken by a later
refactor with the whole suite still green, which is precisely the failure the
guards exist to prevent.

**Where.** `src/anesthesia_sim/core/patient.py`; the tests belong in `tests/unit/test_patient.py`.

**First step.** One test per guard: construct the invalid input, assert the
exception type and match the message given above. Assert the *specified*
message, not whatever the code happens to emit — if the two disagree, that is
a finding to capture, not a test to adjust.

**Scope.** Tests only. This item may not modify `src/anesthesia_sim/core/patient.py` or any other file
outside `touches`; the guards are the specification and are not being
changed. It is classed `test, infra` rather than `safety` on purpose: the
class describes the deliverable, which is a test file, not the subject matter
it exercises. Editing the guard itself would be safety work and a different
item.

Cover both sides of the tolerance: a sum outside it raises, and a sum just
inside it does not. A one-sided test would pass against a guard that rejects
everything.

**Correction to the `verify:` command (2026-08-25).** The command originally
written here was wrong in two ways, both found by a worker refusing to guess
at it rather than by anyone testing it first.

`--cov=` was given a file path. `pytest-cov` reads that as a module name, finds
nothing imported under it, and reports no data — the run then fails
`--cov-fail-under`, so it fails loudly rather than passing falsely, but it
proves nothing about the guards.

Scoping the run to this item's own test file also demanded more than the item
asks: lines covered by the rest of the suite show as uncovered when only one
test file runs, so `--cov-fail-under=100` could not be reached without writing
tests outside this item's scope.

The corrected command runs the whole suite with coverage scoped to the module,
which measures exactly what this item is responsible for.

**Done when.** the `verify:` command above
passes and `make check` is green.

**Worked.** Nothing the brief did not specify.
