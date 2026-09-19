---
id: PL-JQY1
title: max_delivered_concentration_percent is a vaporizer device maximum stored as an agent property, so 18% reads as a fact about desflurane
status: untriaged
feature: delivery-semantics
added: 2026-09-19
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
