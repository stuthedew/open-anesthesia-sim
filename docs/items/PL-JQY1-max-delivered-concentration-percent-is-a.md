---
id: PL-JQY1
title: max_delivered_concentration_percent is a vaporizer device maximum stored as an agent property, so 18% reads as a fact about desflurane
priority: P2
effort: S
status: ready
classes: refactor, docs
feature: delivery-semantics
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
