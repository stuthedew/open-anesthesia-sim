---
id: PL-S6R5
title: RANDOMISED_FRACTION_ROUNDING in tests/reference/test_coupled_dynamics.py is a relative 1e-14 that its comment calls 'a few units in the last place', but it is about 45; record where the number comes from, as test-oracles rule 7 asks
status: untriaged
feature: floating-point-domain
touches: tests/reference/test_coupled_dynamics.py
added: 2026-11-22
---

**Problem.** RANDOMISED_FRACTION_ROUNDING in tests/reference/test_coupled_dynamics.py is a relative 1e-14 that its comment calls 'a few units in the last place', but it is about 45; record where the number comes from, as test-oracles rule 7 asks

**Found by** the session that closed `PL-TV7Q`, 2026-11-22. The comment above `RANDOMISED_FRACTION_ROUNDING` says the relative limit of 1e-14 "allows a few units in the last place". One unit in the last place is at most `sys.float_info.epsilon`, 2.2e-16, of the value, so 1e-14 is about 45 of them. `.claude/rules/test-oracles.md` rule 7 asks the comment to say which kind of limit it is and where its number comes from. `run_rounding` in `src/anesthesia_sim/core/rounding.py` gives 1.1e-11 for 600 one-second steps of three squarings, so a derived limit would be about a thousand times looser than this one. That is a change to a reference test's limit, which the project owner reads first.

**Done when.** The comment names the limit's kind and where 1e-14 comes from, or the limit is replaced by a derived one with the owner's agreement.
