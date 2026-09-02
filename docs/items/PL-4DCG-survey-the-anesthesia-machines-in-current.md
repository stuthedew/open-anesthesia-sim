---
id: PL-4DCG
title: Survey the anesthesia machines in current clinical use for the variables that change a simulated result
priority: P2
effort: M
classes: docs
not-delegable: No command can prove a survey: the deliverable is the judgment about which manufacturer specification reaches a modelled number, and its correctness is whether each recorded value matches the manual revision it cites. Non-delegable by `touches` as well, which names docs/MODEL.md.
status: ready
feature: anesthesia-machine
touches: docs/MODEL.md, ROADMAP.md
added: 2026-09-02
---

**Problem.** `ROADMAP.md` planned-milestone item 1 commits to "a modular
anesthesia-machine abstraction", and PL-FG9D is to design it. Neither can be
designed from first principles, because the thing that decides the shape of
the abstraction is not what an anesthesia machine *is* — it is which of the
ways real machines differ actually reach a number this simulator computes or
displays. That has never been written down here, so any base class designed
today would be a guess at its own extension points.

**Why it matters.** The stated goal is that a *real commercial* machine can be
added as a module. That is a fidelity claim: name a machine in the interface
and a learner will attribute to it the behavior of the machine on the wall in
their OR. Getting the variables wrong does not merely make the abstraction
awkward to extend — it makes the first two or three machines fit and every
later one a special case, which is the kind of architectural problem
`CLAUDE.md` ranks above polish. The survey is also the provenance record:
under the safety-critical standard, a machine-specific constant that reaches a
displayed value needs a citable source, and the manufacturer's operator or
technical manual is that source.

**Scope: surveyed with judgment, not transcribed.** The failure to avoid is a
machine profile where every specification in the manual became a field because
it was in the manual. So a variable is written down because there is a stated
reason it matters to the model, and that reason is written down beside it. A
variable nobody can give a reason for does not get one invented; it is left
out, and leaving it out costs nothing to reverse if a later milestone gives it
a reason. The discipline this feeds is the one on the profile schema itself,
in PL-FG9D.

The reason is judged against the model *as it will be through the machine
milestone*, not against today's four controls — scoped to today's model the
survey would collect two constants and be useless to the item it exists to
serve. Record which of the three each variable is:

- **(a) Changes a number today.** Two are already known. Circuit volume is a
  model parameter with its own provenance item (PL-4YY1). The **default fresh
  gas flow** is the sharper case: `PL-8DJ7` established it is a machine
  setting, not a patient or agent property, and the project owner's recorded
  decision was to wait for this abstraction rather than file it under the
  patient — so it sits as a literal in `core/circuit.py`, is the one number in
  `docs/MODEL.md`'s accuracy table tracing to no cited file, and is named in
  `ROADMAP.md` planned-milestone item 1. It is the first per-machine value
  this survey has to source.
- **(b) Changes a number once planned-milestone item 1 (machine and
  interlocks) and Phase 1 (multi-substance state) land.** The bulk of the
  survey.
- **(c) Ruled out.** One line — the variable, and why it reaches no number —
  written **once for the whole survey, never per machine**, and only where a
  later session would otherwise propose it again. Screens, alarms, workflow,
  self-test and mounting are the obvious members. This is a short list whose
  job is to stop a question being re-opened, not an inventory of what machines
  do; a rule-out that wants a paragraph is really a bucket (b) entry that has
  not been thought through.

**Candidate variables, to be confirmed or ruled out by the survey rather than
assumed.** Each is here because there is a plausible path from it to a
displayed value; the survey's first job is to say whether that path is real,
and a candidate whose path does not survive is left out — or gets bucket (c)'s
one line, if it is one somebody would raise again:

1. **Circle-system internal volume, and absorber volume.** Bucket (a): this is
   the circuit volume the wash-in curve already depends on.
2. **Fresh gas flow: the machine's default and its limits** — the flow the
   machine comes up at, the deliverable range, the minimum total flow, and the
   minimum oxygen flow the machine enforces. Bucket (a) for the default
   (`PL-8DJ7` is waiting on it); bounds on an existing control and the
   interlock floor item 1 needs, for the rest.
3. **Fresh-gas decoupling, and compliance and leak compensation.** These
   decide whether set and delivered ventilation are the same number. This is
   where ventilator drive matters — piston, bellows or turbine is surveyed for
   its consequence here, not catalogued as a taxonomy.
4. **Vaporizer output.** Per-agent dial range and maximum (today a single
   per-agent constant in the agent data file, which a machine dimension would
   have to qualify), dial increments, and whether output depends on fresh gas
   flow or on the delivery device's class. Desflurane is the known break in
   the pattern and should be treated as its own case rather than as an agent
   with different numbers — ISO 5360:2016 declines to specify filling-system
   dimensions for it at all, on the grounds of its properties. PL-043
   deliberately left the dial continuous and recorded that the argument
   reverses if real machine simulation is built; this is the evidence that
   decision needs.
5. **Which agents the machine can deliver at all, and the single-agent
   interlock.** Constrains model selection, which is safety-critical:
   selecting an agent a machine cannot mount should be refused, not simulated.
6. **Sidestream sample flow**, which removes gas from the circuit and so
   changes a number at low fresh gas flow.

**Method, and the standard for it.** Machine behavior is taken from the
manufacturer's operator or technical manual, cited by document and revision,
never from recall or from a secondary summary; standards baselines
(ISO 80601-2-13 for the anesthetic workstation, ISO 5360 for agent-specific
filling and the identification colors the app already uses) are cited by
number and edition. A value that cannot be sourced that way is recorded as
unknown rather than filled in — an unknown circuit volume is a machine that
cannot be added yet, not a machine with a plausible circuit volume.

**Where.** A new document under `docs/`, cited from `docs/MODEL.md` wherever a
machine constant enters the model, and referenced from `ROADMAP.md`
planned-milestone item 1.

**Scope note.** Survey only. No `src/` change, no machine class, no interlock.
This is the input that lets planned-milestone item 1 be scoped; it does not
implement any of it.

**Done when.** The document exists; it names the machines surveyed and why
those; every variable it records carries its bucket and, for (a) and (b), the
reason it matters to the model; every value carries a manual or standard with its
revision, or is marked unknown; and it ends with the one thing PL-FG9D needs —
which variables are per-machine *data* and which are genuinely different
*behavior*. The per-machine values it records are the source rows for
PL-WZVZ's comparison table.
