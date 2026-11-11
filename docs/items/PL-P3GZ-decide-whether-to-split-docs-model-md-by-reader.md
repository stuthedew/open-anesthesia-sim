---
id: PL-P3GZ
title: Decide whether to split docs/MODEL.md by reader: the reverse outline puts 13% of its words in a model description and 72% with a developer
priority: P2
effort: L
status: done
classes: docs, planning
feature: model-md-structure
touches: docs/MODEL.md, docs/items/PL-1VXY-apply-the-2026-11-05-chapter-reads-within.md, docs/items/PL-52KB-docs-model-md-has-five-broken-section-pointers.md, docs/items/PL-19W8-hold-docs-model-md-known-limitations-numeric.md
blocked-by: PL-B07T
deferred-from: v0.7.0 - a decision about how docs/MODEL.md is divided between readers; the schematic release does not depend on it
added: 2026-11-10
closed: 2026-11-11
pr: 2105
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

**Recommendation.** [superseded 2026-11-11: the design round below kept the split and the model description, and revised the rest. No table is generated and the requirements get no numbers.] Split it. Keep `docs/MODEL.md` as the model description
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

**Design round, 2026-11-11.** The round read `PL-B07T` (the accepted draft,
and what it leaves out), `PL-9RLM` (the reverse outline), `PL-YKKC` (the
second outline's structure findings), the three writing rulings a split
changes (`PL-TZ7R`, `PL-W8FL`, `PL-BS6N`) and the tools that hold the
document's path. It changed no file but this one.

*What the round counted.* Each figure is a one-off count on `main` at
`5b7a97b1b`, 2026-11-11.

- *Growth.* `docs/MODEL.md` held 11,234 words on 2026-09-01, 67,088 on
  2026-09-15, 94,569 on 2026-10-01, 102,971 on 2026-10-15, 138,610 on
  2026-11-01 and 129,453 on 2026-11-10.
- *Work still to land in it.* 60 open items declare `docs/MODEL.md` in
  `touches` (`bin/docket concurrent PL-P3GZ`).
- *Citations.* Python files under `src/` and `tests/` cite its sections 354
  times, by 80 distinct titles, in 117 files. The figures under "What a
  split would cost" above counted every Python file and missed citations
  wrapped across lines. By the home the outline gives the cited section: 141
  cite an interface section, 48 the model description, 46 a verification
  section, 40 a section that mostly restates code, 19 parameter sources, 18
  a section that is mostly history and 3 a section to cut. The count could
  not place 39, most of them fixtures in tests of the documentation check.
- *A missed citation fails the check.* `tools/doc_check.py` already refuses a
  citation in a docstring when the document it names holds no such heading
  (`tests/unit/test_doc_check.py`,
  `test_citation_in_a_source_docstring_is_held_to_the_document_it_names`).
- *Whole sections.* Summing the outline by `##` section, seven interface
  sections hold 59,940 words, six verification sections hold 32,206, and
  Parameter provenance holds 13,176. The table under "The order of work"
  names them. Moving those fourteen sections whole leaves about 24,000 words
  in `docs/MODEL.md`.

*The published basis, read on 2026-11-11.* Three papers were read in full
text at PubMed Central.

- Erdemir A, Mulugeta L, Ku JP, et al. Credible practice of modeling and
  simulation in healthcare: ten rules from a multidisciplinary perspective.
  J Transl Med. 2020;18(1):369. doi:10.1186/s12967-020-02540-4. PMID
  32993675. Rule 6 asks for "users' and developers' guides" beside the code,
  and says "Additional documentation, such as a user or developer guide
  [...] can similarly provide detailed explanations not suitable for a
  journal publication." Rule 4 says that to describe limitations fully "it
  can be helpful to consider different audiences (e.g., limitations that are
  important to manuscript reviewers versus another modeler who wishes to
  extend the modeling and simulation framework)".
- Shebley M, Sandhu P, Emami Riedmaier A, et al. Physiologically based
  pharmacokinetic model qualification and reporting procedures for
  regulatory submissions: a consortium perspective. Clin Pharmacol Ther.
  2018;104(1):88-110. doi:10.1002/cpt.1013. PMID 29315504. Table 4 lists
  the sections of a model report and gives each an audience, "All readers"
  or "Technical". Model assumptions, model parameters and model structure
  are separate sections from the evaluation criteria and the results.
- Kuemmel C, Yang Y, Zhang X, et al. Consideration of a credibility
  assessment framework in model-informed drug development: potential
  application to physiologically-based pharmacokinetic modeling and
  simulation. CPT Pharmacometrics Syst Pharmacol. 2020;9(1):21-28.
  doi:10.1002/psp4.12479. PMID 31652029. It restates the definitions of ASME
  V&V 40: "verification is the process of demonstrating that the equations
  are solved correctly in a mathematical sense, validation is the process of
  demonstrating that the correct equations (for the question of interest)
  are being solved". Its Table 2 lists verification of the code and of the
  calculation apart from validation. The standard itself was not read.

Four hosts could not be reached from the session on 2026-11-11:
`diataxis.fr`, `www.fda.gov`, `collections.nlm.nih.gov` and
`centaur.reading.ac.uk`. `curl` got no connection, and the fetch tool
reported that the host names did not resolve. So Diataxis is still cited
from memory, as the recommendation above says. The round does not rely on
the FDA's guidance on reporting computational models, the FDA's guidance on
the format of pharmacokinetic model reports, or the TRACE format of Grimm et
al. (Ecol Model. 2014;280:129-139), none of which it could read.

*Routes weighed.*

1. *Separate documents, one per reader.* Recommended, and set out below.
2. *One file in two parts, the clinician's part first.* Every path and
   citation would stay as it is. Refused, for three reasons. The file stays
   at about 129,000 words, which the copy editor cannot take whole
   (`PL-HTB9`). The clinician's part would restate facts that the
   developer's part states in the same file. And the repository would still
   name no other home for a test's description or an interface rule, which
   is the cause of the growth that "Generator check" below records.
3. *Rename the whole file for developers and install the draft as
   `docs/MODEL.md` in one step.* The clinician would get their document
   first. Refused, because two documents would both state the model until
   the old text was cut, and a change to the model would have to edit both.
4. *Leave the document whole.* Refused. The owner accepted the draft as the
   document a clinician should get, and nothing checks the draft while it
   sits beside the document it summarises.

*The documents.* The three developer documents are named here by what
they hold. The build chooses their file names.

| Document | Reader | What it holds |
| --- | --- | --- |
| `docs/MODEL.md` | A clinician or educator | The accepted draft: what the model represents, its units, assumptions and equations, each parameter with its source, the controls and their limits, how to read the display, the comparisons with measurements in people, the limitations that can change what a value means, and the reference list. |
| The verification document | A developer | The numerical method as implemented, the supported step and input ranges, each required test with its limit and what it can detect, and the hazard list. |
| The interface document | A contributor who changes the interface | What the display must show and in which state, the controls, marks, halts and branches, the run record, displayed precision, and colour contrast. |
| The parameter document | A developer, or a clinician checking a value against its source | The provenance table with each value's file and key, how each source was read, and why each value was chosen over the alternatives. |

Text that restates a docstring or a test goes to that docstring or test.
Decision history goes to the item that took the decision. Planned work goes
to `ROADMAP.md`. `PL-B07T` lists, for the model description, each such fact
and its home.

Together the four documents are the model's specification, and the
safety-critical standard in `CLAUDE.md` applies to all four.
`docs/MODEL.md` stays the home of the equations, units, assumptions,
parameter values and limitations. The verification document becomes the
home of the numerical method, which § 5.9 of the draft describes for a
clinician in a few sentences.

*The order of work.* Three stages, each filed as items once the owner
decides.

1. *Move whole sections, word for word.* One pull request for each new
   document. Each moves `##` sections out of `docs/MODEL.md` unchanged,
   re-points the citations of those sections with a script, and extends the
   checks named under "What the split changes outside the documents" to
   the new file. The move changes no value, equation, code span or
   citation, and the build shows that with the comparison that
   `tools/model_rewrite.py lost` makes. The round did not check whether
   that tool can compare across files.

   | Destination | Sections moved | Words |
   | --- | --- | ---: |
   | The interface document | Runtime controls; Reset behavior; Agent-change behavior; Discarding a run; What a branch comparison asserts; Interface boundary; Minimum displayed outputs | 59,940 |
   | The verification document | Conservation of agent mass; Numerical method; Reasonably foreseeable misuse; Required invariants; Required tests; Release gate | 32,206 |
   | The parameter document | Parameter provenance | 13,176 |

2. *Replace what is left with the accepted draft.* About 24,000 words
   remain in `docs/MODEL.md`: the status, purpose and intended use, the
   model boundary, assumptions, conventions, symbols, tissue groups,
   compartment capacities, governing equations and known limitations, and
   the section on how the document is checked. The build first applies to
   the draft every change `docs/MODEL.md` took after `50af1a2e`. It puts
   the stored-value markers back in the draft, and the draft's path among
   the documents `tools/doc_check.py` checks them in. It places each fact
   that `PL-B07T` lists as left out in its home. Then the draft becomes
   `docs/MODEL.md`, and `docs/prose-review/model-description-draft.md` is
   deleted. The owner reads only what differs from the draft they accepted,
   quoted before and after.
3. *Sort inside each developer document, one item per document.* Move each
   paragraph that the outline gives another home, after a reader confirms
   the label. Cut a paragraph that restates a docstring, a test or an item
   only after confirming that the home holds the fact. Apply the structure
   findings of `PL-YKKC` and `PL-1VXY`, and fix the pointers of `PL-52KB`.
   The hold on copy editor runs ends for a document when its item closes.

Stage 1 collides once with each branch in flight that edits a moved
section. That branch ports its edit to the new file when it brings `main`
in. Eleven branches were in flight on 2026-11-11.

*Calls the round took.* Each is a choice of internal structure, so the
round decided it.

- *No table is generated.* [revises the recommendation above, 2026-11-11]
  `check_provenance` in `tools/doc_check.py` already refuses a provenance
  table that disagrees with the data files in either direction, and
  `check_named_tests` refuses a test name the tree does not hold. A
  generator would add a script, a committed output and a freshness check
  for a guarantee the two checks already give. Reopen this if stage 3 finds
  a table that neither check holds.
- *Requirements keep their headings and get no numbers.* [revises the
  recommendation above, 2026-11-11] The code cites a requirement by its
  quoted heading, and the documentation check resolves that. A numbering
  scheme would be a second way to name the same paragraph.
- *A mixed section moves whole in stage 1, to the home of most of its
  words.* Sorting its paragraphs waits for stage 3, so that stage 1 stays a
  move that a comparison can verify.
- *An open item's `touches` is re-pointed when the item starts.* The start
  mode already asks a session to re-confirm an item whose file has changed.

*What the split changes outside the documents.* Stage 1 carries these,
because a new document that no check reads would hold clinical values
unchecked.

- `CLAUDE.md`: the sentence that makes `docs/MODEL.md` the authoritative
  specification, the list of simulator documents under "Two standards", and
  the fix-now rule's list of clinical paths.
- `.claude/rules/plain-writing.md`: the table of readers, and the paragraph
  that keeps developer detail in notes that open "**For developers.**"
  (`PL-W8FL`, `PL-TZ7R`). After stage 2 `docs/MODEL.md` has no such notes.
- `tools/doc_check.py`: the provenance table's document, the documents the
  stored-value markers are checked in, and the named-test and bound-family
  checks.
- `subprojects/docket/src/docket/arming.py`: `MODEL_DOC`, the paths held for
  the owner's read, and the paths that take a second blind review pass.
- `tools/model_rewrite.py`, `tools/model_doc_review.py`,
  `tools/new_prose.py`, `tools/copy_edit.py`, `tools/blind_review.py` and
  `tools/product_paths.py`, which name the path.
- Thirteen files under `.claude/rules/`, six under `.claude/skills/` and
  three under `.claude/agents/` name the path.

**Question for the owner.** Should `docs/MODEL.md` become the description
you accepted, with the tests, interface rules and source detail moved to
three documents for developers, and should that work start now or after
v0.7.0 ships?

1. *Split, starting now.* A clinician who opens `docs/MODEL.md` reads the
   15,500-word description and nothing else. Stage 1 and stage 2 run before
   the remaining interface work, and each branch in flight ports its edits
   to a moved section once.
2. *Split, after v0.7.0 ships.* The same end state, later. Until then each
   interface item adds its rules, tests and history to the 129,000-word
   document, the draft goes out of date as `docs/MODEL.md` changes, and
   `PL-1VXY`, `PL-52KB` and `PL-HTB9` stay held.
3. *Do not split.* `docs/MODEL.md` stays whole, and the draft is deleted,
   because a second description that nothing checks would mislead.

**Recommendation (design round, 2026-11-11):** option 1. The document grew
from 11,234 to 129,453 words in ten weeks, 60 open items will add to it,
and 141 of the 354 citations already point at interface sections that a
clinician does not read. Stage 1 is a move that a comparison verifies, so
its risk is the one-time port by branches in flight. The choice is the
owner's because it changes which documents are the model's specification
and it puts this work ahead of release work.

**Decision (project owner, 2026-11-11, ratified):** option 1. Split
`docs/MODEL.md` by reader, starting now. It was chosen over splitting after
v0.7.0 ships and over leaving the document whole. The owner's words were
"Agree with recs". The answer takes the round's design as written: the four
documents, the three stages and the four calls the round took. The work is
filed as seven items under the feature `model-md-structure`, in the order
they run:

| Stage | Item | What it does | Status |
| --- | --- | --- | --- |
| 1 | `PL-CTXZ` | Moves the seven interface sections to the interface document. | `ready`, P1 |
| 1 | `PL-6PPZ` | Moves the six verification sections to the verification document. | waits on `PL-CTXZ`, P1 |
| 1 | `PL-FWR6` | Moves § "Parameter provenance" to the parameter document. | waits on `PL-6PPZ`, P1 |
| 2 | `PL-48MX` | Replaces what is left of `docs/MODEL.md` with the accepted draft. | waits on `PL-FWR6`, P1 |
| 3 | `PL-SY7G` | Sorts the interface document by reader. | waits on `PL-48MX`, P2 |
| 3 | `PL-4H8Q` | Sorts the verification document by reader. | waits on `PL-48MX`, P2 |
| 3 | `PL-N83Z` | Sorts the parameter document by reader. | waits on `PL-48MX`, P2 |

The three moves run one after another because each edits `docs/MODEL.md`,
`CLAUDE.md` and the documentation check. The P1 on the first four records
the owner's choice to start now, ahead of the remaining interface work.
`PL-1VXY` now waits on `PL-48MX`, and the stage 3 items apply its findings.
`PL-52KB` stays startable, because it is on v0.7.0's frozen list and making
it wait on the split would take it off that release's gate. Its pointers can
be fixed before or after the moves.

**What waits on this.** [superseded 2026-11-11: the owner decided to split. `PL-HTB9` and `PL-52KB` no longer wait on this item. `PL-1VXY` waits on `PL-48MX`, because the text it edits moves first. The hold on copy editor runs and within-section restructuring lasts for `docs/MODEL.md` until `PL-48MX` closes, and for each developer document until its stage 3 item closes.] The owner asked the Projects trial's coordinator on
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
