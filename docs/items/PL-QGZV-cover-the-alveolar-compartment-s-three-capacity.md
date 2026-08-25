---
id: PL-QGZV
title: Cover the alveolar compartment's three capacity and type guards
priority: P2
effort: S
status: ready
classes: test, infra
feature: core-guard-coverage
touches: tests/unit/test_alveolar.py
verify: uv run pytest tests/unit/test_alveolar.py --cov=src/anesthesia_sim/core/alveolar.py --cov-fail-under=100
added: 2026-08-25
---

**Problem.** Three guards in `core/alveolar.py` never execute under the test suite.
Line 42 raises `SimulationConfigurationError("agent_amount_l exceeds the
alveolar capacity for a concentration fraction of 1")`; line 96 raises
`SimulationConfigurationError("blood_uptake_l must be a number")`; line 106
raises `SimulationConfigurationError("blood transfer would exceed alveolar
capacity")`. Coverage confirms all three as unreached.

**Why it matters.** These are the guards that stop a misconfigured simulation
from running and producing a plausible but wrong clinical value. An untested
guard is a guard nobody has confirmed fires — it can be broken by a later
refactor with the whole suite still green, which is precisely the failure the
guards exist to prevent.

**Where.** `src/anesthesia_sim/core/alveolar.py`; the tests belong in `tests/unit/test_alveolar.py`.

**First step.** One test per guard: construct the invalid input, assert the
exception type and match the message given above. Assert the *specified*
message, not whatever the code happens to emit — if the two disagree, that is
a finding to capture, not a test to adjust.

**Scope.** Tests only. This item may not modify `src/anesthesia_sim/core/alveolar.py` or any other file
outside `touches`; the guards are the specification and are not being
changed. It is classed `test, infra` rather than `safety` on purpose: the
class describes the deliverable, which is a test file, not the subject matter
it exercises. Editing the guard itself would be safety work and a different
item.

**Done when.** `uv run pytest tests/unit/test_alveolar.py --cov=src/anesthesia_sim/core/alveolar.py --cov-fail-under=100`
passes and `make check` is green.
