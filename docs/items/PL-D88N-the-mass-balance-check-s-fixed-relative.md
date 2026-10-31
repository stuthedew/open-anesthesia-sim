---
id: PL-D88N
title: The mass-balance check's fixed relative tolerance of 1e-9 halts a stepped run at the numerical envelope's stiffest corners within seconds (4.3 s at a 0.01 L lung with blood:gas 1e4, measured 2026-10-25), because each step's propagator rounding there is about 1e-10 of the state; decide whether the tolerance should follow the propagator's stated error bound, 2**s times machine epsilon per step, or say why a fixed one is right
priority: P1
effort: M
status: needs-decision
classes: defect, science
feature: floating-point-domain
touches: src/anesthesia_sim/core/agent_simulation_validation.py, docs/MODEL.md, tests/unit/test_agent_simulation_validation.py
added: 2026-10-25
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

**Done when.** Either the tolerance follows the propagator's stated error
bound, and a test shows the 4.3 s configuration above running an hour without
a halt while an injected accounting error of a few times that bound still
halts it; or `docs/MODEL.md` § "The numerical envelope" states that the fixed
tolerance narrows the envelope for a long stepped run, with the measured halt
times.

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
