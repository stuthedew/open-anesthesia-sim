---
id: PL-XWFP
title: TissueGroup.advance and VenousBloodCompartment.advance report uptake as a return - a negative change, as low as -3.2e-18 L, while the driving fraction is above the compartment's - at admitted flows from 1e-30 to 3e-13 L/min, because d + (i - d) * exp(-dt/tau) rounds at the scale of the driving fraction; the circuit's closed form was rewritten for the same reason (found fixing PL-YT8N)
priority: P1
effort: S
status: done
classes: science, defect
feature: numerical-domain
touches: src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/__init__.py, src/anesthesia_sim/core/exponential_approach.py, tests/unit/test_compartment_primitives.py, tests/unit/test_exponential_approach.py, docs/ARCHITECTURE.md
added: 2026-10-11
closed: 2026-10-12
pr: 1465
payoff: the tissue and venous closed forms never report agent leaving while the gradient drives it in, so a reference case checked against them cannot be misled by a sign the physics forbids
verify: grep -q 'def test_a_compartment_never_reports_uptake_as_a_return_at_an_admitted_flow' tests/unit/test_compartment_primitives.py
---

**Problem.** TissueGroup.advance and VenousBloodCompartment.advance report uptake as a return - a negative change, as low as -3.2e-18 L, while the driving fraction is above the compartment's - at admitted flows from 1e-30 to 3e-13 L/min, because d + (i - d) * exp(-dt/tau) rounds at the scale of the driving fraction; the circuit's closed form was rewritten for the same reason (found fixing PL-YT8N)

**Measured 2026-10-11, fixing `PL-YT8N`.** Flows from 1e-30 to 3 L/min at 1
and 3 times each decade, steps of 0.1, 1 and 60 s, and five states - driving
and compartment fractions of 1.0 and 1e-6, 0.02 and 0, 0.08 and 1e-9, 0 and
0.02, and 1e-6 and 1.0. A 6 L vessel-rich `TissueGroup` (tissue:gas 1.0)
returned a change of the sign opposite to its gradient in 100 of 930 cases
(900 as first filed; re-counted at close-out, 62 flows by 3 steps by 5 states),
and a 1.222 L `VenousBloodCompartment` (blood:gas 0.65) in 94, all at flows
from 1e-30 to 3e-13 L/min. The largest were -3.2e-18 L and -4.2e-19 L, at
1e-30 L/min over 0.1 s with a driving fraction of 0.08 against a compartment
at 1e-9.

**Why.** Both write the fraction as `d + (i - d) * exp(-dt/tau)`. Where
`dt/tau` is small that is `d + (i - d)` to within a rounding, and the
rounding is half an ulp of `d`, the driving fraction - 6.9e-18 at 0.08 -
rather than of the compartment's own `i`, so the stored fraction can land
below where it started while the flow is moving agent in.

**Reach.** Not a run's path: `AgentUptakeSystem.advance()` steps the
governing equations, and these are each compartment's closed form against a
held input, called by tests, notebooks and reference cases
(`core/__init__.py`). Uptake reported as a return is physically impossible
and looks like a number, the class `PL-YT8N` fixed in the circuit.

**What a fix has to decide.** `PL-YT8N` wrote the circuit's update as
`i + (d - i) * -expm1(-dt/tau)`, which rounds at the scale of the result and
cannot fall below `i` while `d` is above it. These two store an amount, not a
fraction, and return the stored amount's change, and the
`capacity_l * (amount / capacity_l)` round trip `core/__init__.py` describes
can move the amount by a rounding of its own. So measure first whether that
form alone holds the sign, or whether the change has to be formed from the
fraction difference, which would then disagree with the stored amount by a
rounding. Their zero-flow branches stay required either way.

**Why it matters.** A closed form reporting uptake as a return while the
driving fraction is above the compartment's is a number the physics forbids,
and these are the forms reference cases and notebooks call to check the stepped
model against, so a wrong sign there misleads verification rather than a run.
`PL-YT8N` fixed the same rounding in the circuit at `P1`.

**Done when.** Both report a change of their gradient's sign, or zero, at
every admitted flow, step and state, the walk above included, and a test in
`tests/unit/test_compartment_primitives.py` pins it beside
`test_the_circuit_exhaust_is_never_negative_at_an_admitted_flow`.


**Closed 2026-10-12, in `#1465`.** Both compartments advance their amount
through `core/exponential_approach.py`, one line in two forms: formed from the
amount held for a step closing up to half the gap, with `1 - exp(-dt/tau)`
taken by `expm1`, and from the equilibrium beyond it, so the change has the
gradient's sign and the amount stays between its start and its equilibrium
with nothing clamped, a full approach lands on the equilibrium exactly, a long
washout keeps its residual, and zero flow is exact with no branch - the two
zero-flow branches the brief kept are retired, which `core/__init__.py`
records. The form anchored at the amount throughout, clamped at the
equilibrium, was built first and reworked on review: it reported a washout of
forty time constants as exactly empty, with 2.5e-17 L remaining, and the clamp
bound what the two forms hold by construction. The review's two findings not
fixed here are `PL-FNH3` and `PL-CQ1M`.
