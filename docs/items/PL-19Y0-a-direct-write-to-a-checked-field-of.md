---
id: PL-19Y0
title: A direct write to a checked field of BreathingCircuit, VenousBloodCompartment, TissueGroup, AlveolarCompartment or AgentSimulationValidator skips every check its constructor and setters make: a sevoflurane dial of Percent(50.0) past its 8% vaporizer maximum, a bare-float dial, a zero circuit volume, an inspired fraction of 1.5 and a venous agent amount past capacity are each accepted; only the three flows are guarded (PL-LBQY), and PL-544D covers the alveolar and tissue agent amount alone (found sweeping PL-ZGYX)
priority: P1
effort: M
status: done
classes: safety, defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/agent_simulation_validation.py, src/anesthesia_sim/core/validation.py, src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/core/uptake_system.py, docs/MODEL.md, docs/ARCHITECTURE.md, .claude/rules/core-domain.md, docs/items/PL-2TZT-five-more-guard-names-in-core-are-passed.md, tests/unit/test_circuit.py, tests/unit/test_blood.py, tests/unit/test_tissue.py, tests/unit/test_alveolar.py, tests/unit/test_agent_simulation_validation.py, tests/unit/test_state_capture.py, tests/unit/test_supported_range_edges.py, tests/unit/test_uptake_system_failure.py, tests/reference/test_late_washout_against_published_fits.py, tests/reference/test_published_wash_in_and_elimination.py
added: 2026-10-11
closed: 2026-10-17
pr: 1480
payoff: a test or notebook can no longer set a 50% sevoflurane dial, a zero circuit volume or an inverted flow range that the screen would then show as if the model had accepted it
verify: grep -q 'def test_a_direct_write_is_held_to_the_constructors_checks' tests/unit/test_circuit.py && grep -q 'def test_a_direct_write_is_held_to_the_constructors_checks' tests/unit/test_blood.py && grep -q 'def test_a_direct_write_is_held_to_the_constructors_checks' tests/unit/test_tissue.py && grep -q 'def test_a_direct_write_is_held_to_the_constructors_checks' tests/unit/test_alveolar.py && grep -q 'def test_a_direct_write_is_held_to_the_constructors_checks' tests/unit/test_agent_simulation_validation.py
---

**Problem.** A direct write to a checked field of BreathingCircuit, VenousBloodCompartment, TissueGroup, AlveolarCompartment or AgentSimulationValidator skips every check its constructor and setters make: a sevoflurane dial of Percent(50.0) past its 8% vaporizer maximum, a bare-float dial, a zero circuit volume, an inspired fraction of 1.5 and a venous agent amount past capacity are each accepted; only the three flows are guarded (PL-LBQY), and PL-544D covers the alveolar and tissue agent amount alone (found sweeping PL-ZGYX)

**Reproduced 2026-10-11** on `main` at `d9340516`, on
`s = AgentUptakeSystem.for_agent('sevoflurane')`: each of
`s.patient.venous_blood.agent_amount_l = capacity_l * 1.0000001` (its
`partial_pressure_fraction` then reads `1.0000001`),
`s.circuit.delivered_concentration_percent = 0.5` (held as a `float`),
`= Percent(50.0)` (against `max_delivered_concentration_percent` of 8.0),
`s.circuit.circuit_volume_l = 0.0`,
`s.circuit.inspired_partial_pressure_fraction = 1.5`,
`vessel_rich.perfusion_fraction = 7.0`, `vessel_rich.volume_l = -1.0` and
`s.alveoli.gas_volume_l = 0.0` was accepted without error. The scratch scan
behind the list read each non-frozen dataclass under `src/anesthesia_sim/`
for the fields its `__post_init__` checks and the names its `__setattr__`
guards: only `fresh_gas_flow_l_min`, `alveolar_ventilation_l_min` and
`cardiac_output_l_min` are guarded, and those by type alone.

**Why it matters.** The dial and the inspired fraction are read on screen, and
`PL-LBQY` recorded what the same hole cost the flow: the bare value reached a
snapshot and the readout before the next step's settings record refused it.
No supported setting takes any of these writes; the hole is a caller `mypy`
does not read - a test, a notebook, a value typed `Any`.

**Done when.** Each checked field of the five records refuses, at the write, a
value its constructor would refuse - by a `__setattr__` guard as `PL-LBQY`
added, or by making the record frozen and its setters `replace` - with a unit
test per record, and lands with or after `PL-544D`, which holds the same
mechanism for the alveolar and tissue agent amount.

**At `PL-544D`'s review, 2026-10-12** (the core-invariants pass over `#1428`),
three facts for the fix above. (1) A volume or coefficient guard has to compare
against the amount already held, as `set_circuit_volume` does
("circuit_volume_l is smaller than stored agent"): a volume written under the
held amount leaves the compartment over capacity with the amount's own guard
never consulted. Reproduced on a sevoflurane run at 8% for 300 s:
`alveoli.gas_volume_l = 1e-6` with 0.098 L held completes the next step and
propagates a fraction near 98,000 into every other compartment with the
accounting passing; `fat.volume_l` written to half the held amount's worth
has the step refused at fat, and `PL-544D` made `restore_state` write past
the capacity guard so that the rollback completes rather than replacing the
step's own error (`tests/unit/test_uptake_system_failure.py`). (2) A NaN,
zero, infinite or negative volume written onto a built compartment passes
every later amount, since `0.0 < nan` is false: the `0.0 <` leniency the
amount guard keeps for the constructor's write order is permanent once the
volume is bad. (3) The `require_a_number` on the capacity's factors inside
the amount guard is a stop-gap for that write order, and goes when the
volume's own guard runs first. An infinite capacity built from finite factors
(1e200 by 1e200) passes construction and admits any amount, before and after.

**Folded in from `PL-HJ7L` at the 2026-10-12 triage pass.** `BreathingCircuit
.deliverable_fresh_gas_flow_range` is one of the checked fields above.
Reassigned on a built circuit to `DeliverableFreshGasFlowRange(20.0, 30.0)`, it
leaves `accepted_fresh_gas_flow_range_l_min` at `(20.0, 10.0)` and the held
4.0 L/min outside the machine's range, where the same range at construction
raises `SimulationConfigurationError`, because
`_require_the_two_flow_claims_overlap` and `_require_deliverable_flow` run only
in `__post_init__`. Its guard re-checks both - the overlap, and the held flow
against the new range - as `set_circuit_volume` re-checks against the held
amount. Reproduced by `PL-HJ7L`'s review of `#1442`; nothing under `src/`
reassigns it.
