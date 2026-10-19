---
id: PL-2TZT
title: Five more guard names in core/ are passed unqualified by several classes, so most refusals still cannot say which object refused
priority: P2
effort: M
status: done
classes: defect, ux
feature: core-guard-coverage
touches: src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/governing_equations.py, tests/unit/test_alveolar.py, tests/unit/test_blood.py, tests/unit/test_tissue.py, tests/unit/test_circuit.py, tests/unit/test_uptake_system_failure.py, tests/unit/test_governing_equations.py, tests/unit/test_concentration.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-14QR's 2026-09-22 triage pass
added: 2026-09-22
closed: 2026-10-19
pr: 1676
payoff: a refusal a learner sees in the banner names the tissue or compartment that refused, not a parameter three objects hold
verify: ! grep -rqE --include='*.py' --exclude=simulation_step.py 'require_[a-z_]+\("(agent_amount_l|blood_flow_l_min|volume_l|simulation_step_s|blood_gas_partition_coefficient|perfusion_fraction|tissue_gas_partition_coefficient|arterial_partial_pressure_fraction)"' src/anesthesia_sim/core/ && grep -q '"^venous volume_l must be positive and finite$"' tests/unit/test_blood.py && grep -q '"^test volume_l must be positive and finite$"' tests/unit/test_tissue.py
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

**Since `PL-19Y0` (2026-10-17) the `verify:` above no longer proves Done
when.** `TissueGroup` and `VenousBloodCompartment` now check every field in
`__setattr__`, as `require_*(name, value)` with `name` the bare field name, so
their refusals still read `volume_l must be positive and finite` with no owner
while the literal pattern no longer matches them (nine of the seventeen sites
it matched on `main` at `b9b3c812`). Extend the check to those writes - a refused write on
a built `TissueGroup` naming the group, and on the venous pool naming it -
when this item is worked (found reviewing `PL-19Y0`).

**What `PL-79PK` left for this item (2026-10-17).** `PL-79PK` pins, as anchored
whole strings, every refusal a banner can show except the ones this item will
reword. It leaves alone each guard call that passes one of the five bare names
in the table above, and the `TissueGroup` and `VenousBloodCompartment`
`__setattr__` refusals that name a bare field. Pinning those now would freeze
a message that does not say which object refused. So when this item adds the
owner prefixes, it also pins each reworded message as an anchored whole
string, `match=r"^...$"`, in the tests it already touches.

**Checked 2026-10-19, and fixed on `claude/core-guard-defects-u39w8s`.** On
`main` at `6fd84bd5` the bare names were still there, now mostly as
`require_*(name, value)` in the `__setattr__` of `TissueGroup` and
`VenousBloodCompartment`. Each tissue group's writes and closed-form
arguments now name the group, as `"muscle volume_l"`, and the venous pool's
name the pool, as `"venous volume_l"`. The alveolar compartment's and the
circuit's agent amounts and the circuit's own step say `alveolar` and
`circuit`. Two bare names are left on purpose, because once the compartments
name theirs only one object can raise each: `simulation_step_s` in
`core/simulation_step.py` is the run's step, and `blood_gas_partition_coefficient`
in `UptakeEquationSettings` is the agent's. The `verify:` skips
`simulation_step.py` for that reason, reads only `.py` files (the old pattern
also matched the compiled `__pycache__` files), and greps a whole anchored
message from each of the two test files that pin the `__setattr__`
refusals, which the old pattern could not see. Each reworded message is
pinned as an anchored whole string, as `PL-79PK` asked.

**Owner ask, 2026-10-19:** #1676 carries this item with PL-8LQZ, PL-FNH3,
PL-XVCV, PL-HPKK, PL-5BD7, PL-5D1Z and PL-WP52, and is held for the owner's
review of one risk. A new or reworded refusal could fire on something a
learner does and halt a run that ran before. The full suite, the reference
trajectories included, passes unchanged. The 1 ms floor the compartments now
take is the floor the run already had, and the capacity refusals need a
factor near 1e200 or 1e-200. What is left to judge is whether the reworded
refusal messages read clearly to a learner.
