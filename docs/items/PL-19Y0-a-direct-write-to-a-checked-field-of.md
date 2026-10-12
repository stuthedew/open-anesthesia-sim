---
id: PL-19Y0
title: A direct write to a checked field of BreathingCircuit, VenousBloodCompartment, TissueGroup, AlveolarCompartment or AgentSimulationValidator skips every check its constructor and setters make: a sevoflurane dial of Percent(50.0) past its 8% vaporizer maximum, a bare-float dial, a zero circuit volume, an inspired fraction of 1.5 and a venous agent amount past capacity are each accepted; only the three flows are guarded (PL-LBQY), and PL-544D covers the alveolar and tissue agent amount alone (found sweeping PL-ZGYX)
status: untriaged
feature: parse-dont-validate
touches: src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/agent_simulation_validation.py, tests/unit/test_circuit.py, tests/unit/test_blood.py, tests/unit/test_tissue.py, tests/unit/test_alveolar.py, tests/unit/test_agent_simulation_validation.py
added: 2026-10-11
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
