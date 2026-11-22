---
id: PL-S6R5
title: RANDOMISED_FRACTION_ROUNDING in tests/reference/test_coupled_dynamics.py is a relative 1e-14 that its comment calls 'a few units in the last place', but it is about 45; record where the number comes from, as test-oracles rule 7 asks
status: done
feature: floating-point-domain
touches: tests/reference/test_coupled_dynamics.py, docs/VERIFICATION.md
added: 2026-11-22
closed: 2026-11-22
pr: 2243
verify: ! grep -qF 'The bound allows a few units in the last place' tests/reference/test_coupled_dynamics.py
---

**Problem.** RANDOMISED_FRACTION_ROUNDING in tests/reference/test_coupled_dynamics.py is a relative 1e-14 that its comment calls 'a few units in the last place', but it is about 45; record where the number comes from, as test-oracles rule 7 asks

**Found by** the session that closed `PL-TV7Q`, 2026-11-22. The comment above `RANDOMISED_FRACTION_ROUNDING` says the relative limit of 1e-14 "allows a few units in the last place". One unit in the last place is at most `sys.float_info.epsilon`, 2.2e-16, of the value, so 1e-14 is about 45 of them. `.claude/rules/test-oracles.md` rule 7 asks the comment to say which kind of limit it is and where its number comes from. `run_rounding` in `src/anesthesia_sim/core/rounding.py` gives 1.1e-11 for 600 one-second steps of three squarings, so a derived limit would be about a thousand times looser than this one. That is a change to a reference test's limit, which the project owner reads first.

**Done when.** The comment names the limit's kind and where 1e-14 comes from, or the limit is replaced by a derived one with the owner's agreement.

**Done 2026-11-22**, on `claude/project-thread-v9awbd`, in the same pull request as `PL-TV7Q`. The limit stays at 1e-14; the comment above `RANDOMISED_FRACTION_ROUNDING` now says what it is.

1. **Its size in units in the last place.** One unit in the last place of a value is between 2**-53 and 2**-52 of it, so 1e-14 of the highest delivered fraction is 45 to 90 units. Over the highest delivered fractions of the nine seeded runs, computed with `math.ulp`, it is 49 to 78 units. The brief's "about 45" was the lower end only.
2. **Its kind.** A numerical limit on rounding, and a fixed allowance in the sense of `core/rounding.py`, not a derived bound.
3. **Why not the derived bound.** `run_rounding(3, StepCount(600))` is 1.07e-11, 1 066 times this limit, so a limit there would let a compartment rise a thousand times further above what was delivered before the check failed.
4. **Why the tighter limit is safe.** `propagator_rounding(3)` is 1.8e-14, already above the allowance, so the allowance holds only because no compartment comes near the ceiling. Re-measured on 2026-11-22 by stepping the nine seeded runs: the highest compartment reached 0.681 of the highest fraction delivered. That measurement now lives in `docs/VERIFICATION.md` § "The tests and the figures behind the comparison", under the random runs, and the comment points there. The comment also says that runs whose phases were long enough to reach equilibrium would need the limit set again.

So the limit is mis-described, not wrong: no run tested comes within a third of it. The comment inside `test_randomised_control_trajectories_keep_every_invariant` that said "A few units in the last place" now names the constant. No assertion or value changed.

**Generator check.** An instance of the fact that `PL-GJ1W` (no one place states how far a computed value can be from the exact one) names: a measured rounding figure standing in for, or copied beside, the bound it should be checked against. That head is still open, so this is not a re-entry; it was found by `PL-TV7Q`, which is under the same head.
