---
id: PL-8DJ7
title: The default fresh gas flow is a literal in core/circuit.py, so MODEL.md restates it twice outside both the provenance table and the new prose markers
priority: P2
effort: M
status: done
classes: defect, docs
feature: model-spec-accuracy
touches: src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/data, docs/MODEL.md, tools/doc_check.py
added: 2026-09-02
closed: 2026-09-02
pr: 216
---

**Problem.** `BreathingCircuit.fresh_gas_flow_l_min` defaults to `4.0` as a
literal in `src/anesthesia_sim/core/circuit.py:70`. No data file holds it, so
it has no provenance row, no citation, and no version. `docs/MODEL.md`
restates it twice as "4 L/min fresh gas" - once as the gate's reference point
and once as the defaults note under the accuracy table - and neither
restatement can be marked by `PL-1BPV`'s new prose markers, because a marker
names a data file and key and there is none to name.

**Why it matters.** Found while marking prose values for `PL-1BPV`. Two of the
four sites that brief listed turned out to be this constant rather than the
reference adult's `default_alveolar_ventilation_l_min`, which is also 4 L/min -
a coincidence that would have bound a marker to the wrong key had the design
been a numeral scan instead of an explicit declaration. So the near-miss is
already recorded; what is left is that the value itself is unprovenanced.

`CLAUDE.md` asks for agent and model parameters to live in validated,
versioned data files, and a default fresh gas flow is a clinically meaningful
starting condition: it sets how fast the circuit washes in at the start of
every run, and the accuracy table's whole "default flows" column is computed
at it. A reader tracing that column back reaches a literal with no source,
while every other number in the same table traces to a cited file.

**Where.** `src/anesthesia_sim/core/circuit.py:70`; `docs/MODEL.md` at the
gate's reference-point list and the defaults note beneath the accuracy table;
`src/anesthesia_sim/data/` for wherever it should live;
`tools/doc_check.py` if the provenance table gains a row for it.

**Decision needed.** Where does the default fresh gas flow belong? It is not an agent property and
not obviously a patient property either - it is a machine setting, and the
roadmap's planned anesthesia-machine abstraction is the natural home, which
may be a reason to wait rather than to invent a file now. The cheap
alternative is a row in `reference_adult.json` alongside the ventilation and
cardiac-output defaults it sits with in the prose; that is honest about how it
is used today and moves later with everything else. Whichever it is, the value
then gets a provenance row and the two prose sites get markers, at which point
the gap closes by the mechanism `PL-1BPV` already built.

Check for siblings while there: any other numeric default in `core/` that
`docs/MODEL.md` restates has the same problem, and the answer should cover the
class rather than this one constant.

**Decision (2026-09-02, project owner): wait for the anesthesia-machine
abstraction; do not invent a home now.** A fresh gas flow is a machine setting,
not a patient or agent property. Putting it in `reference_adult.json` today
would be quick and would close the provenance gap, but it files a machine
setting under the patient and creates a home that moves again within a
milestone or two — so the citation, the schema and every reference to it get
written twice, and the intervening state says something false about what kind
of quantity it is.

**The intent is routed rather than dropped.** `ROADMAP.md`'s planned milestone 1
— the modular anesthesia-machine abstraction — now names this constant in its
own line, so scoping that milestone picks it up. That is `CLAUDE.md`'s rule for
a change wanted but not yet ready to build: one line of intent on the roadmap,
not a queue item that sits there being read past. This item closes on the
second branch of its own Done-when, the decision recorded with its reasoning.

**What is accepted in the meantime.** The value stays a literal, the two
`docs/MODEL.md` restatements stay unmarked, and the accuracy table's "default
flows" column keeps tracing to code rather than to a cited file. That is a real
gap and it is being carried deliberately, not overlooked. It is bounded: the
value is correct today, `PL-1BPV`'s markers cover every other number in the
same passages, and a change to it would be a change to `core/` — a protected
path no delegated worker may edit, and one no session reaches without reading
the file.

**Done when.** The default fresh gas flow is sourced from a versioned data
file with a provenance row, both `docs/MODEL.md` restatements carry markers,
and no numeric default in `core/` that the model specification restates is
left unprovenanced - or the decision to leave it in code is recorded here with
its reasoning.
