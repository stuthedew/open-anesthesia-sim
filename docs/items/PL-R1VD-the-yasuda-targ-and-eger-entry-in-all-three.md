---
id: PL-R1VD
title: The Yasuda, Targ and Eger entry in all three agent files opens 'cited but not adopted' while its adopted field has been true since PL-FN5F on 2026-09-13 - the stale opener PL-1JDD removed from Davis and Mapleson
priority: P2
effort: S
status: done
classes: defect, docs
feature: provenance
touches: src/anesthesia_sim/data/agents/sevoflurane.json, src/anesthesia_sim/data/agents/isoflurane.json, src/anesthesia_sim/data/agents/desflurane.json
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-30
closed: 2026-09-30
pr: 1229
payoff: a reader checking where the nine tissue:gas coefficients come from is told the truth in the first sentence of each note, not its reverse
verify: ! grep -q 'cited but not adopted. Human tissue study' src/anesthesia_sim/data/agents/sevoflurane.json && ! grep -q 'cited but not adopted. Human tissue study' src/anesthesia_sim/data/agents/isoflurane.json && ! grep -q 'cited but not adopted. Human tissue study' src/anesthesia_sim/data/agents/desflurane.json
---

**Problem.** The Yasuda, Targ and Eger entry in all three agent files opens 'cited but not adopted' while its adopted field has been true since PL-FN5F on 2026-09-13 - the stale opener PL-1JDD removed from Davis and Mapleson

**What is wrong, read from the files on 2026-09-30.** In
`src/anesthesia_sim/data/agents/sevoflurane.json`, `isoflurane.json` and
`desflurane.json`, the `sources` entry citing Yasuda N, Targ AG, Eger EI II
(*Anesth Analg* 1989) declares `"adopted": true`, and its `note` opens "Tier 1,
primary measurement, cited but not adopted." The same note says, further down,
"ADOPTED 2026-09-13, ON THE PROJECT OWNER'S DECISION (PL-FN5F). `adopted` moves
from false to true, and this entry becomes the authority for this file's three
tissue:gas coefficients." So `PL-FN5F` flipped the field and appended the
adoption, and left the opener saying the opposite.

**Why it is a defect and not a dated record.** The opener carries no date and
is in the present tense, so under `docs/MODEL.md` § "How this document is held
to the tree" it is a live claim, not a record of what was true before
2026-09-13. The project has already ruled on this exact shape: `PL-1JDD` found
the Davis and Mapleson entry in `reference_adult.json` opening "CITED BUT NOT
ADOPTED" four sentences above its own adoption, called writing `adopted: true`
under prose saying the opposite "the correct-number-wrong-label failure", and
removed the stale opener. That entry now opens "Tier 2, published model
quantification, ADOPTED - see below", which is the shape the fix takes here.

**Why it matters.** A reader auditing where the nine tissue:gas coefficients
come from reads the opener first, and is told the measurement is not their
authority when it is. `CLAUDE.md`'s clinical-output standard counts a correct
value carrying the wrong provenance as a safety failure, and `docs/MODEL.md`
§ "Source hierarchy" sends that reader to these notes.

**How far it reaches.** Only these three. Every one of the 44 `sources`
entries was scanned on 2026-09-30 for two contradictions: an adopted entry
with "not adopted" in the first 200 characters of its note, and an unadopted
entry calling itself "the source of the stored" value. These three were the
only hits.

**Relation to other items.** It is the class `PL-9LXK` names - a prose claim
about a source's adoption drifting from the declared field - found while
re-confirming that item, and an instance of the mechanism `PL-4FBP` heads. The
drift dates from 2026-09-13, before `PL-4FBP` closed on 2026-09-19, so it is an
old member found late. It is not evidence that the head is still producing new
ones. If `PL-9LXK`'s recommended route is taken, adding a per-value
`authority_for` to every `sources` entry, that work edits all three files and
this should ride it.

**Done when.** Each of the three notes opens with the adoption and its date,
in the form Davis and Mapleson's now takes. The measured values and the
not-substituted reasoning below the opener stay as they are. The fixing session
also decides whether a guard is owed, and records the answer here. The phrase
"not adopted" inside the opening sentence of an entry declaring `adopted: true`
is an exact test for how this project writes its openers.
