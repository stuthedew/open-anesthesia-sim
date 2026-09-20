---
id: PL-QW19
title: default_fresh_gas_flow_l_min is a required field no manufacturer publishes, so the first real machine profile must invent an unsourced number or cannot be written
priority: P2
effort: S
status: ready
classes: defect, anticipated
feature: machine-profile-framework
touches: src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/uptake_system.py, tests/unit/test_circuit.py, tests/unit/test_parameters.py, docs/machine-abstraction.md, docs/MODEL.md
added: 2026-09-20
payoff: stops the first real machine profile being unaddable, or being added only by inventing a startup fresh gas flow no manufacturer publishes and writing a provenance row that cites nothing
verify: grep -q 'def test_a_profile_omitting_the_default_fresh_gas_flow_falls_back' tests/unit/test_circuit.py
---

**Problem.** default_fresh_gas_flow_l_min is a required field no manufacturer publishes, so the first real machine profile must invent an unsourced number or cannot be written

**Why it matters.** The tree and the design document disagree about whether an
opening fresh gas flow is a machine specification, and the disagreement blocks
the first real machine profile rather than merely looking untidy.

`_BreathingCircuitPayload` in `src/anesthesia_sim/core/parameters.py` declares
`default_fresh_gas_flow_l_min: PositiveFinite` with no default, under an
`extra="forbid"` strict payload — so every profile in `data/machines/` must
supply a positive number. `docs/machine-survey.md` § "(a2) Default fresh gas
flow" records the search and its result in as many words: *"No reachable source
states a startup fresh gas flow for any surveyed machine."* The shipped 4.0 is
labelled in `reference_circle_system.json`'s `provenance_gap` as a **teaching
default, not a clinical recommendation**, with no published counterpart —
the project owner's own ratified decision of 2026-09-20.

That is already awkward. What makes it blocking is
`tools/doc_check.py`'s `check_provenance`, which walks every leaf number in
`data/**/*.json` and errors where `docs/MODEL.md` holds no provenance row for
it. So a second profile must carry a row for a number nobody published. Under
`docs/machine-abstraction.md` § "Question 4"'s own admission rule — a profile
carrying `unknown` in a field the model reads is refused, because a machine with
an unknown required field cannot be added — the author's three options are:
fabricate a flow and write a provenance row that cites nothing; copy the
reference file's 4.0 and thereby assert a Dräger startup convention that does
not exist; or not add the machine. Each is worse than the last. This is the
concrete instance of the owner's "makes our life miserable" objection.

**The design already decided it the other way, and the tree has not caught up.**
`docs/machine-abstraction.md` § "Three homes, and why the shipped constants
move" puts this field under **"The run owns its opening conditions"**, not under
"The machine owns what a machine specifies", and gives the reasoning: `PL-8DJ7`
established only which side of the patient/agent split a flow falls on, and the
survey supplies the fact that settles the home — no reachable source states a
startup flow, so a per-machine field "would either block every machine or force
each one to fabricate a number. It is an opening condition of a run: a teaching
choice, which is exactly what the shipped file's own `provenance_gap` already
calls it."

The same section notes the precedent that makes the cheap fix legitimate rather
than a shortcut: `deliverable_fresh_gas_flow_range` (`PL-8PS6`) is **optional,
defaulting to `None`**, and the design records that Question 4's refusal of an
`unknown` "applies to the required fields a real machine profile must supply and
not to this one". Making the flow optional moves it into that same category by
the design's own logic.

**Resolve the disagreement in the design's favour, at the cheap end.** Concretely:

1. `_BreathingCircuitPayload.default_fresh_gas_flow_l_min` becomes
   `PositiveFinite | None = None`, and `BreathingCircuitParameters` carries
   `float | None` with a comment saying, as its neighbour already does for the
   deliverable range, that `None` reads as *this profile states no startup
   flow* and never as *this machine has none*.
2. `AgentUptakeSystem.for_agent()` passes the profile's value where present and
   falls through to the documented fallback where absent. The fallback already
   exists and is already pinned: `BreathingCircuit`'s field default
   `fresh_gas_flow_l_min: float = 4.0` in `src/anesthesia_sim/core/circuit.py`,
   guarded by `test_the_bare_circuit_defaults_match_the_shipped_machine_file` in
   `tests/unit/test_circuit.py`, which asserts the literal equals the shipped
   file's value. That guard needs re-pointing once the file's value may be
   absent, and the docstring on it — which currently says the default is reached
   only by "a bare unit-test construction" — stops being true and must be
   rewritten to say what the fallback now means.
3. `docs/machine-abstraction.md` records that the field is now optional, the way
   it recorded the same outcome for `deliverable_fresh_gas_flow_range`; and
   `docs/MODEL.md`'s provenance material says the fallback's authority is the
   teaching-default rationale in the reference file rather than any source.

`reference_circle_system.json` keeps its 4.0 and its provenance row unchanged,
so no stored value moves, no provenance row is orphaned, and nothing displayed
changes for the shipped run.

**Explicitly not a run-opening-conditions object.** The design's "The run owns
its opening conditions" also names the opening dial position and the patient
circuit volume, and building the object that owns all three is the expensive
version of this item. It is not needed here and is not started here: the opening
dial position is already in the tree by convention
(`AgentUptakeSystem.for_agent()` opens the vaporizer at that agent's 1 MAC), and
the patient circuit volume is `PL-TBMX`'s deferred half. This item removes one
blocking `required`, documents where the number comes from when a profile is
silent, and stops. If the object is built later it subsumes the fallback without
having to undo it.

**What would falsify this.** A manufacturer publishing a startup fresh gas flow
— which would make the field supplyable and the requirement merely strict rather
than blocking; the survey's search being incomplete, which it invites itself —
its "What is missing" list names the Dräger *Instructions for Use* technical
data sections it could not reach; or a
decision that a machine profile *should* assert a recommended starting flow as
an educational claim of its own, which would be a deliberate reversal of
`docs/machine-abstraction.md` and needs the project owner rather than this item.
Note what would *not* falsify it: changing the shipped 4.0 to some other number
is `PL-NM7X`'s question, already decided, and independent — the field being
required is a schema problem whatever value it holds.

**Not in scope.** No change to the value 4.0. No run-opening-conditions object.
No machine-by-id loading — that is `PL-2FZ9`, and this item works with one
profile or ten. No change to `core/supported_ranges.py`'s envelope, and no new
relationship between the fallback and `deliverable_fresh_gas_flow_range`; a
profile declaring a range and no startup flow falls back to the documented
value, and `BreathingCircuit` refuses it in its own words if the range excludes
it, exactly as it would refuse a declared one.

**Done when.** A machine profile may omit `default_fresh_gas_flow_l_min` and
load; a run built from such a profile opens at the documented fallback flow and
a test named for that behaviour asserts it; the fallback's authority is stated
where a reader of the schema will meet it; `docs/machine-abstraction.md` records
that the tree now agrees with it; `reference_circle_system.json` is unchanged;
and `make check` is green. The `verify:` command looks for a test whose name
starts `test_a_profile_omitting_the_default_fresh_gas_flow_falls_back` in
`tests/unit/test_circuit.py`, so name it that way.
