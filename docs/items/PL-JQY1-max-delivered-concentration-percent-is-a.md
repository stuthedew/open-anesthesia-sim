---
id: PL-JQY1
title: max_delivered_concentration_percent is a vaporizer device maximum stored as an agent property, so 18% reads as a fact about desflurane
priority: P2
effort: S
status: ready
classes: refactor, docs
feature: machine-profile-framework
touches: src/anesthesia_sim/data/agents, src/anesthesia_sim/data/machines, src/anesthesia_sim/core/circuit.py, docs/MODEL.md
added: 2026-09-19
payoff: settles whether a vaporizer's calibrated maximum is keyed to the agent or the machine, so the field name stops re-opening a question its provenance note already answers
verify: grep -qF 'device-capability' docs/MODEL.md
---

**Problem.** max_delivered_concentration_percent is a vaporizer device maximum stored as an agent property, so 18% reads as a fact about desflurane
 — found while writing `docs/machine-survey.md` for `PL-4DCG`.

`src/anesthesia_sim/data/agents/desflurane.json` stores
`max_delivered_concentration_percent: 18.0`, and `docs/MODEL.md`'s breathing-circuit
section describes it as "the 18% calibrated maximum of the Tec 6 vaporizer, which
this model accepts as desflurane's `max_delivered_concentration_percent`". So the
document already knows the number belongs to a device; the data file files it
under the agent, and `core/circuit.py` reads it into
`max_delivered_partial_pressure_fraction` as though it were an agent property.
Sevoflurane's 8.0 and isoflurane's 5.0 are in the same position.

**Why it matters.** A reader of the data file learns that desflurane's maximum
deliverable concentration is 18%, which is not true of desflurane — it is true of
one vaporizer. A different desflurane device, or a machine with an electronically
controlled injector, is not bound to 18% by anything about the agent. That is a
traceability failure of the kind `CLAUDE.md`'s safety-critical standard names:
the value is right and the thing it is attributed to is wrong, so a later reader
cannot tell which inputs produced the bound. It also puts a device constant
outside the machine data file that `PL-4YY1` created for exactly this class of
value.

**Where.** `src/anesthesia_sim/data/agents/*.json`
(`max_delivered_concentration_percent`); `src/anesthesia_sim/core/circuit.py`
(`max_delivered_partial_pressure_fraction`); `docs/MODEL.md` § "Delivery-limit
and MAC parameters"; `src/anesthesia_sim/data/machines/`.

**Do not fix this ahead of `PL-FG9D`.** Where the field should move is the
parameter/strategy question that item answers, and the survey's finding is that
the answer is a *pair* — an agent and a device together — rather than a move from
one file to the other. What is fixable now, and may be all this item is, is the
provenance note saying so where the value is stored.

**Done when.** Either the field carries, at its storage site, that 18% is the
Tec 6's calibrated maximum and not a property of desflurane, or `PL-FG9D` has
moved it and the note went with it.

**The hold named above has lifted** (triage, 2026-09-20). `PL-FG9D` (design the
base anesthesia-machine abstraction) is `done`, closed 2026-09-20, merged as
`#748`. So "do not fix this ahead of `PL-FG9D`" is satisfied and this item is
startable; what it is *not* is automatically resolved, because that design
landed as a zero-diff refactor of the circuit abstraction and did not move this
field. Read `PL-FG9D`'s close-out for what it settled about where a machine
parameter lives before choosing between the two endings below.

The storage site can carry the note without new machinery:
`src/anesthesia_sim/data/agents/desflurane.json` already holds `sources` and
`provenance_gap` alongside `max_delivered_concentration_percent`, which is
where a device attribution belongs if the field stays on the agent.

**Re-scoped at triage, 2026-09-20: the provenance half is already done, and it
was done before this was captured.** Every one of the three agent files carries
an `adopted: true` source whose note says exactly what this item asks for, at
the storage site, and has since `b1a78fc` on 2026-08-23. Desflurane's reads:

> Primary source for a device capability: `docs/MODEL.md`'s source hierarchy
> concerns measured physiologic quantities, and a calibrated dial maximum is
> not one. Tec 6 vaporizer output was analyzed at all integer dial settings
> from 1% to 18%, confirming 18% as the device's calibrated maximum. Used here
> as `max_delivered_concentration_percent`. **This is a device-capability limit
> on the delivered-concentration control, not a scientific model parameter**;
> it does not affect the governing equations.

Sevoflurane's names the Dräger Vapor 2000 and Sevotec 5 and isoflurane's the
Penlon Sigma Delta and Isotec 5, each with the same closing sentence. So the
first of the two endings below — "the field carries, at its storage site, that
18% is the Tec 6's calibrated maximum and not a property of desflurane" — is
satisfied, and the reader this item worries about is not misled by the file:
the attribution is in it, adopted, and explicit.

**What is left is structural, and it is a `refactor` rather than a safety
finding.** A device constant is still *keyed under the agent* — read by
`core/circuit.py` into `max_delivered_partial_pressure_fraction` as though it
were an agent property — while `src/anesthesia_sim/data/machines/` exists as
the home for this class of value (`PL-4YY1`, closed 2026-09-13; it holds
`reference_circle_system.json` today). `PL-FG9D` closed on 2026-09-20 without
touching the field or deciding where it belongs: nothing in that item mentions
`max_delivered_concentration_percent`.

So the open question is whether the value moves to the machine file, stays on
the agent as a documented device-capability entry, or becomes the *pair* the
survey argued for — an agent and a device together — and the answer produces no
wrong clinical value either way, which is why this seats at `P2` as a
`refactor` rather than at `P1` as a `safety` finding.

**Done when** (replacing the one above): the device maximum is either moved to
the machine data file with `core/circuit.py` reading it from there, or recorded
in `docs/MODEL.md` as deliberately keyed to the agent with the reason, so a
later reader is not left to re-open the question from the field name.

**Re-scoped 2026-09-20: this is a row on the machine profile, not a data
migration, and it moves into `feature: machine-profile-framework`.** The
machine-framework audit of the same date reached this item as its sixth finding
and recommended re-scoping rather than filing anything new. Two things changed:
where the item sits, and what it is expected to cost.

*Why the feature moved.* The question this item asks — where a per-machine,
per-agent device limit lives — is one of the data-schema decisions the
machine-profile framework is taking right now, and the framework's own cost
split is what makes the timing matter. Anything that edits an *existing*
profile grows more expensive with every profile that exists:
`_StrictPayload` sets `model_config = ConfigDict(extra="forbid")`
(`src/anesthesia_sim/core/parameters.py`), so no profile may carry an
undeclared key and a required key has no default. Deciding the slot while one
profile ships is a row; deciding it afterwards is a migration of every file.
It was filed under `delivery-semantics` because the survey framed it as a
delivery question; it is a *schema* question, and it belongs with the five
items that are deciding the schema.

*The cheap route, and why it is not the same as moving the field.* Add an
**optional** `agent_limits` mapping to the machine profile — agent id to
maximum delivered concentration in percent — on `_BreathingCircuitPayload` and
its public `BreathingCircuitParameters`, defaulting to absent. Absent means
*this profile declares no per-agent limit*, the agent file's value is used, and
today's behavior is reproduced exactly: no stored value moves, no consumer
changes, no displayed number changes. Present means the machine narrows the
agent's claim, and the effective limit is the intersection.

That is not a new pattern to invent. `deliverable_fresh_gas_flow_range` already
ships it, and `core/circuit.py`'s module docstring states the rule this field
would reuse verbatim: *"Fresh gas flow is bounded twice, by two claims that are
not the same claim (`PL-8PS6`) … The effective limit is the intersection, and
each side refuses in its own name."* Its `None` is documented as *"no machine
range declared"* rather than *"unlimited"*, which is the same honest reading
`agent_limits` needs for its absence, and
`BreathingCircuit._require_the_two_flow_claims_overlap()` is the worked example
of holding both claims in one place. So the cheap route costs one optional
field, one lookup in `AgentUptakeSystem.for_agent()`, and the provenance rows
for any limit a profile actually declares.

*What the full move would cost instead — verified against the source, not
estimated.* Four things, and the first two are the reason this is not a
rename:

1. **The cross-field validator becomes a cross-file check that no per-file
   payload can express.** `_AgentPayload._mac_percent_must_not_exceed_vaporizer_max()`
   in `src/anesthesia_sim/core/parameters.py` rejects an agent whose 1 MAC its
   own vaporizer cannot deliver, raising on
   `self.mac_percent > self.max_delivered_concentration_percent`. Its docstring
   says why it is a `model_validator` rather than a `field_validator` and
   closes: *"The MAC start in `AgentUptakeSystem.for_agent()` depends on this
   holding."* Move the maximum to the machine file and `_AgentPayload` can no
   longer see it — the guard has to be deleted and re-sited at construction,
   where it stops being a statement about a data file and becomes a statement
   about a pairing.
2. **`for_agent`'s 1-MAC start acquires a new failure mode.**
   `AgentUptakeSystem.for_agent()` in `src/anesthesia_sim/core/uptake_system.py`
   builds the circuit with
   `delivered_partial_pressure_fraction=fraction_from_percent(agent.mac_percent)`
   and `max_delivered_partial_pressure_fraction` from the same agent file;
   `BreathingCircuit.__post_init__` then calls `_require_deliverable()`, which
   raises `SimulationConfigurationError` when the delivered fraction exceeds the
   maximum. Today that cannot fire from `for_agent()`, because the validator in
   point 1 guarantees the inequality inside one file. With the limit keyed to
   the machine, a machine whose limit sits below the chosen agent's MAC refuses
   to construct at all, and *which* of three answers is right — refuse the
   pairing with a message naming both, start the run below 1 MAC, or forbid the
   combination where a machine is chosen — is a decision this item would have to
   take. Under the cheap route the same decision arrives only for a profile that
   actually declares a narrowing limit, which is where it belongs.
3. **There is a second read path that never touches the circuit.**
   `src/anesthesia_sim/app/controller.py` reads
   `agent_parameters.max_delivered_concentration_percent` into
   `self._max_delivered_concentration_percent` and publishes it on
   `SimulationSnapshot`; `app/dashboard_frame.py`, `app/simulation_view.py` and
   `app/qt_widgets.py` read it from the snapshot. So the controller would need
   the machine profile too, and the two paths would have to be shown to agree —
   presentation correctness, not just calculation.
4. **The provenance surface is larger than "two markers".** `docs/MODEL.md`
   carries 5 `<!-- provenance: -->` markers, 8 `<!-- derived: -->` markers and 3
   parameter-table rows naming `data/agents/*.json` ·
   `max_delivered_concentration_percent` (counted 2026-09-20). Every one of them
   would have to be re-pointed at the machine file, and `tools/doc_check.py`'s
   `check_provenance` fails `make check` until they all are. The derived markers
   are the awkward ones: they name the agent file as the source of numbers
   computed from the maximum *and* the MAC together, so a move splits a single
   derivation across two files.

Cost of the full move: MEDIUM to HIGH, and it opens the decision in point 2.
Cost of the row: LOW, and it opens nothing until a profile uses it.

*What would falsify the re-scope.* If a machine profile is authored whose
vaporizer limit genuinely conflicts with an agent file's value — a Tec 6
replaced by an injector with a different ceiling for the same agent — then the
agent file's number is no longer a defensible default and the full move is
owed, because two files would be asserting different maxima for the same
physical device. Nothing on the roadmap produces that profile: item 40's scope
is one shipped profile and no machine chooser. Equally, if `agent_limits` turns
out to need a required key rather than an optional one — if any profile must
declare a limit for every agent — the field stops being a row and becomes the
migration this re-scope was avoiding.

*Not in scope, and unchanged by this section.* The provenance half is still
done, as recorded above: the `adopted` source note at each agent file's storage
site already says the number is a device-capability limit. No agent file
changes. No displayed number changes. The `verify:` command is unchanged —
`grep -qF 'device-capability' docs/MODEL.md` was re-run on 2026-09-20 and still
exits 1, because `docs/MODEL.md` does not yet carry the phrase the agent files
do — and the cheap route satisfies it the same way the full move would: the
sentence `docs/MODEL.md` owes is that the agent file carries a
device-capability default which a machine profile may narrow, and where that
leaves the MAC guard.
