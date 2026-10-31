---
id: PL-QX2G
title: Give the gas, blood and tissue volumes and the partition coefficients a declared numerical envelope, refused at build as checked types: today each is only positive and finite, so a tissue volume of 1e-300 L with a tissue:blood coefficient of 1e-30 makes washin_rate_s raise a bare ZeroDivisionError, and a 1e307 L tissue with a 1e-307 tissue:gas coefficient has a 1 L capacity but an infinite time constant
priority: P1
effort: M
status: done
classes: defect, safety
feature: floating-point-domain
milestone: v0.6.9
touches: src/anesthesia_sim/core, src/anesthesia_sim/data, src/anesthesia_sim/app/controller.py, docs/MODEL.md, docs/ARCHITECTURE.md, tests/unit, tests/reference
added: 2026-10-25
closed: 2026-10-25
pr: 1833
payoff: a volume or partition coefficient outside the envelope on which core's arithmetic is shown correct is refused when it is built, so no product of them can reach inf, zero or a bare built-in error
verify: grep -rq 'def test_every_volume_and_partition_coefficient_is_refused_outside_its_numerical_envelope' tests/unit
---

**Problem.** Give the gas, blood and tissue volumes and the partition coefficients a declared numerical envelope, refused at build as checked types: today each is only positive and finite, so a tissue volume of 1e-300 L with a tissue:blood coefficient of 1e-30 makes washin_rate_s raise a bare ZeroDivisionError, and a 1e307 L tissue with a 1e-307 tissue:gas coefficient has a 1 L capacity but an infinite time constant

**Where it is.** `core/validation.py`'s `require_positive_finite` is the only check on the circuit, alveolar, venous and tissue volumes and on the blood:gas and tissue:gas partition coefficients. Two products have a further guard, `require_a_capacity` (`PL-8LQZ`, `PL-FNH3`): a venous or tissue volume times its own coefficient must be positive and finite. Nothing guards the other products and quotients built from the same inputs:

- `TissueGroup.tissue_blood_partition_coefficient`, the quotient of the tissue:gas and blood:gas coefficients, is not checked when either coefficient is written. A run refuses it only at its next step.
- `TissueGroupEquationSettings.washin_rate_s` divides by `volume_l * tissue_blood_partition_coefficient`. At a tissue volume of 1e-300 L and a tissue:blood coefficient of 1e-30 that product underflows to 0.0, and the property raises a bare `ZeroDivisionError` (reproduced 2026-10-25). `AgentUptakeSystem.advance` rolls the step back but restates only `SimulationConfigurationError`, so the built-in error leaves `core/exceptions.py`'s hierarchy.
- `TissueGroup.time_constant_s` evaluates `SECONDS_PER_MINUTE * self.volume_l * ...` left to right. At a volume of 1e307 L and a tissue:gas coefficient of 1e-307 the capacity is 1 L, an ordinary value, but the time constant is `inf`, so the tissue never moves (reproduced 2026-10-25). At a volume of 1e-300 L and a blood:gas coefficient of 1e30 it is 0.0, which `exponential_approach` divides by.
- `build_system_matrix` divides flows by each volume. A small alveolar volume or a large blood:gas coefficient is refused only when the propagator is computed (`PL-2MD9`, `PL-3PRZ`), so a settings record or a `RunDefinition` can hold settings that no step accepts.
- `AgentParameters`' three tissue:blood coefficients are the same unchecked quotient.

**What to do.** Give each of these inputs a declared numerical envelope, the way `MINIMUM_SIMULATION_STEP_S` already gives the step a floor. The envelope is not a supported range. A supported range says where the model represents a patient. The envelope says where the arithmetic has been shown to give the right answer, and it is set far outside any physiological value so that no real parameter set meets it. Build each input as a checked type, as `FreshGasFlow` is built, so that the check happens once at the type and every signature after it takes the type. That covers the compartments, `UptakeEquationSettings`, `TissueGroupEquationSettings` and the parameter-file payloads. Choose the bounds so that every product and quotient formed from them stays many decades inside the float range, and say in `docs/MODEL.md` § "Numerical method" how the bounds were measured. A candidate is a volume from 1e-3 L to 1e3 L and a partition coefficient from 1e-3 to 1e4. These are three decades below a neonate's alveolar volume and xenon's blood:gas coefficient of 0.115, and above any fat volume or methoxyflurane's fat:gas coefficient. The measurement decides the bounds, not this sentence.

`docs/MODEL.md` § "What is not bounded this way" says the two gas volumes carry no supported range, because neither is a control. That reasoning still applies. An envelope is a different claim about the same values, and the section should say so rather than be contradicted.

`PL-X8F6` asks for tests of the alveolar and venous volume refusals that exist today. Once those refusals become the envelope's checked types, its tests are this item's edge tests, so close it here.

**Why it matters.** At these inputs core raises an error from outside its own hierarchy, freezes a tissue that should move, or accepts settings it cannot step. The safety-critical standard asks for an obvious refusal at build instead. No shipped parameter file is near the bounds, so no learner sees a change.

**Done when.** Every volume and partition coefficient is a checked type with a declared envelope that is stated, with its measurement, in `docs/MODEL.md`; the parameter-file payloads and the equation settings take those types; and a test probes each envelope at both edges and one representable value past each.

**Generator check.** A member of the `floating-point-domain` feature, split from `PL-58D7`, the generator head.

**Session notes, 2026-10-25 (claimed on `claude/blissful-goodall-i6dw3h`; stopped for length before any code).** The session that claimed this item read the code and took one measurement, then reset at the spend budget. The next session starts from here.

*The shape planned.* One new module in `core/` holds the envelope, because the envelope is a numerical claim and `core/supported_ranges.py` holds physiological ones. It defines `MINIMUM_VOLUME_L`, `MAXIMUM_VOLUME_L`, `MINIMUM_PARTITION_COEFFICIENT` and `MAXIMUM_PARTITION_COEFFICIENT`. It also defines two checked types built as `FreshGasFlow` is built, a `float` and a `CheckedQuantity` (names to settle, for example `CompartmentVolume` and `PartitionCoefficient`). Each type has a stored-value check that refuses a bare `float` with `TypeError`, as `require_fresh_gas_flow` does. `docs/ARCHITECTURE.md` § "Where new code belongs" needs the new module, because `tools/doc_check.py` holds that map to the tree. The places that store a volume or a coefficient, and so call the stored-value check in place of `require_positive_finite`, are these:

- `BreathingCircuit.__setattr__` and `set_circuit_volume` (`circuit.py`).
- `AlveolarCompartment.__setattr__` for `gas_volume_l` (`alveolar.py`).
- `VenousBloodCompartment.__setattr__` (`blood.py`).
- `TissueGroup.__setattr__` (`tissue.py`).
- `TissueGroupEquationSettings.__post_init__` and `UptakeEquationSettings.__post_init__` (`governing_equations.py`).
- The parameter payloads in `parameters.py`, which build the types at load. `patient.py` and `uptake_system.py` then pass them through.

`app/controller.py` passes a circuit volume to `set_circuit_volume` and must build the type there. About 300 keyword uses in the tests build compartments from bare floats: `test_circuit.py` 38, `test_tissue.py` 36, `test_parameters.py` 21, `test_governing_equations.py` 20, `test_alveolar.py` 18, `test_blood.py` 13 and `test_controller.py` 13, with fewer in about twenty other files. That migration is mechanical, so a subagent can do it once the types exist in `src/`.

Once both factors are inside the envelope, their product lies between 1e-6 and 1e7 at the candidate bounds. So `require_a_capacity` in `core/validation.py` can never fire. Retire it, and rewrite its regression tests (`PL-8LQZ`, `PL-FNH3`) as tests that the envelope refuses those inputs. `require_room_for_the_agent_held` stays, because it checks a relation with the amount held.

*The measurement that changes the candidate bounds.* The products and quotients are not the binding limit. The propagator's squarings are. The script built `UptakeEquationSettings` at envelope corners, with every flow at its maximum and the tissue flows split 0.98, 0.01 and 0.01 of a 10 L/min cardiac output. It counted the squarings that `matrix_exponential` would perform:

| Corner | Fastest rate (1/s) | Squarings at 0.1 s | Squarings at 86 400 s |
| --- | --- | --- | --- |
| Candidate: volumes 1e-3 L, coefficients 1e-3 to 1e4, so tissue:blood 1e-7 | 1.6e9 | 32 | 52 |
| Same, with tissue:blood also held at 1e-3 or above | 1.7e6 | 22 | 42 |
| Volumes 1e-2 L, coefficients 1e-2 to 1e3, tissue:blood 1e-7 | 1.6e6 | 22 | 42 |
| Volumes 1e-2 L, coefficients 1e-2 to 1e3, tissue:blood 1e-2 or above | 1.7e4 | 15 | 35 |

`MAXIMUM_SQUARINGS` is 32. At 32 squarings the module's own error bound is 2^-20, about 1e-6, in every entry. A slow state such as the fat changes by about 7e-7 of itself per 0.1 s step. So at the candidate's stiffest corner, rounding is as large as the fat's whole change per step, and the error compounds over a run. The candidate bounds therefore do not meet this item's own claim, that the arithmetic has been shown to give the right answer inside the envelope. The stiff corner comes from the tissue:blood quotient: a tiny tissue:gas coefficient over a huge blood:gas one. No agent has a tissue:blood coefficient outside about 0.5 to 100.

*The shipped extremes, for the margins.* Volumes run from 1.222 L (venous pool) to 33 L (muscle), with the circuit at 6.0 L and the alveolar gas at 2.5 L. Blood:gas coefficients run from 0.42 to 1.30, and tissue:gas coefficients from 0.54 to 70.

*What the next session does first.* Measure the propagator's error against a high-precision evaluation at the corners. No `mpmath` or `scipy` is installed, so write a `decimal` scaling-and-squaring Taylor series in the scratchpad. Measure the mixed corners too: one input at its edge with the rest at shipped values. Then choose the bounds so that the 0.1 s propagator's error at every corner is far below the slowest shipped mode's change per step, and record the criterion with the numbers in `docs/MODEL.md` § "Numerical method". Bounding the tissue:blood quotient as well looks necessary. That bound is a relation between two fields, so `TissueGroup` and the agent payload check it. Alternatively, a third checked type can hold the quotient for `TissueGroupEquationSettings`. Every corner exceeds 32 squarings at the 24 h horizon. So read how `RunDefinition.state_at` composes its intervals (`run_definition.py` lines 961 and 1003) before claiming anything about long evaluations at the corners. A refusal there comes from `core/exceptions.py`, which `PL-58D7`'s planned corner sweep accepts.

**Outcome, 2026-10-25 (the session that resumed after the reset).** Built as the notes above planned, with the bounds the measurement chose.

*The bounds, and why they differ from the candidate.* Volumes are 0.01 to 10 000 L. Partition coefficients are 0.001 to 10 000, and the tissue:blood quotient is held to the same envelope. The candidate's volume floor of 0.001 L was refused by measurement. At its stiffest corner (alveolar gas 0.001 L, blood:gas 10 000, flows at their maximum) the 0.1 s step needed 22 squarings, its worst propagator entry was 1.7e-9 wrong against a 70-digit evaluation, and a wash-in stepped for 24 h drifted 4.9e-4. At 0.01 L the same corner needs 19 squarings, with a step error of 5.8e-11 and 2.5e-5 after 24 h. The criterion recorded in `docs/MODEL.md` § "The numerical envelope" is that no corner's 0.1 s step needs more squarings than the shipped sevoflurane system needs over the 24-hour horizon, which is 19. A sweep of all 2,560 corners (every flow at zero or its maximum, four cardiac-output splits) found 19 at worst. The volume ceiling was raised from 1e3 to 1e4 L because no squaring count depends on it. Choosing between these bounds is a numerical judgment with nothing a learner sees, so the session took it, as the notes above said it would.

*Decisions inside the agreed approach.*

- One module, `core/numerical_envelope.py`, holds `CompartmentVolume`, `PartitionCoefficient`, their stored-value checks `require_compartment_volume` and `require_coefficient`, and `tissue_blood_partition_coefficient`. That function is the one place the quotient is formed, so `TissueGroup` and `AgentParameters` cannot form it differently. The stored-value check is `require_coefficient` and not `require_partition_coefficient`, because `tools/core_vocabulary_check.py` requires an identifier containing `partition_coefficient` to name its two phases, and a generic guard names none.
- `require_a_capacity` is deleted. `require_a_capacity_with_room_for_the_agent` stays as the shared call that `blood.py` and `tissue.py` make, because `tools/duplicate_code_check.py` refused the two inline copies, but it now checks only room for the agent.
- The parameter payloads keep `PositiveFinite`. `parse_*` builds each value as its type, as it builds `Percent`, so the interval has one home. The three public records require the types in `__post_init__`.
- `SimulationController(circuit_volume_l=...)` and its snapshot field take `CompartmentVolume`.
- The 2026-09-06 measurements in `docs/MODEL.md` § "What is not bounded this way" (a 0.005 L alveolus, volumes down to 1e-323 L) are kept as history, with a paragraph saying the envelope now refuses them. The propagator's own refusals are still tested by building the matching matrix directly in `tests/unit/test_matrix_exponential.py`.

*Regression replay against the code before the fix* (`.claude/rules/test-oracles.md` rule 6). The new tests need the new types, so the variant run on `45277541` was the item's own reproduction, from a worktree with `PYTHONPATH` on its `src/`: `TissueGroupEquationSettings('fat', 1e-300, 1.0, 1e-30).washin_rate_s` raised `ZeroDivisionError: division by zero`, and `TissueGroup(name='fat', volume_l=1e307, perfusion_fraction=0.06, blood_gas_partition_coefficient=0.65, tissue_gas_partition_coefficient=1e-307)` had `capacity_l` 0.9999999999999999 and `time_constant_s(0.6)` `inf`. On this branch both inputs are refused when they are built (`tests/unit/test_numerical_envelope.py`).

`PL-X8F6` closes with this item. Its compartment-level refusal tests for the alveolar and venous volumes are in `tests/unit/test_alveolar.py` and `tests/unit/test_blood.py`.
