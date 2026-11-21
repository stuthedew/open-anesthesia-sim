---
id: PL-076B
title: Two tests check less than docs/MODEL.md says: a negative amount of agent is tried at -1e-12 L and not at the nearest value below zero, and the display-path bounds are 5 to 10 times looser than the figures docs/INTERFACE.md prints
priority: P2
effort: S
status: done
classes: defect
feature: model-spec-accuracy
touches: tests/unit/test_governing_equations.py
deferred-from: v0.7.0 - captured after the freeze by the check of docs/MODEL.md against the code; it changes no displayed value, and it is not safety or science
added: 2026-11-21
closed: 2026-11-21
pr: 2190
payoff: a check that let through a small negative amount of delivered or exhausted agent fails a test, as docs/MODEL.md says it does
tests: tests/unit/test_governing_equations.py::test_require_canonical_state_refuses_a_negative_amount_of_agent
---

**Problem.** Two tests check less than docs/MODEL.md says: a negative amount of agent is tried at -1e-12 L and not at the nearest value below zero, and the display-path bounds are 5 to 10 times looser than the figures docs/INTERFACE.md prints

**Why it matters.** `docs/MODEL.md` tells a reader that a test tries each limit at the nearest storable value, and that a test keeps the printed display-path figures true. Where a test checks less than that, a change that loosens the limit or moves a printed figure passes.

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21.

1. **A negative amount of agent.** § "The numerical envelope": "A test in `tests/unit/test_governing_equations.py` sets each fraction and amount to the nearest storable value past each limit and expects a refusal." The fractions use `nextafter(0.0, -1.0)` and `nextafter(1.0, 2.0)`, and the upper limit of an amount uses `nextafter(MAXIMUM_CUMULATIVE_AGENT_L, inf)`. The lower limit of the two amounts is tried at `-1e-12` (`test_require_canonical_state_refuses_a_negative_amount_of_agent`). A check that allowed a small negative amount would pass. `EDGES` in `tests/unit/test_numerical_envelope_sweep.py` has no entry for the starting state, so the sweep does not cover it either. The fix is `nextafter(0.0, -1.0)` beside or in place of `-1e-12`.
2. **The display-path bounds.** [superseded 2026-11-21: moved to `PL-8J3W` (the display-path test's bounds against the printed figures), which waits on `PL-SZ6G` (a run's time as a whole number of seconds)]

**Done when.** The negative-amount test tries the nearest value below zero at both amounts.

**What was done, 2026-11-21.** `test_require_canonical_state_refuses_a_negative_amount_of_agent` now tries each of the two amounts at `nextafter(0.0, -1.0)` as well as at `-1e-12`.

**The new cases catch a loosened check, and the old ones do not.** In a scratch copy of `src/`, the check `if value < 0.0:` in `require_nonnegative_finite` (`core/validation.py`) was changed to `if value < -1e-13:`. The two cases at `-1e-12` passed, and the two new cases failed with "DID NOT RAISE SimulationConfigurationError".

**Documents checked.** `docs/MODEL.md` § "The numerical envelope", whose sentence about the nearest storable value past each limit is now true of the lower limit of the two amounts.

**Generator check.** Filed by `PL-RMNP` (the check of `docs/MODEL.md` against the code), a sweep that the owner asked for. The fact it misreads is whether a `docs/MODEL.md` sentence about what the model computes matches what it computes, which the head `PL-B6YV` (a document sentence about what the model computes, checked against the code) already states. It is counted under the sweep and is not a new head.
