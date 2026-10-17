---
id: PL-CQ1M
title: BreathingCircuit.advance_fresh_gas, formed from the fraction it holds throughout (PL-YT8N), carries a washout residual only to an ulp of that fraction: at forty time constants it reports exactly 0 where the balance leaves 4e-18; the two-regime arrangement core/exponential_approach.py takes forms the result from the equilibrium beyond half a gap and keeps the residual, and the circuit could take the module (found reviewing PL-XWFP)
priority: P3
effort: S
status: ready
classes: refactor
feature: numerical-domain
touches: src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/exponential_approach.py, src/anesthesia_sim/core/__init__.py, docs/ARCHITECTURE.md, tests/unit/test_circuit.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-12
payoff: the first-order closed form is written once in core/, so the circuit stops carrying the arrangement the patient compartments' measurements retired
verify: grep -q 'def test_a_long_circuit_washout_keeps_its_residual' tests/unit/test_circuit.py
---

**Problem.** BreathingCircuit.advance_fresh_gas, formed from the fraction it holds throughout (PL-YT8N), carries a washout residual only to an ulp of that fraction: at forty time constants it reports exactly 0 where the balance leaves 4e-18; the two-regime arrangement core/exponential_approach.py takes forms the result from the equilibrium beyond half a gap and keeps the residual, and the circuit could take the module (found reviewing PL-XWFP)

**Reproduced 2026-10-17** on this tree (`b9b3c812`) against a 40-digit
`decimal` reference, washing a bare 6 L circuit at 4 L/min out from a
fraction of 1.0 under a dial of zero: at 20 and 30 time constants
`advance_fresh_gas` agrees with `exponential_approach` and the reference
(2.061e-09; 9.359e-14 against 9.358e-14); at 37.5 and 40 it reports exactly
`0.0` where the module and the reference give 5.176e-17 and 4.248e-18. From
0.05 the same lengths lose 2.6e-18 and 2.1e-19. A second of the module's four
properties is missing too, found in the same run: over 20,000 drawn starting
fractions below half an 8% dial, a 60-time-constant wash-in lands an ulp past
the dial in 484 and an ulp short in 514, where the module's
equilibrium-anchored form lands on it exactly. The other two hold (the result
stays between the two fractions, and is exact at zero flow).

**Why it matters, and how little.** No run reaches this closed form:
`advance_fresh_gas` is called only by `BreathingCircuit.advance`, the
`tests/reference/test_circuit_wash_in.py` analytic tests and unit tests, and a
run steps through `AgentUptakeSystem.advance()` (the method's own docstring
says so). The lost residual is below 1e-16 of the starting fraction, the
exhaust still closes the balance to rounding (6.0 L exhausted of 6.0 L held at
40 time constants), and an ulp past an 8% dial is no displayed value. So this
is not a numerical-fidelity defect a learner or a clinician could meet; it is
the circuit holding its own arrangement of the one closed form
`core/exponential_approach.py` was written to state once, with two of the
four properties that module's docstring says the arithmetic owes the physics.
The consequence is maintenance: a reader of `core/` meets the line twice, in
two arrangements, and the circuit's is the one the module's measurements
retired. `CLAUDE.md`'s one-source-of-truth principle is what makes it worth
doing at all, at `P3`.

**Done when.** `BreathingCircuit.advance_fresh_gas` forms its next fraction
with `exponential_approach` (initial and delivered fraction, step, and the
circuit's own time constant, or the step in time constants where forming
`tau` would overflow as `PL-B26Y` records), keeping its exhaust terms and their
no-negative-term argument; `core/exponential_approach.py`'s module docstring
and `docs/ARCHITECTURE.md`'s line for it name the circuit as a caller and say
why the fraction rather than an amount is anchored there; the
`core/__init__.py` paragraph on the circuit's closed form is brought into line;
and `test_a_long_circuit_washout_keeps_its_residual` in
`tests/unit/test_circuit.py` pins the 40-time-constant washout above against
the reference, beside an exact full wash-in onto the dial. The reference
wash-in tests and
`test_the_circuit_balance_closes_within_the_rounding_of_what_the_step_moves`
pass unchanged.
