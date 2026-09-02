---
id: PL-KGNF
title: docs/MODEL.md still names sevoflurane specifically in section headings and Purpose, four releases after three agents shipped
priority: P2
effort: M
status: ready
classes: defect, docs
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-09-02
verify: python3 tools/doc_check.py check && ! grep -q '^## Conservation of sevoflurane' docs/MODEL.md
---

**Problem.** `docs/MODEL.md` names sevoflurane in places that describe
agent-generic structure: the block diagram's input ("delivered sevoflurane"),
the Purpose bullet on mass conservation, the compartment-storage definition and
every row of the symbol table ($`M_C`$, $`M_A`$, $`M_v`$, $`M_i`$,
$`\lambda_{b:g}`$), the model-boundary bullets, the tissue-group definition,
and the `## Conservation of sevoflurane` section heading. Isoflurane and
desflurane have been selectable agents since v0.2.0 and use these same
equations unchanged — which the document states in prose under "Status" and
again under "Purpose", while the headings, tables and equations around that
sentence still read as sevoflurane-only.

**Why it matters.** A reader running desflurane meets a symbol table that calls
$`\lambda_{b:g}`$ the "Sevoflurane blood:gas partition coefficient" and a
conservation section headed with an agent they are not using. A correct value
under the wrong label is the failure this project's presentation standard names
explicitly, and `docs/MODEL.md` is where a reader goes to learn what a
displayed number means. It stays at P2 rather than carrying a safety class
because the document does say, in two places, that the equations are shared —
the defect is that its headings and tables contradict its own prose, not that
it withholds the generalization.

**Where.** `docs/MODEL.md`. The agent-generic mentions above move to "the
agent" or "the loaded agent". The sevoflurane-specific ones stay: the
historical statements about what v0.1.0 modeled, the parameter-provenance rows
citing `data/agents/sevoflurane.json`, and the per-agent measured numbers in
the numerical section (the capacity-guard timings and the wash-in run).
Separating the two is the work; the substitution itself is mechanical.

**Found.** 2026-09-02, captured during a queue review and triaged in the
v0.2.9 release pass.

**Done when.** No heading, symbol definition, or structural statement in
`docs/MODEL.md` names one agent where the model is agent-generic, and every
remaining mention of sevoflurane is historical, a per-agent measured value, or
a citation to that agent's parameter file.
