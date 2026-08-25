---
id: PL-3TMW
title: Cover the tissue compartment's three configuration guards
priority: P2
effort: S
status: ready
classes: test, infra
feature: core-guard-coverage
touches: tests/unit/test_tissue.py
added: 2026-08-25
---

**Problem.** Three guards in `core/tissue.py` never execute under the test suite. Line
34 raises `SimulationConfigurationError("name must be a nonempty string")`;
line 43 raises `SimulationConfigurationError("perfusion_fraction must not
exceed 1")`; line 63 raises `SimulationConfigurationError("agent_amount_l
exceeds the tissue capacity for a concentration fraction of 1")`. Coverage
confirms all three as unreached.

**Why it matters.** These are the guards that stop a misconfigured simulation
from running and producing a plausible but wrong clinical value. An untested
guard is a guard nobody has confirmed fires — it can be broken by a later
refactor with the whole suite still green, which is precisely the failure the
guards exist to prevent.

**Where.** `src/anesthesia_sim/core/tissue.py`; the tests belong in `tests/unit/test_tissue.py`.

**First step.** One test per guard: construct the invalid input, assert the
exception type and match the message given above. Assert the *specified*
message, not whatever the code happens to emit — if the two disagree, that is
a finding to capture, not a test to adjust.

**Scope.** Tests only. This item may not modify `src/anesthesia_sim/core/tissue.py` or any other file
outside `touches`; the guards are the specification and are not being
changed. It is classed `test, infra` rather than `safety` on purpose: the
class describes the deliverable, which is a test file, not the subject matter
it exercises. Editing the guard itself would be safety work and a different
item.

**Verify.** `uv run pytest tests/unit/test_tissue.py --cov=src/anesthesia_sim/core/tissue.py --cov-fail-under=100`

This is the command that proves the item done. It moves to a `verify:`
front-matter field once PL-G3TG lands; until then the store rejects the
field, which is the checker working as intended.

**Done when.** `uv run pytest tests/unit/test_tissue.py --cov=src/anesthesia_sim/core/tissue.py --cov-fail-under=100`
passes and `make check` is green.
