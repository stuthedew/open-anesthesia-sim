---
id: PL-9B1M
title: A step from a state at the top of the fraction range, every compartment at a partial pressure fraction of 1, rounds a fraction up to 3.5e-11 past 1 (1986 of 10 368 steps in the envelope sweep), so AgentUptakeSystem.advance rolls the step back with SimulationNumericalError; the display path at the stiffest corners draws fractions up to 1.000033 without refusing
priority: P1
effort: M
status: needs-decision
classes: defect, safety
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

**Why it matters.** A fraction of one atmosphere is a partial pressure, and no
compartment can hold more than one atmosphere of agent. On the display path a
chart can draw a fraction up to 1.000033, which is a physically impossible
value presented as a model output. On the stepped path the same rounding halts
a run that did nothing wrong. Neither is reachable with a shipped vaporizer,
but both are reachable through the core interface, whose dial ceiling is
100%.

**Done when.** A step from any state the supported ranges admit either
returns fractions from 0 through 1 or refuses with the reason, on both the
stepped path and the display path. The sweep in
`tests/unit/test_numerical_envelope_sweep.py` no longer accepts this refusal by
name, and `docs/MODEL.md` states the route taken.

**Decision needed.** Which of the two routes above. **Recommended: route 1.**
Cap the inputs (the dial's ceiling and the opening state) at a fraction an
agent can physically reach, and keep the check on computed fractions at 1.
Because the model conserves mass, no computed fraction can exceed the highest
input fraction by more than rounding, so a computed fraction can then never
come within rounding of 1. This narrows what the type admits as an input rather
than widening a checked type by a tolerance, which is the "parse, don't
validate" principle in `.claude/rules/expert-review.md`. The display path must
apply the same check, since today it draws 1.000033 without refusing. Route 2
keeps the full 0 to 1 input range, but it makes "a fraction" mean "a fraction
or a value slightly above 1" everywhere the type is read. The choice is the
owner's because it changes the range a checked clinical quantity admits, which
the safety-critical standard reaches.

**Generator check.** `PL-58D7`'s fact: the floating-point input domain on which
each operation in `core/` gives a correct answer. `PL-58D7`'s envelope sweep
filed it on the day that head closed, 2026-10-26, and its `generator:` line
names it, so it is that head's own finding and not a re-entry (`PL-R4Y2`'s
triage, 2026-10-31).
