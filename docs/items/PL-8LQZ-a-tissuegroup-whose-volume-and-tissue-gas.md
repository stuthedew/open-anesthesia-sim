---
id: PL-8LQZ
title: A TissueGroup whose volume and tissue:gas coefficient multiply to a capacity that underflows to 0.0 (1e-200 x 1e-200) passes construction and require_room_for_the_agent_held, and partial_pressure_fraction then raises ZeroDivisionError rather than a refusal: the mirror of PL-FNH3's capacity overflowing to inf (found reviewing PL-19Y0)
priority: P2
effort: S
status: ready
classes: defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/blood.py, tests/unit/test_tissue.py, tests/unit/test_blood.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-17
payoff: a compartment whose capacity underflows to zero is refused at build by name, instead of failing later with a bare division error the halt path does not handle
verify: grep -q 'def test_a_capacity_that_underflows_to_zero_is_refused' tests/unit/test_tissue.py
reenters: PL-ZGYX
---

**Problem.** A TissueGroup whose volume and tissue:gas coefficient multiply to a capacity that underflows to 0.0 (1e-200 x 1e-200) passes construction and require_room_for_the_agent_held, and partial_pressure_fraction then raises ZeroDivisionError rather than a refusal: the mirror of PL-FNH3's capacity overflowing to inf (found reviewing PL-19Y0)

**Reproduced 2026-10-17.** `TissueGroup(name='x', volume_l=1e-200,
perfusion_fraction=0.1, blood_gas_partition_coefficient=1.0,
tissue_gas_partition_coefficient=1e-200)` builds with `capacity_l == 0.0`, and
`partial_pressure_fraction` then raises `ZeroDivisionError: division by zero`.

**Why it matters.** The core's contract is that an invalid record is refused at
build, by name, with a `SimulationConfigurationError`. A `ZeroDivisionError` at
the first read is an obvious failure rather than a wrong number, but it names
nothing, and it escapes the handlers that turn a refusal into a halt. No shipped
data reaches it.

**Done when.** A tissue group, and the venous pool if it shares the defect, whose
capacity is not a positive finite number is refused at build with a message
naming both factors. A test pins the refusal. `PL-FNH3` is the overflow half and
can be done in the same change.

**Generator check.** An instance of `PL-ZGYX`'s fact, filed after that head
closed on 2026-10-11.
