---
id: PL-2MD9
title: "The propagator's constant state row drifts and the squarings amplify it: 2.28e+222 at an alveolar volume of 1e-19 L, where governing_equations.UNIT_STATE promises no step can perturb it"
priority: P2
effort: M
status: ready
classes: defect, science, anticipated
feature: numerical-domain
touches: src/anesthesia_sim/core/matrix_exponential.py, src/anesthesia_sim/core/governing_equations.py, tests/unit/test_matrix_exponential.py, docs/MODEL.md
added: 2026-09-14
verify: uv run pytest tests/unit/test_matrix_exponential.py && grep -q 'def test_a_zero_row_propagates_to_its_exact_basis_row' tests/unit/test_matrix_exponential.py
---


**Problem.** `governing_equations.UNIT_STATE` is the constant 1 that turns
$`dy/dt = Ay + b`$ into $`dy/dt = Ay`$, and its docstring states the guarantee
this rests on: "Its row is empty, so it is constant by construction rather than
by convention, and no step can perturb the forcing term the other rows read
from it."

The guarantee is exact in the algebra and false in the implementation. If row
$`i`$ of $`A`$ is entirely zero then row $`i`$ of $`A^k`$ is zero for every
$`k \geq 1`$, so row $`i`$ of $`\exp(A\,\Delta t)`$ is row $`i`$ of the
identity, to the last bit. Measured 2026-09-14 on sevoflurane at the shipped
0.1 s step, driving `AlveolarCompartment.gas_volume_l` downward:

| `gas_volume_l` | `propagator[UNIT_STATE][UNIT_STATE]` |
| --- | --- |
| 2.5 L (shipped) | 1.0 |
| 1e-8 L | 0.9999999962747097 |
| 1e-12 L | 1.0000610370184777 |
| 1e-14 L | 0.9961013694411648 |
| 1e-16 L | 2.718281808182473 |
| 1e-18 L | 1.6038101267862054e-28 |
| **1e-19 L** | **2.2844048619719663e+222** |

**Mechanism, established rather than assumed.** The shift is what admits it.
`matrix_exponential` adds $`sI`$ to make the matrix entrywise nonnegative, which
puts $`s`$ on the constant row's diagonal where $`A`$ had 0; the series then
computes $`e^{s\Delta t/2^{j}}`$ there and the decay multiplies
$`e^{-s\Delta t/2^{j}}`$ back. That round trip is exact in the reals and lands
at $`1+\delta`$ in floating point. Each squaring squares it, so after $`j`$
squarings the row carries $`(1+\delta)^{2^{j}}`$. At 1e-19 L, $`j`$ is large
enough to turn a rounding error into 222 orders of magnitude.

**Why this is separate from `PL-3PRZ` rather than part of it.** That item
covered the same family — the propagator failing silently — and closed the two
cases whose remedy is a guard on the *result*: the zero matrix, and the norm
whose scaling overflowed. This one cannot be closed that way. The two invariant
forms tried and measured there both fail here:

- **Requiring the zero row to propagate to its exact unit basis row** is the
  correct statement, and refusing on it rejected 131 additional decades of
  alveolar volume including ordinary ones, because the round trip above is
  never bit-exact.
- **Requiring `propagator[i][i] >= exp(A[i][i] * dt)`**, the provable per-entry
  lower bound, is violated at ulp level by `matrix_exponential`'s own passing
  tests (`test_propagating_twice_matches_propagating_once`).

So the remedy is a change to the numerical method rather than a guard on its
output, which is why it is its own item. The obvious candidate is to restore
the zero rows of $`A`$ to their exact basis rows after the decay and before the
squarings, so there is no $`\delta`$ for the squarings to amplify. That is a
change to a safety-critical numerical path and wants its own verification
against the analytic solutions in `tests/unit/test_matrix_exponential.py`, not
a rider on a guard item.

**What is not at risk today.** No shipped path reaches these volumes: the
alveolar volume is a fixed model parameter, is not user-settable, and
`SimulationController` exposes no setter for it (`docs/MODEL.md` § "What is not
bounded this way"). The band is also covered downstream — the mass-balance
guard halts the run at 1e-9 L and below, which is every row of the table above
— so no drifted value reaches a display. What makes it worth an item is that
the coverage is incidental rather than designed: the accounting tolerance is
what happens to catch it, and `UNIT_STATE`'s docstring states a guarantee the
code does not keep.

**Found by** `PL-3PRZ`, while sweeping every decade from 1e0 to 1e-323 L to
establish that item's mechanism.

**Why it matters.** A stated invariant that the implementation does not keep is
worse than an unstated one, because the next session builds on it. `UNIT_STATE`'s
docstring says "no step can perturb the forcing term the other rows read from
it", and the forcing term is what makes the inhomogeneous system solvable in
closed form - so anything later resting on that guarantee, including the
canonical evaluation rule `docs/MODEL.md` now carries, is resting on something
measured to be false. The measurement above is also a warning about the method
rather than about one parameter: the amplification mechanism is
$`(1+\delta)^{2^{j}}`$ across the squarings, so it is the scaling-and-squaring
path that carries it, not the alveolar volume specifically.

**Why P2 and `anticipated` rather than P1.** The brief's own last paragraph is
the reason, and it is load-bearing: no shipped path reaches these volumes - the
alveolar volume is a fixed model parameter with no setter on
`SimulationController` - and the mass-balance guard halts the run at 1e-9 L and
below, which covers every row of the measured table, so no drifted value reaches
a display. `anticipated` is this project's own mechanism for holding a `science`
concern at its blocker's band rather than in the top one. **If alveolar volume
ever becomes settable, this re-bands to P1 immediately**, and that is the trigger
to watch rather than a date.

**Done when.** The propagator keeps the guarantee `UNIT_STATE` states: a zero row
of $`A`$ propagates to its exact unit basis row, bit for bit, at every alveolar
volume the shipped validators admit - the candidate being to restore the zero
rows after the decay and before the squarings, so there is no $`\delta`$ left to
square. `tests/unit/test_matrix_exponential.py` asserts it directly, the analytic
comparisons already in that file still pass, and `UNIT_STATE`'s docstring either
states a guarantee that now holds or says precisely where it stops.
