---
id: PL-2TZT
title: Five more guard names in core/ are passed unqualified by several classes, so most refusals still cannot say which object refused
priority: P2
effort: M
status: ready
classes: defect, ux
feature: core-guard-coverage
touches: src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/governing_equations.py, tests/unit/test_alveolar.py, tests/unit/test_blood.py, tests/unit/test_tissue.py, tests/unit/test_circuit.py, tests/unit/test_uptake_system_failure.py, tests/unit/test_governing_equations.py
added: 2026-09-22
payoff: a refusal a learner sees in the banner names the tissue or compartment that refused, not a parameter three objects hold
verify: ! grep -rqE 'require_[a-z_]+\("(agent_amount_l|blood_flow_l_min|volume_l|simulation_step_s|blood_gas_partition_coefficient|perfusion_fraction|tissue_gas_partition_coefficient|arterial_partial_pressure_fraction)"' src/anesthesia_sim/core/
---

**Problem.** Five more guard names in core/ are passed unqualified by several classes, so most refusals still cannot say which object refused

`PL-SPN6` fixed the one collision that had a test pinning it, and stated the
convention in `core/validation.py`'s module docstring: where several objects
can raise on the same parameter, the caller prefixes the owner. The rest of
`core/` does not follow it yet, and the count is larger than the one item
suggested.

**Names passed unqualified by more than one class**, each producing a refusal
that says only which parameter left its range:

| Name | Passed by | Instances that can raise it |
| --- | --- | --- |
| `agent_amount_l` | `AlveolarCompartment`, `VenousBloodCompartment`, `TissueGroup`, `BreathingCircuit` | 6 |
| `blood_flow_l_min` | `VenousBloodCompartment` (×2 sites), `TissueGroup` (×2 sites) | 4 |
| `volume_l` | `VenousBloodCompartment`, `TissueGroup` | 4 |
| `simulation_step_s` | `VenousBloodCompartment`, `TissueGroup`, `BreathingCircuit`, `AgentUptakeSystem` | 6 |
| `blood_gas_partition_coefficient` | `VenousBloodCompartment`, `TissueGroup`, `UptakeEquationSettings` | 5 |

**And every `TissueGroup` guard but the one `PL-SPN6` fixed is three-way
ambiguous across `vessel_rich`, `muscle` and `fat`** — including
`perfusion_fraction`, `tissue_gas_partition_coefficient` and `advance()`'s
`arterial_partial_pressure_fraction`. `governing_equations.py`'s
`TissueGroupEquationSettings` already qualifies its own three with
`f"{self.name} ..."`, so the twin class of the same object disagrees with it.

**Why it matters - it is not just tidiness - and why it is nevertheless not `PL-SPN6`.**
The reason is the same one: `app/dashboard_frame.py`'s `refused_setting_notice`
renders a `SimulationConfigurationError` verbatim into a banner, so the reader
of these messages has no traceback. `blood_flow_l_min` and
`blood_gas_partition_coefficient` are the ones a user can reach — a cardiac
output change redistributes tissue flows — so a refusal there names a
parameter three tissues hold. It was left out of `PL-SPN6` because that item's
brief, its `Done when` and its three test assertions are all about the
`partial_pressure_fraction` collision; widening it would have been scope the
owner did not agree to, and this is a decision about a convention rather than
a single message.

**Where.** `core/alveolar.py`, `core/blood.py`, `core/tissue.py`,
`core/circuit.py`, `core/uptake_system.py`, `core/governing_equations.py`, and
whichever tests pin the messages.

**Interacts with `PL-T137`** (each guard's message should carry the rejected
value, not just its name). That one edits `core/validation.py`'s message
templates; this one edits call sites, so they compose rather than collide —
but the combined message is worth thinking about once, not twice.

**Done when.** Every guard call site in `core/` that more than one object can
reach names its owner, on the convention `core/validation.py` states, and the
tests pin an owner rather than a bare parameter name.

**Reproduced 2026-09-22 (`PL-14QR`, triage).** `grep -rnE 'require_[a-z_]+\("(agent_amount_l|volume_l|blood_flow_l_min)"' src/anesthesia_sim/core/`
finds ten bare call sites across `alveolar.py`, `blood.py`, `circuit.py` and
`tissue.py`, as the table says. The `verify:` extends that pattern to all eight
names above, so it passes only when none is left bare.
