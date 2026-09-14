---
id: PL-3PRZ
title: The agent-accounting guard catches an absurdly small alveolar volume at 1e-9 L but stops catching it by 1e-300 L, where the run returns a concentration of exactly zero with accounting passing
priority: P2
effort: M
status: done
classes: defect
feature: core-guard-coverage
touches: src/anesthesia_sim/core/matrix_exponential.py, tests/unit/test_matrix_exponential.py, tests/unit/test_agent_simulation_validation.py, docs/MODEL.md
added: 2026-09-06
closed: 2026-09-14
verify: uv run pytest tests/unit/test_matrix_exponential.py tests/unit/test_agent_simulation_validation.py && grep -q 'def test_refuses_the_zero_matrix_the_squarings_can_produce' tests/unit/test_matrix_exponential.py
---

**Problem.** Measured 2026-09-06 on sevoflurane at the shipped 0.1 s step,
driving `AlveolarCompartment.gas_volume_l` downward and advancing three steps:

| `gas_volume_l` | Outcome |
| --- | --- |
| 0.005 L (and 1e-6 L) | advances, accounting passes |
| 1e-9, 1e-12, 1e-15, 1e-30 L | `AgentSimulationValidationError` - the run halts |
| 1e-100 L | `SimulationNumericalError` - the step is rolled back |
| **1e-300 L** | **advances, returns a concentration of exactly 0, accounting passes** |

The last row is the defect. Every row above it fails obviously, which is the
required behavior; the bottom one succeeds quietly and hands back a number.

**Why it matters, and why it is small.** A concentration of zero from a lung
of 1e-300 L is a plausible-looking value produced where every intermediate
guard has been passed - `CLAUDE.md`'s "prefer an obvious failure to a
plausible-looking number" inverted, in the one regime the guard was expected
to cover most easily. Against that: no caller reaches 1e-300 L by mistake,
and `docs/MODEL.md` § "What is not bounded this way" now states in terms
that the accounting guard is a backstop rather than a declared bound, so
nothing in the documentation relies on it.

Worth understanding rather than worth fixing blind. The likely mechanism is
that the amounts involved underflow to exactly zero, so the residual the
accounting check forms is zero and passes - which would mean the check is
comparing a quantity that has itself been annihilated. If that is what
happens, the same shape could arise wherever an amount underflows, which is
the part that generalizes beyond an absurd volume.

**Where.** `src/anesthesia_sim/core/agent_simulation_validation.py`;
`src/anesthesia_sim/core/alveolar.py`.

**Done when.** The mechanism is established rather than assumed - whether the
amounts underflow to exactly zero, so the residual the accounting check forms
is itself annihilated and passes - and then either the guard refuses the
regime, or `docs/MODEL.md` records the bound below which the accounting check
stops being evidence, with the reason. A regression test at 1e-300 L pins
whichever it turns out to be.

**Found by** `PL-GYH2`, while checking a claim written into `docs/MODEL.md`
rather than asserting it.

**Classed `defect` rather than `science`, and it can be overruled.** No
interface path reaches an alveolar volume of 1e-300 L - the circuit and
alveolar volumes are not user-settable - so no clinician can be misled by this
today, and `docs/MODEL.md` § "What is not bounded this way" already states that
the accounting guard is a backstop rather than a declared bound. What would
change the class is the generalization the brief names: if an amount
underflowing to zero can annihilate the residual anywhere else, the guard is
weaker than the specification says it is.

**Done 2026-09-14. The mechanism is not the one this brief predicted, and the
guard named in the title was never at fault.** The prediction was that "the
amounts involved underflow to exactly zero, so the residual the accounting
check forms is zero and passes". What happens is one layer up: at 1e-300 L the
squarings drive the *propagator* to the zero matrix, `propagate()` returns the
zero state vector, and the accounting identity is then handed
$`0 + 0 - 0 - 0`$. Every term of the check was annihilated before the check
ran. Zero balances zero, and the check was right to say so.

So the fix is in `core/matrix_exponential.py`, not in
`agent_simulation_validation.py` or `alveolar.py`, and `touches` was corrected
to match. Two refusals were added, both exact statements rather than
tolerances:

- **A zero propagator is refused.** $`\exp(A\,\Delta t)`$ is nonsingular for
  every finite $`A`$ — its determinant is $`e^{\operatorname{tr}(A)\Delta t}`$
  — so the zero matrix is the exponential of nothing and can only be a
  floating-point artifact. `_require_finite` accepted it: the zero matrix is
  finite and entrywise nonnegative, so both properties the module states of
  its output held of a matrix that solved nothing.
- **A norm whose scaling to the series bound overflows is refused.** Found in
  the same sweep at 1e-309 L, where the row sum is finite (1.2e+307) and the
  division by $`2^{-4}`$ reaches `inf`; `ceil(log2(inf))` then raised a bare
  `OverflowError`, outside `core/exceptions.py` and outside this module's
  documented failures, so `advance()` neither restated it nor recognised it.

**Two stronger invariants were tried first and both were measured too strict**,
which is why the weakest sufficient one shipped:

- *Every diagonal entry strictly positive*, provable from the shift as
  $`\exp(A\Delta t)_{ii} \geq e^{-s\Delta t} > 0`$. It refuses
  `test_diagonal_matrix_matches_scalar_decay[3600.0]`, where `exp(-0.5 * 3600)`
  is a real number no double can hold and 0.0 is the correct entry.
- *`propagator[i][i] >= exp(A[i][i] * dt)`*, the provable per-entry bound. It
  is violated at ulp level by `test_propagating_twice_matches_propagating_once`.

**Measured across every decade from 1e0 to 1e-323 L, before and after.** 120
advance with the constant state row exact, and the same 120 advance now — no
volume that worked before is refused. 77 were already refused as non-finite;
194 are refused now; the 116 that silently returned a zero propagator plus the
one `OverflowError` account for the difference exactly. The table in this
brief is unchanged in every row but the last, which now halts.

**`PL-2MD9` carries what is left.** Between 1e-8 and 1e-19 L the propagator
stays finite and nonzero while the constant state row drifts to 2.28e+222,
against `governing_equations.UNIT_STATE`'s docstring guarantee that "no step
can perturb" it. Its remedy is a change to the numerical method rather than a
guard on the result — the two invariant forms above are exactly what fails to
catch it — so it is its own item rather than a rider here.

**On the class.** It stays `defect`. The generalization this brief named as
what would raise it — "if an amount underflowing to zero can annihilate the
residual anywhere else" — is real but sits in a different place than expected:
it is not amounts that underflow, it is the propagator that produces them, and
no shipped path reaches a volume that does it. The shape worth carrying
forward is the one this found: **a residual formed from quantities that a
single failure can reach together proves nothing when that failure occurs.**
