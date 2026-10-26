---
id: PL-PM67
title: docs/MODEL.md says the fractions cannot leave their physical range and no parameter set can trigger the capacity guard, and core/exceptions.py says no step can raise SimulationNumericalError, but the Metzler argument proves only the lower bound, and rounding carries a fraction just above 1 from a saturated state
priority: P1
effort: S
status: done
classes: docs, science
feature: replay-findings
touches: docs/MODEL.md, src/anesthesia_sim/core/exceptions.py, tests/unit/test_uptake_system_failure.py
added: 2026-10-25
closed: 2026-10-26
pr: 1864
payoff: the specification no longer states an upper-bound guarantee that rounding breaks from a saturated state
verify: ! grep -qF 'the fractions cannot leave their physical range' docs/MODEL.md && ! grep -qF 'Under the exact step, no parameter set triggers the' docs/MODEL.md && ! grep -qF 'No step, whatever its size, can produce this error' src/anesthesia_sim/core/exceptions.py
---

**Problem.** `docs/MODEL.md` § "Selected method (as implemented)" says "the fractions cannot leave their physical range" and "no patient file or agent can trigger the compartment capacity guard". § "Supported simulation step" says "no parameter set triggers the guard". The `SimulationNumericalError` docstring in `src/anesthesia_sim/core/exceptions.py` says "No step, whatever its size, can produce this error". A nonnegative propagator keeps fractions at or above 0 but says nothing about 1. Reproduced on main: with every compartment at 1.0 and a 100% dial, the first 0.1 s step fails with `SimulationNumericalError` in 12 of 12 agent and flow cases. The `advance` docstring (`uptake_system.py`) already states the narrower, correct claim.

**Why it matters.** The shipped vaporizer maxima keep every fraction far below 1, so no run hits this. But the specification states a guarantee it does not have, and no test checks the upper bound. Narrow the two documents to match the `advance` docstring. The exceptions docstring also ignores the settings-record failure that `advance` restates as this error.

**Done when.** `docs/MODEL.md` § "Selected method (as implemented)" and § "Supported simulation step", and the `SimulationNumericalError` docstring, claim only what the Metzler argument proves, that a step cannot drive a fraction negative, as the `advance` docstring does. None says a fraction cannot leave its physical range or that no step can raise the error.

**Found by.** `PL-TBQS` reviewer replay on #376, findings r03 F1 and r05 F2. Checked against main on 2026-10-25 with `scripts/c_upper.py`.
