---
id: PL-QX2G
title: Give the gas, blood and tissue volumes and the partition coefficients a declared numerical envelope, refused at build as checked types: today each is only positive and finite, so a tissue volume of 1e-300 L with a tissue:blood coefficient of 1e-30 makes washin_rate_s raise a bare ZeroDivisionError, and a 1e307 L tissue with a 1e-307 tissue:gas coefficient has a 1 L capacity but an infinite time constant
priority: P1
effort: M
status: ready
classes: defect, safety
feature: floating-point-domain
touches: src/anesthesia_sim/core, src/anesthesia_sim/data, docs/MODEL.md, tests/unit
added: 2026-10-25
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
