---
id: PL-NYFZ
title: A test tolerance smaller than the gap between neighbouring floating-point numbers at the compared value turns an approximate check into an exact one without saying so (Error Prone's FloatingPointAssertionWithinEpsilon flags this in Java); nothing here checks for it in the simulator's tests (found while researching PL-TN0G)
priority: P3
effort: M
status: ready
classes: feature
feature: dead-test-limits
touches: docs/items, tools/tolerance_spacing_check.py, tests/unit/test_tolerance_spacing_check.py
added: 2026-11-03
payoff: no simulator test passes off an exact comparison as an approximate one, or the item records that none does
verify: grep -q '^\*\*Measured' docs/items/PL-NYFZ*.md
---

**Problem.** A test tolerance smaller than the gap between neighbouring floating-point numbers at the compared value turns an approximate check into an exact one without saying so (Error Prone's FloatingPointAssertionWithinEpsilon flags this in Java); nothing here checks for it in the simulator's tests (found while researching PL-TN0G)

**Why it matters.** A tolerance smaller than the gap between neighbouring floating-point numbers makes an approximate comparison exact. Such a test can fail on a harmless change in rounding, and it does not allow the error its author meant to allow. Error Prone flags this in Java (FloatingPointAssertionWithinEpsilon, https://raw.githubusercontent.com/google/error-prone/master/docs/bugpattern/FloatingPointAssertionWithinEpsilon.md, cited in `PL-TN0G`). `PL-TN0G` left this open as a different check from its dead-limit probe.

**Done when.** The brief records, in a paragraph that starts `**Measured**`, how many tolerances in `tests/` are smaller than `math.ulp` of the value they compare. If any are, each is fixed and a check refuses a new one. If none are, the item is dropped with that count as its reason. A new check under `tools/` is a new workflow mechanism, so building one waits while a workflow-lane head is live. The count does not wait.

**Generator check.** One-off: a check proposed from published practice, not a misread fact.
