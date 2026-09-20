---
id: PL-8PS6
title: Fresh gas flow range is a machine property held in supported_ranges.py, not a global constant
priority: P1
effort: M
status: ready
classes: safety, anticipated, refactor
feature: anesthesia-machine
touches: src/anesthesia_sim/core/supported_ranges.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/data/machines, tests/unit, docs/MODEL.md
added: 2026-09-06
payoff: stops a second machine's flowmeter silently widening the range the compartment model's error bound was actually measured over, by giving the model envelope and the machine's deliverable range separate names, sources and refusal messages
verify: grep -q 'def test_machine_deliverable_flow_range_is_separate_from_model_envelope' tests/unit/test_supported_ranges.py
---

**Problem.** `MINIMUM_FRESH_GAS_FLOW_L_MIN = 0.0` and
`MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10.0` sit in
`src/anesthesia_sim/core/supported_ranges.py` as global constants, and
`require_supported_fresh_gas_flow` enforces them for every simulation. But the
deliverable fresh gas flow range is a property of the anesthesia machine — its
flowmeters, its minimum-flow floor, whether it supports minimal- or
closed-circuit flow — and it differs between machines. It belongs on an
anesthesia-machine profile, not in a module of model-wide constants.

**Why it matters.** Two separate constraints currently coincide in one number,
and conflating them is the safety hazard rather than the tidiness problem:

1. **The model's validated envelope** — the range over which the compartment
   model's error bound was measured, which is what the module docstring and
   the refusal message actually claim ("the domain this compartment model is
   claimed to represent a patient over", `docs/MODEL.md` § "Supported input
   ranges"). That is a model property and stays where it is.
2. **The machine's deliverable range** — what a given machine can physically
   set. That is the machine property this item is about.

The effective limit on a control is the **intersection** of the two, and each
side needs its own name, its own source and its own refusal message. If they
stay merged, adding a machine profile whose flowmeter goes higher silently
widens the model's claimed validity envelope — a plausible-looking number
produced outside the domain anything was measured over, which is exactly what
`CLAUDE.md`'s safety-critical standard forbids. Conversely a machine with a
higher floor than 0.0 (no true off position on the common gas outlet) would,
under a single constant, either be unrepresentable or would move the model's
floor for every machine.

**Where.** Named by symbol rather than by line, per
`.claude/rules/citation-drift.md`; the line numbers this block carried until
2026-09-20 had all drifted.

- `core/supported_ranges.py`'s `MINIMUM_FRESH_GAS_FLOW_L_MIN` and
  `MAXIMUM_FRESH_GAS_FLOW_L_MIN` — the two constants.
- `core/supported_ranges.py`'s `require_supported_fresh_gas_flow`, whose message
  cites `docs/MODEL.md` § "Supported input ranges" as the authority for the
  interval.
- `core/circuit.py`'s `BreathingCircuit.__post_init__` and
  `BreathingCircuit.set_fresh_gas_flow` — the two call sites.
- `core/circuit.py`'s `BreathingCircuit.fresh_gas_flow_l_min` field default of
  `4.0`, which is a **teaching default** on the same footing — relabelled by
  `PL-NM7X` on 2026-09-20, which withdrew the unsourced claim that it was "a
  routine mid-range clinical fresh gas flow".
- `docs/MODEL.md` § "Supported input ranges" — the prose that would have to
  separate the two claims.

The precedent for the split already exists in the same file: the vaporizer's
calibrated maximum is agent-specific and therefore lives on `BreathingCircuit`
as instance state rather than as a constant there. The fresh gas flow range is
the same shape with the machine, rather than the agent, as the carrier.

**Related.** `PL-FG9D` (design the base anesthesia-machine abstraction so a real
commercial machine is a data-plus-plugin addition) is where the carrier gets
designed; this item is a concrete property that abstraction has to hold.
`PL-4DCG` (survey the anesthesia machines in current clinical use for the
variables that change a simulated result) is where the per-machine numbers come
from. `PL-WZVZ` (make an inter-machine difference attributable) is the display
half. `PL-4YY1` (record provenance for the circuit volume and default fresh gas
flow) covers the 4.0 L/min default.

**Blocked on `PL-FG9D`, and classed `anticipated` for the same reason.** There
is one implicit machine today, and over it the constants are the model's own
envelope and are enforced correctly - so nothing displayed is wrong yet, and
the `safety` class describes the hazard the second machine introduces rather
than a live one. `docket check` seats such an item at its blocker's band
(`checks.py`, the `anticipated` exemption), which is why this sits at P2 behind
`PL-FG9D` instead of in the top band. The split cannot be made earlier than the
carrier: naming the machine's range is only meaningful once there is a machine
profile to name it on.

**Done when.** The machine's deliverable fresh gas flow range is read from a
validated, versioned machine profile with its own primary source (an
operator's manual or manufacturer specification, not a reference
implementation), the model's
validated envelope stays separately named in `supported_ranges.py`, a setting
outside either is refused with a message that says which of the two it
violated, and `docs/MODEL.md` distinguishes the two claims.

## Promoted, 2026-09-20 (`PL-8G48`), and what the tree now supplies

`PL-FG9D` closed as `#748` and `PL-4DCG` as `#742`, so the paragraph above is
answered: **the carrier exists.**
`src/anesthesia_sim/data/machines/reference_circle_system.json` is a validated,
versioned machine profile (`schema_version: 2`) already holding
`circuit_volume_l` and `default_fresh_gas_flow_l_min`, and
`docs/machine-abstraction.md` § "The fields the survey's evidence admits" slots
the three this item wants by name, each pointing at survey section (b8):
`deliverable_flow_range_l_min` ("the flow bound, with the model envelope"),
`minimum_total_flow_l_min` and `minimum_oxygen_flow_l_min` ("refusals below the
floor"). The same document states the other half outright - "**The model keeps
its envelope.** `core/supported_ranges.py`'s bounds are the model's" - so the
split this item asks for is specified rather than still to be argued.

**Verified against the tree on promotion**, so the fault is recorded as present
rather than merely the fix as absent: `MINIMUM_FRESH_GAS_FLOW_L_MIN = 0.0` and
`MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10.0` are still module-level constants in
`core/supported_ranges.py`, and the machine profile's keys are exactly
`schema_version, id, display_name, circuit_volume_l,
default_fresh_gas_flow_l_min, sources, provenance_gap` - no flow-range field of
any kind. The slot is specified and empty.

**It does not wait for a second machine.** The split is meaningful over one
profile: with the machine range absent the effective limit is the model envelope
alone, which is today's behavior, and what the work buys is that adding the
second machine cannot silently widen the envelope. That is the whole hazard.

### The `Done when.` above overstates what is reachable, and this is the correction

It requires the machine range to carry "its own primary source (an operator's
manual or manufacturer specification, not a reference implementation)". **No
such source exists for any machine**, and that is a finding of `PL-4DCG`'s
survey rather than a gap in the search: `docs/machine-survey.md` § "(b8) Flow
bounds, minimum oxygen flow, and the hypoxic guard" reports "**unknown for every
machine**" - no minimum oxygen flow, minimum total flow or deliverable range was
reachable for any of the eight surveyed - and names ISO 80601-2-13:2022 as the
governing standard while stating plainly that its text was not reachable and
that no claim about its requirements is made.

So the item ships the **structure with the value recorded as unknown**, which is
what the abstraction already provides for and what `PL-WZVZ` independently
requires of per-machine values ("an unknown value shows as unknown rather than
blank"). Read the `Done when.` above with that clause replaced by: *the machine's
deliverable range is a field on the profile whose value is `null`/unknown for
`reference_circle_system`, with survey section (b8) cited as the authority for
the unknown rather than for a number.* Everything else in it stands unchanged -
the separately named envelope, the refusal message saying which of the two claims
a setting violated, and `docs/MODEL.md` distinguishing them.

Disposition of one item's `Done when.` wording, taken in-session under rule 14
of `.claude/rules/instruction-writing.md`; it narrows no safety property, since
the split is the property and the absent number is the status quo.

### The band moves to P1, which is the promotion rather than a re-rating

`check_gate_reentries` exempts a `safety` item from the P1 floor only while
`anticipated` **and** `status: blocked` hold together, so leaving `blocked` is
the event that returns this finding to the debt gate. That is the settled
behavior rather than a side effect - `PL-ZF2G` installed it and `PL-JFQ3`
applied it - and the brief above already says "the band is owed again the moment
the item is unblocked". The hazard is still not live (one machine), which is why
`anticipated` stays on the item; what has changed is that the work is startable.
