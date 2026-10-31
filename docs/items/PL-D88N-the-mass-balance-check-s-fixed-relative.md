---
id: PL-D88N
title: The mass-balance check's fixed relative tolerance of 1e-9 halts a stepped run at the numerical envelope's stiffest corners within seconds (4.3 s at a 0.01 L lung with blood:gas 1e4, measured 2026-10-25), because each step's propagator rounding there is about 1e-10 of the state; decide whether the tolerance should follow the propagator's stated error bound, 2**s times machine epsilon per step, or say why a fixed one is right
priority: P1
effort: M
status: ready
classes: defect, science
feature: floating-point-domain
touches: docs/MODEL.md, tests/unit/test_numerical_envelope_sweep.py
added: 2026-10-25
payoff: the agent-conservation check stays as strict as today on every run a learner can reach, and a stiffer patient profile fails a test the day it ships instead of halting runs for rounding
verify: grep -q 'def test_every_shipped_agent_steps_without_squarings' tests/unit/test_numerical_envelope_sweep.py && grep -qF 'PL-D88N' docs/MODEL.md
---

**Problem.** The mass-balance check's fixed relative tolerance of 1e-9 halts a stepped run at the numerical envelope's stiffest corners within seconds (4.3 s at a 0.01 L lung with blood:gas 1e4, measured 2026-10-25), because each step's propagator rounding there is about 1e-10 of the state; decide whether the tolerance should follow the propagator's stated error bound, 2**s times machine epsilon per step, or say why a fixed one is right

**Where it was found.** `PL-QX2G`'s blind review, pass 1, on 2026-10-25. That item gave every volume and partition coefficient a numerical envelope (`core/numerical_envelope.py`), chosen so that the 0.1 s step needs at most 19 squarings at every corner. The step's propagator is formed at every corner. But `AGENT_ACCOUNTING_RELATIVE_TOLERANCE` in `core/agent_simulation_validation.py` is one part in 1e9, and at 19 squarings each step rounds by about 1e-10 of the state. So the check halts the run with `AgentSimulationValidationError` after a few dozen steps. Reproduced with `AgentUptakeSystem.for_agent("sevoflurane")` at the widest flows, every tissue:blood coefficient at 1: alveolar gas 0.01 L with blood:gas 1e4 halted at 4.3 s, 0.01 L with blood:gas 100 at 499 s, and 1.0 L with blood:gas 1e4 at 934 s. Blood:gas 12 ran an hour without a halt in a 0.01 L lung. `docs/MODEL.md` § "The numerical envelope" records the table.

**Why it is not urgent.** The halt is an obvious refusal from `core/exceptions.py`, with the step rolled back, so no wrong value reaches a reader. No shipped or realistic parameter set is near those corners. It matters when a stiffer but real profile arrives, such as a small patient at its own flows, because the check would then blame the numerics for rounding that the propagator's own bound allows.

**What to decide.** Either derive the tolerance from the propagator's stated bound, about `2**s * 2**-52` per step times the steps in the accounting period, so that the check fires only on an error larger than the method allows; or keep the fixed tolerance and state in `docs/MODEL.md` that it narrows the envelope for a long stepped run, with the measurement. `PL-XST1`, the measurement of the validator's running totals, is the nearest related item.

**Re-measured after `PL-XST1`, 2026-10-26.** `PL-XST1` gave the validator's running totals compensated (Kahan) summation. The same seven configurations, rerun on a tree carrying it, halted at the same instants: 4.3 s, 934 s and 499 s, and the other four ran an hour without a halt. So the residual that trips the check is the propagator's rounding, not the summation's.

**Why it matters.** The mass-balance check is the guard that refuses a run
whose agent accounting no longer adds up. When it fires on rounding the method
itself allows, it blames the numerics for a correct run. The halt is the safe
failure, so no wrong value is shown. But a stiffer real profile, such as a
small patient, would halt within seconds for no reason a reader could act on.

**Done when.** `docs/MODEL.md` § "The numerical envelope" states that the
agent-accounting tolerance stays a fixed 1e-9, that it halts a long stepped
run at the stiff corners with the halt times measured above, and why a
tolerance summed from the propagator's bound was not adopted, citing
`PL-D88N`. A test in `tests/unit/test_numerical_envelope_sweep.py` steps every
shipped agent at every corner of the supported settings, at the step's ceiling
and its floor, and requires each propagator to need zero squarings. Its failure
message names this item as the place to choose a tolerance that widens only by
what the squarings add.

**Decision needed.** Whether the tolerance should follow the propagator's
bound or stay fixed. **Recommended: follow the bound.** The check should fire
only on an error larger than the method allows. At ordinary corners the step
needs few squarings, so a bound of about `2**s * 2**-52` per step stays far
tighter than 1e-9 there and the check loses no strength where runs actually
go. The cost is that the threshold then depends on the step's squaring count,
so it must be computed in one place, stated in `docs/MODEL.md`, and tested at
both a stiff and an ordinary corner. The choice is the owner's because it sets
the threshold of a safety check in `core/`.

**Generator check.** `PL-58D7`'s fact: the floating-point input domain on which
each operation in `core/` gives a correct answer. It was filed on 2026-10-25,
while `PL-58D7` was still open, by the blind review of `PL-QX2G`, one of that
head's splits. So it is not a re-entry (`PL-R4Y2`'s triage, 2026-10-31).

**Measured 2026-10-31, on `main` at `89d19f9f`.** Three findings.

1. **Every supported setting needs zero squarings.** Each shipped agent was
   stepped once at every combination of fresh gas 0, 0.5, 1, 4 and 10 L/min,
   alveolar ventilation 0, 1, 4 and 12 L/min, and cardiac output 0, 0.5, 2.5, 5
   and 10 L/min, at steps of 0.1 s, 0.01 s and 0.001 s. All 900 propagators took
   0 squarings, read from `_squarings_for` in `core/matrix_exponential.py`. Only
   the numerical envelope's stiff corners, such as a 0.01 L lung with a
   blood:gas coefficient of 1e4, take more (19 there).
2. **A correct run's residual stays far below 1e-9.** Over 24 h at the 0.1 s
   step, the worst relative residual was 3.08e-12 for sevoflurane at 2%,
   4 L/min fresh gas, 4 L/min ventilation and 5 L/min cardiac output, and
   5.27e-13 for desflurane at 18% with every flow at its maximum. The worst case
   in `docs/MODEL.md` § "Mass-balance identity", desflurane at 18% and the 1 ms
   step floor for 24 h, reached 3.73e-11 (`PL-XST1`, 2026-10-25).
3. **A tolerance derived from the propagator's bound would be loose.** The
   bound is about `3 * 2**s * 2**-52` per step, with the margin of 3 that
   `tests/unit/test_numerical_envelope_sweep.py` uses. The check compares the
   whole run's residual, so a rigorous tolerance sums that bound over every
   step. At s = 0 that gives 5.8e-10 for 24 h at 0.1 s, 5.8e-9 at 0.01 s and
   5.8e-8 at the 1 ms floor. The last is 58 times looser than 1e-9 and about
   1,500 times the residual measured on that run. So even `max(1e-9, bound)`
   would loosen the check by up to 58 times on a long fine-step run with a
   shipped agent. A real accounting error of a few parts in 1e8 would then
   pass. The 2026-10-31 recommendation above, to follow the bound, assumed the
   squaring count would decide this. It does not: the number of steps does.

**Decision needed, restated 2026-10-31.** Which tolerance the check uses.

- **A.** Follow the summed bound, or `max(1e-9, bound)`. This ends the false
  halts at the stiff corners. It also loosens the check by up to 58 times on
  long fine-step runs that learners can reach.
- **B.** Keep 1e-9 fixed. State in `docs/MODEL.md` § "The numerical envelope"
  that it halts a long stepped run at the stiff corners, with the halt times
  above. Add a test requiring every shipped agent, at every corner of the
  supported settings and at every supported step, to need zero squarings. A
  stiffer profile, such as a small patient, then fails that test when it
  ships, which is the moment to choose a tolerance that widens only by what the
  squarings add.
- **C.** Widen the tolerance only by what squarings add: about
  `3 * (2**s - 1) * 2**-52` per step, summed. This is exactly 1e-9 wherever
  s = 0, so it leaves every reachable run's check unchanged, and it ends the
  false halts at the stiff corners now.

**Recommended: B.** It keeps the check as strict as today on every run a
learner can reach. It costs a paragraph and one test, and the test names the
moment the question becomes real. C is the right shape for that moment.
Building it now adds a computed threshold to a safety check for a profile that
does not exist. The choice is the owner's because it sets the threshold of a
safety check in `core/`, and because an earlier reply proposed A.

**Answered 2026-10-31: B, keep 1e-9 fixed** (project owner, 2026-10-31,
ratified, over A, a tolerance summed from the propagator's bound, and C, a
tolerance widened only by what squarings add). The measurements above are the
case: every reachable run needs zero squarings and stays at least 27 times
below 1e-9, while A would loosen the check by up to 58 times on a long run at
the 1 ms floor. C stays the recorded shape for the day the new test first
fails.

