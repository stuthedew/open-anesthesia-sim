---
id: PL-LHHG
title: Cover the controller's circuit-volume guard
priority: P2
effort: S
status: ready
classes: test, infra
feature: core-guard-coverage
touches: tests/integration/test_controller.py
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

**Verify.** `uv run pytest tests/integration/test_controller.py --cov=src/anesthesia_sim/app/controller.py --cov-fail-under=100`

This is the command that proves the item done. It moves to a `verify:`
front-matter field once PL-G3TG lands; until then the store rejects the
field, which is the checker working as intended.

**Done when.** The `verify:` command above passes and `make check` is green.
