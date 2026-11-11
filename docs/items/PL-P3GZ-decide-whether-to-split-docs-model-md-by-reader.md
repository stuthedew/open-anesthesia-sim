---
id: PL-P3GZ
title: Decide whether to split docs/MODEL.md by reader: the reverse outline puts 13% of its words in a model description and 72% with a developer
priority: P2
effort: L
status: needs-decision
classes: docs, planning
feature: model-md-structure
touches: docs/MODEL.md
blocked-by: PL-B07T
deferred-from: v0.7.0 - a decision about how docs/MODEL.md is divided between readers; the schematic release does not depend on it
added: 2026-11-10
payoff: a clinician finds the model, its values and its limits without reading past tests, interface rules and decision history
verify: grep -qE '^[*][*]Decision [(]project owner' docs/items/PL-P3GZ-*.md
---

**Problem.** Decide whether to split docs/MODEL.md by reader: the reverse outline puts 13% of its words in a model description and 72% with a developer

**Why it matters.** `docs/MODEL.md` held 11,234 words on 2026-09-01 and holds
129,453 on 2026-11-10. The plain-English rewrites and a full line edit by
the copy editor took it from 142,087 words to about 129,000 and left its
structure as it was. The project owner suspected on 2026-11-10 that the
document's bloat lies in its overall structure more than in its sentences,
and asked for a reverse outline of the whole document. `PL-9RLM` holds that
outline and how it was made.

**What the outline shows.** The document is at least four documents in one.
By where each paragraph would best live, its words divide as follows:

| Best home | Words | Share |
| --- | ---: | ---: |
| Verification and validation report | 29,975 | 23% |
| Code, as a docstring or a test | 23,578 | 18% |
| Interface requirements list | 22,665 | 18% |
| Item record (history and rationale) | 22,073 | 17% |
| Model description for a clinician | 16,792 | 13% |
| Parameter source register | 11,370 | 9% |
| Nowhere (cut) | 2,717 | 2% |

So the words are mostly misplaced and few are empty. 72% serve a developer,
23% a clinician and 5% only the project's upkeep. § "Minimum displayed
outputs" has 33,567 words, of which 1,856 belong in a model description, and
§ "Runtime controls" has 18,702, of which 1,887 do. The 101 notes that open
"**For developers.**" hold 39,406 words and often restate the requirement
above them with function and test names. The labels are one model's
judgement of each paragraph, with no second rater.

**A second outline agrees.** Another session made its own reverse outline of
the document on the same day, by section and not by paragraph label. It
found that the model's own sections, from the model boundary through
conservation of agent mass, are about 11% of the document. `PL-YKKC` holds
its findings, which include headings that do not name what they hold and
terms used before they are defined. Weigh them with this decision.

**What a split would cost.** 147 Python files mention `docs/MODEL.md`. The
code and tests cite 81 of its sections in 250 places, and
`tools/doc_check.py` binds sections of it to the tree. A split moves or
re-points each of those. `CLAUDE.md` makes `docs/MODEL.md` the authoritative
specification for the model as implemented, and
`.claude/rules/plain-writing.md` says the numerical method stays in it
(`PL-TZ7R`), so a split also changes those two rules.

**Decision needed.** Whether to split `docs/MODEL.md` by reader, into which
documents, and which of them are generated from the tests and data files.

**Recommendation.** Split it. Keep `docs/MODEL.md` as the model description
that a clinician reads: the model, its equations and parameters, its
assumptions and the limitations that change a clinical conclusion. Move the
interface behaviour to a numbered requirements list tied to its tests.
Generate the table of tests and the parameter source table from the tests
and the data files, so that neither is a second copy. Leave decision history
in the items, where the capture rule already puts it. The published basis is
Diataxis, which separates documentation by what its reader needs to do
(https://diataxis.fr). The session could not reach that site on 2026-11-10,
so it cites the framework from memory. This is the owner's decision because
it is a major refactor that changes what the project's specification is.

**The draft came first.** The owner agreed on 2026-11-10 to read a draft of
the clinician's model description before deciding this (ratified, over
deciding from the outline's totals alone). `PL-B07T` wrote that draft and
closed on 2026-11-11.

**The owner's answer on the draft, 2026-11-11.** The owner read
`docs/prose-review/model-description-draft.md` and answered "Yes with
references": it is the document a clinician should get. It now carries a
reference list. `PL-B07T` records what the draft takes, what it leaves out
with the home of each fact, and the two things a split must add before the
draft could replace any part of `docs/MODEL.md`: the stored-value markers,
and its path among the documents `tools/doc_check.py` checks them in.

**What waits on this.** The owner asked the Projects trial's coordinator on
2026-11-10 to hold all copy editor runs, line edits and within-section
restructuring of `docs/MODEL.md` until this is decided. That covers `PL-1VXY`
(apply the chapter reads' within-section findings), `PL-52KB` (five broken
section pointers) and `PL-HTB9` (the copy editor fails on a whole-document
request). A split would cut or move most of the text they would edit, and
the owner ruled on 2026-11-07 that no document is line edited ahead of its
restructure.

**Done when.** The owner has decided whether to split `docs/MODEL.md` by
reader, and this item records the decision in a paragraph that opens
"**Decision (project owner". Where the decision is to split, the work it
needs is filed as items.

**Generator check.** An instance of the fact that `PL-J1ZM` (sessions
over-explain in every kind of text) states: no rule says what a reader can
do without. The outline adds a second cause for `PL-J1ZM`'s record. The
repository names no home but `docs/MODEL.md` for a test's description, an
interface requirement or a value's source history, so each change adds them
there.
