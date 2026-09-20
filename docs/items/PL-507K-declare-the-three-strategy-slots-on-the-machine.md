---
id: PL-507K
title: Declare the three strategy slots on the machine profile with one legal value each, validated against a registry in core
priority: P2
effort: S
status: ready
classes: feature
feature: machine-profile-framework
touches: src/anesthesia_sim/core, src/anesthesia_sim/data/machines/reference_circle_system.json, tests/unit/test_parameters.py, docs/machine-abstraction.md
added: 2026-09-20
payoff: no machine profile already written has to be reopened and edited when the second delivery or dial-mapping strategy lands
verify: grep -q 'def test_rejects_an_unknown_delivery_strategy' tests/unit/test_parameters.py && grep -q 'delivery.*fresh_gas_bypass' src/anesthesia_sim/data/machines/reference_circle_system.json
---

**Problem.** Declare the three strategy slots on the machine profile with one legal value each, validated against a registry in core

**Why it matters.** `docs/machine-abstraction.md:158-207` defines the closed
set of machine behaviors as three independent slots - delivery, removal and
dial mapping - each filled by a named strategy from a registry in `core/`, and
records that a profile "names one from each; it cannot supply one". Its
Question 4 already commits the loader to refusing a profile that "names a
strategy not in the registry" (`docs/machine-abstraction.md:391`). None of the
three fields exists on `_BreathingCircuitPayload`
(`src/anesthesia_sim/core/parameters.py:651-658`), so that refusal cannot fire
and a profile is silent about which physics it claims.

**What makes adding them later expensive, which is the whole case.** Every
payload model inherits `_StrictPayload`, (`core/parameters.py:390`), which sets
`model_config = ConfigDict(extra="forbid")` at `core/parameters.py:444` and is
stated in the module docstring at lines 12-15, so a profile may not carry a key
the schema has not declared - and a *required* key has no default,
so it cannot be added without editing every profile that exists at the time.
Today that is one file. The cost is therefore N file edits for N profiles,
paid at whatever N has reached, against one edit now.

**And they cost nothing in provenance.** `tools/doc_check.py`'s
`check_provenance` walks `_leaf_numbers` over each data file
(`tools/doc_check.py:925-933`), so it demands a `docs/MODEL.md` row for numbers
only. Three string fields add zero rows. Verified against the probe file used
for `PL-2FZ9` (load a machine profile by id): a two-number profile produced
exactly two provenance errors and nothing else.

**The honest limit, stated first because it is what this item is most likely to
be oversold on.** Declaring the slots makes the **data** future-proof, not the
code. `core/` still computes both rates inline - the delivery term
$`\dot V_F F_D`$ at `src/anesthesia_sim/core/governing_equations.py:355-360`
and the closed-form fresh-gas exchange at
`src/anesthesia_sim/core/circuit.py:433-448` - and nothing dispatches on a
strategy name. **The second member of any slot is still a code change of
exactly the same size as it is today.** This item does not make
`in_circle_injection`, `closed_circuit` or `fixed_volume_percent` cheaper to
implement; it makes them cheaper to *admit*. An item claiming otherwise would
be worse than no item.

What three inert fields do buy, precisely:

1. **No JSON is ever retrofitted.** The `extra="forbid"` argument above.
2. **The registry and its validator exist**, so the day a second member lands
   it is a registry entry plus a rate function - a code change - rather than a
   schema event that also touches every shipped profile and its tests.
3. **A profile becomes self-describing for attribution.** What
   `reference_circle_system.json` claims about its own physics is currently
   inferable only by reading `core/`; `PL-WZVZ` (make an inter-machine
   difference attributable to a named parameter) needs it stated in the file.

**Why this is worth doing on speculation at all.** It is not speculation: the
second member is already on the roadmap. Planned-milestone item 4, "Add direct
agent injection into the circuit, bypassing the vaporizer and its interlocks"
(`ROADMAP.md:5761-5762`), is the `in_circle_injection` delivery strategy
`docs/machine-abstraction.md:166` names, and the Zeus IE is the surveyed
machine behind it. A second dial mapping (`fixed_volume_percent`, the Tec 6) is
likewise named and has `PL-439V` behind it. The slots are three inert fields
against a landing that is likely rather than hypothetical.

**On the abstraction's own admission rule.** `docs/machine-abstraction.md`
admits a field only where something consumes it, and these three are not read
by the model. The consumer is the validator - the refusal at Question 4 rule 3
- plus attribution. That is a narrower consumer than the other fields have and
the brief says so rather than blurring it; it is also the consumer the design
document itself specified for these three.

**Done when.**

- `_BreathingCircuitPayload` declares `delivery`, `removal` and `dial_mapping`
  as required non-empty strings.
- A frozen registry in `core/` holds the legal values - `fresh_gas_bypass`,
  `fresh_gas_displacement`, `variable_bypass` - one per slot, with the
  not-yet-implemented members of `docs/machine-abstraction.md`'s tables
  deliberately absent rather than declared and unreachable.
- A payload validator refuses any other value, with a message naming the slot
  and its legal set, raised as a `SimulationConfigurationError` at the module
  boundary like every other parse failure here.
- `src/anesthesia_sim/data/machines/reference_circle_system.json` declares all
  three, with the sentence in its `provenance_gap` or a source note saying that
  the three names are a statement about which model path runs and not a
  measured property of any apparatus.
- `tests/unit/test_parameters.py` holds
  `test_rejects_an_unknown_delivery_strategy`.

**Explicitly not in scope.** No second strategy member - no
`in_circle_injection`, `closed_circuit` or `fixed_volume_percent`
implementation, and no dispatch in `core/`. No extraction of the two rates from
`governing_equations.py` or `circuit.py`. None of the other fields in
`docs/machine-abstraction.md`'s field table (`:285-296`) - `not_modelled`,
`agents`, `agent_limits`, `sample_gas_flow_l_min`, `sample_gas_configuration`,
`minimum_total_flow_l_min`, `minimum_oxygen_flow_l_min`: each is its own
admission decision, and `agent_limits` in particular is `PL-JQY1`'s.

**What would falsify this.** That the set is closed. If a machine turns up
needing a fourth slot, or a strategy that is a parameterized family rather than
a name - a delivery mode with its own numeric argument, say - then a bare
string enum is the wrong shape and the fields get retrofitted anyway, which is
the cost this item claims to avoid. The evidence it is closed is
`docs/machine-abstraction.md`'s derivation of the three slots from the eight
machines `docs/machine-survey.md` surveyed; a ninth machine outside them
falsifies it. It is also falsified if planned-milestone item 4 leaves the
roadmap, since the likely-second-member argument goes with it and three inert
fields become speculation.
