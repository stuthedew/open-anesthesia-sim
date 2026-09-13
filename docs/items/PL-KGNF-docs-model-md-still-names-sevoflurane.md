---
id: PL-KGNF
title: docs/MODEL.md still names sevoflurane specifically in section headings and Purpose, four releases after three agents shipped
priority: P2
effort: M
status: done
closed: 2026-09-13
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

**Closed 2026-09-13. Twenty-three sites, all in the document's structural
front** (lines 24-716) plus one in § "Assumptions", and the separation the
brief called "the work" fell out cleanly because the document had already
generalized the parts around them:

- the block diagram's input, the § "Purpose" mass-conservation bullet, and two
  § "Model boundary" bullets (agent in through fresh gas, no metabolism);
- § "Agent amount" - whose own heading was already generic while all three
  sentences under it said sevoflurane: what a compartment stores, what
  $`M_x`$ denotes, and the unit the code works in;
- eight § "Symbols" rows - $`F_D`$, $`F_I`$, $`F_A`$, $`\lambda_{b:g}`$,
  $`M_C`$, $`M_A`$, $`M_v`$, $`M_i`$. The other rows in the same table were
  already generic ($`F_a`$, $`F_v`$, $`F_i`$, $`\lambda_{i:b}`$, and
  $`\mathrm{MAC}_\%`$ reads "Agent's 1 MAC"), so the table contradicted
  itself row by row;
- both § "Compartment capacities" gas-compartment amounts, and two of the six
  tissue-group bullets - the other four were already generic;
- § "Conservation of sevoflurane" is § "Conservation of agent mass", with its
  delivered and exhausted amounts. The heading is cited from nowhere else in
  the tree, so the rename cost no citation sweep;
- § "Assumptions": carrier gases do not affect **agent** kinetics.

**What stays, audited against the Done-when.** 113 mentions remain and each is
one of the three permitted kinds: historical (§ "Status"'s v0.1.0 sentences,
the note that isoflurane and desflurane were added in v0.2.0 using these
equations unchanged), a per-agent measured value (every Yasuda row, the MAC and
MAC-awake tables, the timing and residual measurements, the ISO 5360 colours),
or provenance citing `data/agents/sevoflurane.json`. Line 77 is the one worth
naming: sevoflurane is there because the Gas Man reference simulator is where
*this agent's* parameters came from, which is provenance rather than
structure.

No equation, parameter, numerical method, unit or displayed value moves; the
394 documentation and reference tests pass.
