---
id: PL-D88N
title: The mass-balance check's fixed relative tolerance of 1e-9 halts a stepped run at the numerical envelope's stiffest corners within seconds (4.3 s at a 0.01 L lung with blood:gas 1e4, measured 2026-10-25), because each step's propagator rounding there is about 1e-10 of the state; decide whether the tolerance should follow the propagator's stated error bound, 2**s times machine epsilon per step, or say why a fixed one is right
status: untriaged
feature: floating-point-domain
added: 2026-10-25
---

**Problem.** The mass-balance check's fixed relative tolerance of 1e-9 halts a stepped run at the numerical envelope's stiffest corners within seconds (4.3 s at a 0.01 L lung with blood:gas 1e4, measured 2026-10-25), because each step's propagator rounding there is about 1e-10 of the state; decide whether the tolerance should follow the propagator's stated error bound, 2**s times machine epsilon per step, or say why a fixed one is right

**Where it was found.** `PL-QX2G`'s blind review, pass 1, on 2026-10-25. That item gave every volume and partition coefficient a numerical envelope (`core/numerical_envelope.py`), chosen so that the 0.1 s step needs at most 19 squarings at every corner. The step's propagator is formed at every corner. But `AGENT_ACCOUNTING_RELATIVE_TOLERANCE` in `core/agent_simulation_validation.py` is one part in 1e9, and at 19 squarings each step rounds by about 1e-10 of the state. So the check halts the run with `AgentSimulationValidationError` after a few dozen steps. Reproduced with `AgentUptakeSystem.for_agent("sevoflurane")` at the widest flows, every tissue:blood coefficient at 1: alveolar gas 0.01 L with blood:gas 1e4 halted at 4.3 s, 0.01 L with blood:gas 100 at 499 s, and 1.0 L with blood:gas 1e4 at 934 s. Blood:gas 12 ran an hour without a halt in a 0.01 L lung. `docs/MODEL.md` § "The numerical envelope" records the table.

**Why it is not urgent.** The halt is an obvious refusal from `core/exceptions.py`, with the step rolled back, so no wrong value reaches a reader. No shipped or realistic parameter set is near those corners. It matters when a stiffer but real profile arrives, such as a small patient at its own flows, because the check would then blame the numerics for rounding that the propagator's own bound allows.

**What to decide.** Either derive the tolerance from the propagator's stated bound, about `2**s * 2**-52` per step times the steps in the accounting period, so that the check fires only on an error larger than the method allows; or keep the fixed tolerance and state in `docs/MODEL.md` that it narrows the envelope for a long stepped run, with the measurement. `PL-XST1`, the measurement of the validator's running totals, is the nearest related item.
