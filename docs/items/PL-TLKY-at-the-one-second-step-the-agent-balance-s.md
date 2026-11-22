---
id: PL-TLKY
title: At the one-second step the agent balance's fixed limit of one part in 10**9 is below one propagator's derived rounding bound at the stiffest envelope corners (9.3e-9 at 22 squarings), so the check refuses the first step at 8 of the 96 corners, and it is two thirds of the derived bound for a shipped agent's longest run (1.5e-9); decide whether the limit should widen by what squarings add, which PL-D88N recorded as the shape for the day a shipped step first needed a squaring
priority: P1
effort: S
status: needs-decision
classes: safety
feature: floating-point-domain
touches: src/anesthesia_sim/core/rounding.py, src/anesthesia_sim/core/agent_simulation_validation.py, docs/MODEL.md, tests/unit/test_numerical_envelope_sweep.py
deferred-from: v0.7.0 - not live: checked 2026-11-22 at d4e8200c: the fixed limit refuses only at the envelope's stiffest corners (alveolar volume 0.01 L, blood:gas coefficient 10 000), which no shipped agent or patient file reaches; a shipped agent's step needs at most three squarings and its 24-hour residual was at most 9.8e-12, and the limit errs only toward a halt, so no learner can see a wrong value now
added: 2026-11-21
payoff: The check that halts a run whose agent does not add up neither halts a correct run nor lets a real accounting error pass, at every step a run can take.
---

**Problem.** At the one-second step the agent balance's fixed limit of one part in 10**9 is below one propagator's derived rounding bound at the stiffest envelope corners (9.3e-9 at 22 squarings), so the check refuses the first step at 8 of the 96 corners, and it is two thirds of the derived bound for a shipped agent's longest run (1.5e-9); decide whether the limit should widen by what squarings add, which PL-D88N recorded as the shape for the day a shipped step first needed a squaring

**Where it was found.** `PL-SZ6G` (a run's time as a whole number of seconds), 2026-11-21, after `core/rounding.py` was merged in.

**What was measured.** `tests/unit/test_numerical_envelope_sweep.py` takes one one-second step at each of 96 volume and coefficient corners, from 3 openings, 27 flow corners and 2 sets of perfusion fractions: 15 552 first steps. Every step that needs fewer than 22 squarings passes the agent balance. Of the 864 that need 22, the check refuses 76, at 8 corners, and the largest imbalance is 1.7e-9 of the agent handled. All 8 have an alveolar volume of 0.01 L and a blood:gas coefficient of 10 000, with the circuit or the venous pool at 10 000 L. At the 0.1 s step the same corners passed their first step and halted within seconds (`PL-D88N`, the fixed mass-balance tolerance). A shipped agent's step needs 2 squarings at its default flows and 3 at the widest. Its derived bound over 24 h is `run_rounding(3, 86 400)`, 1.5e-9, and the measured residual is at most 9.8e-12.

**What `PL-D88N` recorded.** The project owner kept the limit fixed on 2026-10-31 (ratified), with a test that required every shipped step to need no squaring. The item says that the first failure of that test is "the moment to choose a tolerance that widens only by what the squarings add", and names that shape as its option C. The one-second step is that failure. `PL-SZ6G` restated the test as "at most three squarings" and kept the limit, because the derived bound for the longest shipped run did not grow: it was 1.9e-9 for 24 h at 0.1 s.

**Checked 2026-11-22**, at `d4e8200c`. `grep -n "AGENT_ACCOUNTING_RELATIVE_TOLERANCE" src/anesthesia_sim/core/rounding.py` prints `AGENT_ACCOUNTING_RELATIVE_TOLERANCE: Final = 1e-9`, and its docstring still says that a run at the stiffest envelope corners halts on its first step "although nothing is wrong with its accounting". The limit is still fixed.

**Why it matters.** The agent balance is the check that halts a run whose agent does not add up. A limit below the rounding that a correct step can carry halts a correct run, and a limit above what rounding explains lets a real accounting error pass. Today the fixed limit errs only toward halting, and only at inputs no shipped agent or patient reaches. A shipped agent's longest run has a derived bound of one and a half times the limit, so the limit no longer covers the arithmetic's own worst case.

**Decision needed.** Whether the limit stays at 1e-9 for every run, or widens by what the squarings of the run's own step add. The choice is the owner's, because it sets the threshold of a safety check in `core/`.

**Recommendation:** widen by the squarings, `PL-D88N`'s option C, and keep 1e-9 as the least the limit can be. With `PROPAGATOR_ROUNDING_UNITS` of 10 for each step, option C adds 10 times (2**3 - 1) times 86 400 times 2.2e-16 to a shipped agent's longest run, which is 1.3e-9, so its limit would be at most 2.3e-9. A profile at the stiffest corners could then take its steps. No shipped or realistic profile is near those corners today, so nothing a learner can reach changes either way, and the item is not urgent.

**Done when.** The agent balance's limit is the one the owner chose, `docs/MODEL.md` and `core/rounding.py` state it and its reason, and a test shows that a correct one-second step at the stiffest envelope corners passes or halts as that choice says.

**Generator check.** An instance of the fact that `PL-GJ1W` (no one place states how far a computed value can be from the exact one) names: how far a computed value can be from the exact one, and so what a comparison on it proves. That head is still open, so this is not a re-entry. `PL-D88N` recorded this case in advance as the moment to choose, so its fix did not miss it.
