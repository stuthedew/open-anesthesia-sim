---
id: PL-076B
title: Two tests check less than docs/MODEL.md says: a negative amount of agent is tried at -1e-12 L and not at the nearest value below zero, and the display-path bounds are 5 to 10 times looser than the figures docs/INTERFACE.md prints
status: untriaged
feature: model-spec-accuracy
added: 2026-11-21
---

**Problem.** Two tests check less than docs/MODEL.md says: a negative amount of agent is tried at -1e-12 L and not at the nearest value below zero, and the display-path bounds are 5 to 10 times looser than the figures docs/INTERFACE.md prints

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21.

1. **A negative amount of agent.** § "The numerical envelope": "A test in `tests/unit/test_governing_equations.py` sets each fraction and amount to the nearest storable value past each limit and expects a refusal." The fractions use `nextafter(0.0, -1.0)` and `nextafter(1.0, 2.0)`, and the upper limit of an amount uses `nextafter(MAXIMUM_CUMULATIVE_AGENT_L, inf)`. The lower limit of the two amounts is tried at `-1e-12` (`test_require_canonical_state_refuses_a_negative_amount_of_agent`). A check that allowed a small negative amount would pass. `EDGES` in `tests/unit/test_numerical_envelope_sweep.py` has no entry for the starting state, so the sweep does not cover it either. The fix is `nextafter(0.0, -1.0)` beside or in place of `-1e-12`.
2. **The display-path bounds.** § "Canonical evaluation test": "A test checks it against a bound for each quantity, so a change to how values are computed cannot silently move a figure that `docs/INTERFACE.md` prints." `docs/INTERFACE.md` § "The canonical evaluation rule" prints "less than a ten-millionth" of 0.1 L for the running totals, which is 1e-8 L, and "about a hundred-millionth of its 0.01% step" for a fraction, which is 1e-12. `tests/reference/test_canonical_evaluation.py` asserts `WORST_ACCUMULATOR_SEPARATION = 5e-8` and `WORST_FRACTION_SEPARATION = 1e-11`. The measured differences are 3.1e-9 L and 8.0e-13, so the printed figures are true today. A change could move the totals' difference to 4e-8 L, past the printed figure, and the test would pass. Either tighten the two bounds to the printed figures, or word the sentence as "cannot move the difference by more than an order of magnitude unnoticed". `PL-SZ6G` (a run's time as a whole number of seconds) will change the measured differences, so choose after it merges.

**Done when.** The negative-amount test uses the nearest value below zero, and the display-path bounds and the sentence about them agree.
