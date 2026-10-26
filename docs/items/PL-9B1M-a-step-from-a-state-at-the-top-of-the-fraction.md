---
id: PL-9B1M
title: A step from a state at the top of the fraction range, every compartment at a partial pressure fraction of 1, rounds a fraction up to 3.5e-11 past 1 (1986 of 10 368 steps in the envelope sweep), so AgentUptakeSystem.advance rolls the step back with SimulationNumericalError; the display path at the stiffest corners draws fractions up to 1.000033 without refusing
status: untriaged
feature: floating-point-domain
touches: src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/concentration.py, tests/unit/test_numerical_envelope_sweep.py
added: 2026-10-26
---

**Problem.** A fraction in this model is a fraction of one atmosphere, and
`concentration.py` checks that each one lies from 0 through 1. A state at the
very top of that range, with every compartment at a fraction of 1, cannot be
stepped reliably. The matrix exponential's rounding can put one fraction
just past 1, from 1.0000000000000002 up to 1.0000000000349965. The check then
refuses it. `AgentUptakeSystem.advance`
turns that refusal into a `SimulationNumericalError` and rolls the step back.

**Measured, 2026-10-26.** `PL-58D7`'s envelope sweep steps the coupled system
once from a full state at each of the 96 envelope corners, the 27 flow corners,
the two step bounds and two splits of the cardiac output. That is 10 368
steps, and 1986 of them were refused. The largest refused fraction was
1.0000000000349965, about 1.6e5 units in the last place, which is still inside
one step's propagator bound at 19 squarings.
The fractions refused were the inspired, alveolar, venous and tissue ones. One
reproduction is a 0.01 L circuit, lung, venous pool and tissue, a blood:gas
coefficient of 1e-3, a tissue:blood coefficient of 1, a cardiac output of
10 L/min, no ventilation or fresh gas, and a 0.1 s step.

The display path (`RunDefinition.evaluate`) does not refuse. Washing out from
a full state at the stiffest corners, it returns fractions up to 1.000033
across 60 columns, which is inside the error bound that `matrix_exponential`
states for the propagators it chains. A chart would then plot a partial
pressure above one atmosphere.

**Why it is not urgent.** The refusal is the safe failure: no wrong value is
shown, and the step is rolled back. No shipped run reaches it. The shipped
vaporizers stop at 18% (desflurane), 8% (sevoflurane) and 5% (isoflurane), so
no compartment gets near a fraction of 1. It is reachable only through the
core interface, where a circuit's dial defaults to a ceiling of 100%.

**What to decide.** Two routes look sound, and silently clamping the result
back to 1 is not one of them, because the safety standard refuses a silent
coercion.

1. Lower the supported fraction ceiling to one an agent can physically reach,
   such as the highest saturated vapour pressure of a shipped agent as a
   fraction of one atmosphere. A state could then never sit within rounding of
   the check's upper edge.
2. Let the check accept a fraction within the propagator's stated error bound
   of 1, and say so in `docs/MODEL.md`. This keeps the range the type claims,
   but it widens a checked type by a tolerance.

The sweep in `tests/unit/test_numerical_envelope_sweep.py` accepts this
refusal by name and cites this item. It requires the refused fraction to lie
within one step's propagator bound of 1 and the state to be unchanged. Remove that acceptance when the item is
fixed.
