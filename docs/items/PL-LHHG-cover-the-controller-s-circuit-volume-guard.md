---
id: PL-LHHG
title: Cover the controller's circuit-volume guard
priority: P2
effort: S
status: ready
classes: test, infra
feature: core-guard-coverage
touches: tests/integration/test_controller.py
verify: uv run pytest --cov=anesthesia_sim.app.controller --cov-fail-under=100
added: 2026-08-25
---

**Problem.** One guard in `app/controller.py` never executes under the test
suite. Line 293 raises `SimulationConfigurationError("circuit_volume_l is
smaller than stored agent")` when a circuit-volume change would strand more
agent in the circuit than the new volume can hold. It is the controller's only
uncovered statement.

**Why it matters.** It is the guard that stops a live settings change from
leaving the circuit holding more agent than it has room for — a state whose
displayed concentration would exceed 1.0 and be read as a real value. An
untested guard is a guard nobody has confirmed fires.

**Where.** `src/anesthesia_sim/app/controller.py`; the test belongs in
`tests/integration/test_controller.py`.

**First step.** Drive it through the controller's public surface — run the
circuit up to a known agent amount, then request a circuit volume below it —
rather than by constructing the internal state directly. The guard exists to
catch a sequence of user actions, so the test should exercise that sequence.

**Scope.** Tests only. This item may not modify `controller.py` or any other
file outside `touches`. Classed `test, infra` rather than `safety` on purpose:
the class describes the deliverable, which is a test file, not the subject
matter it exercises.

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

**Done when.** The `verify:` command above passes and `make check` is green.

**Worked.** Derived the known circuit agent amount from the public snapshot's
volume and concentration fields.
