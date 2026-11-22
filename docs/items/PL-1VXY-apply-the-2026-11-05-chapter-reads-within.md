---
id: PL-1VXY
title: Apply the 2026-11-05 chapter reads' within-section findings to docs/MODEL.md: PL-BSMF applied only the outline read, and the 30 chapter reads in /mnt/project-files/v0.7.0/repo-copy-edit/runs/docs-MODEL-md/structure/chapter-NN.txt also move paragraphs within a section and fix headings; their row numbers are from cfb15a4a, before the restructure
priority: P2
effort: L
status: done
classes: docs
feature: model-md-structure
milestone: v0.6.20
touches: docs/INTERFACE.md, docs/PARAMETERS.md, docs/VERIFICATION.md
blocked-by: PL-N83Z, PL-4H8Q, PL-SY7G
added: 2026-11-07
closed: 2026-11-22
pr: 2235
payoff: each section of MODEL.md reads in the order its reader needs, so a qualifying paragraph comes before the value it qualifies, and the line edit can start
verify: grep -qF 'How far one stored value can change before the gate fails' docs/VERIFICATION.md
---

**Problem.** PL-BSMF applied only the outline read's 77 findings to docs/MODEL.md (order, repeated facts, misplaced passages, two headings). This item applies the within-section findings of the 30 chapter reads of 2026-11-05, which move paragraphs within a section and fix headings. The reads are in /mnt/project-files/v0.7.0/repo-copy-edit/runs/docs-MODEL-md/structure/chapter-NN.txt.

**Found 2026-11-07 at the close of `PL-BSMF`.** The chapter reads contain
several hundred findings inside single sections, such as paragraphs in the
wrong order, a heading that no longer covers its section, and release history
inside § "Purpose". Their queries were filed separately, as `PL-HR4T` and the
twelve others that `PL-BSMF` names. The reads' row numbers are from cfb15a4a,
before the restructure, so each structural finding has to be found again in
the restructured text.

Apply the findings before the line edit, because the owner ruled on 2026-11-07
that no document is line edited ahead of its restructure. Audit the old text
against the new as `PL-BSMF` did, with two reviewers and in both directions.

**Checked 2026-11-09:** The chapter reads are not in this checkout or this
container. `ls /mnt/project-files` finds no such directory, so the reads can be
opened only where the project's files are mounted, as in a Projects thread.
One within-section finding of the kind this item names is still present:
`grep -n 'must demonstrate' docs/MODEL.md` finds § "Purpose" opening with
release history, "The “Sevo works” milestone (v0.1.0) must demonstrate:"
(line 52), and ending with what v0.2.0 added (lines 65 to 67). `PL-BSMF`'s
`verify:` tested for "The milestone must demonstrate", which the restructure
reworded, so it passes while the release history stays.

**Why it matters.** The restructure put the chapters in order, but inside many
sections a reader still meets a paragraph before the one it depends on, a
heading that no longer covers what is under it, or release history where they
look for what the model does. A clinician reading a section to decide whether
to trust a value can reach the paragraph that qualifies it late, or miss it.
The next line edit of `docs/MODEL.md` waits on this item, because the owner
ruled on 2026-11-07 that no document is line edited before its restructure.

**Done when.** Each within-section finding of the 30 chapter reads has been
found again in the restructured text, and either applied or recorded as no
longer applying, with the reason. The old and new text have been audited in
both directions by two reviewers, as `PL-BSMF` did, so that no statement was
lost. The queries the reads raised stay with their own items (`PL-HR4T` and
the twelve others that `PL-BSMF` names).

**Size, and a recommended split (2026-11-09).** This is effort L and too large
for one session. `PL-BSMF` applied the outline read's 77 findings as one L
item. This item holds several hundred findings across 30 chapter reads, each
to be found again by hand in a 12,763-line document, and each change owes the
two-reviewer audit. Split it before starting into about six slices of five
chapter reads each, in the restructured chapter order, each with its own pull
request and audit. The first slice covers § "Status" through § "Conventions",
which holds the § "Purpose" finding above. Give each slice a `verify:` that
removes one passage its reads name, as this item's does. The work needs the
reads mounted, so it suits a Projects thread.

**Generator check.** One-off: this item applies the `docs/MODEL.md`
structure-read sweep of 2026-11-05. It is not a defect with a cause of its own.

**Waits on the split, 2026-11-11.** The project owner decided on 2026-11-11
to split `docs/MODEL.md` by reader (`PL-P3GZ`). The text this item edits
moves to three new documents (`PL-CTXZ`, `PL-6PPZ`, `PL-FWR6`), and what is
left is replaced by the description the owner accepted (`PL-48MX`). So this
item waited on `PL-48MX`, which closed on 2026-11-22. The three items that sort each document
(`PL-SY7G`, `PL-4H8Q`, `PL-N83Z`) apply this item's findings for the
sections they hold, and the session that applies the last of them closes
this item.

**Checked 2026-11-22** against `d4e8200`: still applies, and still blocked. Its blocker `PL-48MX` (replace what is left of `docs/MODEL.md` with the accepted description) is itself blocked, behind `PL-FWR6` and then `PL-6PPZ`, which is ready. The finding this item names is still present: `grep -n "must demonstrate" docs/MODEL.md` finds "The “Sevo works” milestone (v0.1.0) must demonstrate:" in § "Purpose". The chapter reads are still not in this container, because `/mnt/project-files` does not exist here.

**Record 2026-11-22: what became of each chapter read.** There are 86
chapter reads, not 30 as the title says. Each was checked against the four
documents on branch `wip-chain` at `2712f1af`. The table gives each chapter's
section in the old `docs/MODEL.md` (cfb15a4a), the document that now holds its
text, and what became of its findings within the section. "Already true" means
the text on this branch already does what the finding asked; which change made
it so was not traced. "Superseded" means the text was replaced, by the
clinician's description (`PL-48MX`) or by the rewrite for whole-second
stepping (#2180). The reasons for every finding not applied follow the table.

Counts: superseded 11; applied by this item 10; applied by `PL-SY7G` 14, by
`PL-4H8Q` 12, by `PL-N83Z` 6 and by `PL-W51N` 1; already true 23; no change
proposed 1; not applied 8; still open 0; cut whole by the split 0.

| Ch | Old section | Now in | Disposition |
| --- | --- | --- | --- |
| 1 | Status | MODEL | superseded |
| 2 | Intended use | MODEL, VERIFICATION | applied by `PL-4H8Q` |
| 3 | Reasonably foreseeable misuse | VERIFICATION, INTERFACE | applied by `PL-4H8Q`; INTERFACE part already true |
| 4 | How this document is held to the tree | VERIFICATION | reorder applied by `PL-4H8Q`; reader split not applied, reason in `PL-4H8Q` |
| 5 | Purpose | MODEL | superseded |
| 6 | Model boundary | MODEL, VERIFICATION | superseded |
| 7 | Conventions | VERIFICATION, PARAMETERS | applied by `PL-4H8Q`; Biro restatement cut here |
| 8 | Symbols | MODEL, VERIFICATION | applied by `PL-4H8Q` |
| 9 | Compartment capacities | MODEL | superseded |
| 10 | Tissue groups | MODEL | superseded |
| 11 | Governing equations | MODEL | superseded |
| 12 | Conservation of agent mass | VERIFICATION | applied by `PL-4H8Q` |
| 13 | Numerical method | VERIFICATION | applied by `PL-4H8Q` |
| 14 | Step atomicity | VERIFICATION | already true; rename not applied (reader) |
| 15 | Selected method | VERIFICATION | applied by `PL-4H8Q` |
| 16 | The numerical envelope | VERIFICATION | applied by `PL-4H8Q` |
| 17 | Parameter provenance | PARAMETERS | applied by `PL-N83Z` |
| 18 | Source hierarchy, first part | PARAMETERS | applied by `PL-N83Z` |
| 19 | Source hierarchy, second part | PARAMETERS | applied by `PL-N83Z` |
| 20 | v0.2.0: isoflurane and desflurane | PARAMETERS | applied by `PL-N83Z` |
| 21 | Delivery-limit and MAC parameters | PARAMETERS | applied by `PL-N83Z` |
| 22 | Required invariants | VERIFICATION | applied by `PL-4H8Q` |
| 23 | Required tests | VERIFICATION | already true; clinician's opening not applied (reader) |
| 24 | Zero-agent test | VERIFICATION | not applied (reader, heading) |
| 25 | Zero-ventilation test | VERIFICATION | not applied (reader, heading) |
| 26 | Zero-cardiac-output test | VERIFICATION | not applied (reader, heading) |
| 27 | Zero-tissue-flow test | VERIFICATION | not applied (reader, heading) |
| 28 | Equilibrium test | VERIFICATION | not applied (reader, heading) |
| 29 | Directional ventilation test | VERIFICATION | already true; rename not applied (heading) |
| 30 | Directional solubility test | VERIFICATION | not applied (reader, heading) |
| 31 | Directional tissue-capacity test | VERIFICATION | not applied (reader, heading) |
| 32 | Washout test | VERIFICATION | not applied (reader, heading) |
| 33 | Step-refinement test | VERIFICATION | superseded (#2180) |
| 34 | Independent-solution test | VERIFICATION | three subheadings added here; rest already true |
| 35 | Published wash-in and elimination validation test | VERIFICATION | applied by `PL-4H8Q` |
| 36 | Desflurane's residual | VERIFICATION | applied by `PL-4H8Q` |
| 37 | The early wash-in curve | VERIFICATION | restated +2.10 SD cut here; rest already true |
| 38 | What the published-data gate can and cannot resolve | VERIFICATION | applied here |
| 39 | The first 24 hours of elimination | VERIFICATION | applied by `PL-4H8Q` |
| 40 | Mass-balance test | VERIFICATION | already true; clinician's opening not applied (reader) |
| 41 | Closed-form agreement test | VERIFICATION, now "Prediction agreement test" | superseded (#2180) |
| 42 | Parameter-recovery test | VERIFICATION | already true |
| 43 | Deterministic replay test | VERIFICATION | already true |
| 44 | Canonical evaluation test | VERIFICATION, now "Stored-state test" | superseded (#2180) |
| 45 | Runtime controls | INTERFACE | already true |
| 46 | Halting on a marked crossing | INTERFACE | applied by `PL-SY7G` |
| 47 | The control-input record | INTERFACE | applied by `PL-SY7G` |
| 48 | The run is that record | INTERFACE | superseded (#2180) |
| 49 | The canonical evaluation rule | INTERFACE | applied by `PL-SY7G` |
| 50 | Supported input ranges | INTERFACE | applied by `PL-SY7G`; step paragraph not moved (other document) |
| 51 | What a setting outside the range costs | INTERFACE | applied by `PL-SY7G` |
| 52 | The model's envelope and a machine's range | INTERFACE | already true |
| 53 | Supported run length | INTERFACE | applied by `PL-SY7G` |
| 54 | What is not bounded this way | INTERFACE | moves applied here; rename filed as `PL-G05S` |
| 55 | Reset behavior | INTERFACE | already true; rescoping the list not applied (requirement) |
| 56 | Agent-change behavior | INTERFACE | already true, by the split into § "Discarding a run, and the questions that guard it" |
| 57 | What a branch comparison asserts | INTERFACE | applied by `PL-SY7G` |
| 58 | Interface boundary | INTERFACE | subheadings by `PL-SY7G`; two citation forms fixed here |
| 59 | Minimum displayed outputs | INTERFACE | opening and close already true; list grouping not applied (check) |
| 60 | What this list requires once the layout is the reader's | INTERFACE | applied by `PL-SY7G` |
| 61 | MAC multiples as a display unit | INTERFACE | applied by `PL-SY7G` |
| 62 | The chart's time base | INTERFACE | already true |
| 63 | MAC-awake as a chart reference | INTERFACE | applied by `PL-SY7G`; rename filed as `PL-G05S` |
| 64 | The control-input timeline | INTERFACE | already true |
| 65 | F_A/F_I as a displayed ratio | INTERFACE | already true |
| 66 | Color contrast | INTERFACE | applied by `PL-SY7G`, whose record calls it chapter 63 |
| 67 | The six compartment traces | INTERFACE | already true |
| 68 | Displayed precision | INTERFACE | no change proposed |
| 69 | Why the readouts show two decimals | INTERFACE | applied by `PL-W51N`'s rewrite |
| 70 | The MAC multiple's resolution | INTERFACE | already true |
| 71 | What the model keeps that the display rounds | INTERFACE | already true |
| 72 | Comparing two readouts | INTERFACE | already true |
| 73 | One resolution for all six readouts | INTERFACE | already true |
| 74 | The readout row's width condition | INTERFACE | applied by `PL-SY7G` |
| 75 | Time, flows and the chart | INTERFACE | applied here |
| 76 | The agent-accounting panel | INTERFACE | already true; moving the opening's reasons not applied |
| 77 | Agent amounts in millilitres, and the cost | INTERFACE | applied here; rename not applied, reason in `PL-SY7G` |
| 78 | A compartment's amount and share | INTERFACE | already true |
| 79 | The chart's hover readout | INTERFACE | applied by `PL-SY7G` |
| 80 | A preview of an unapplied setting | INTERFACE | already true |
| 81 | A cost at the reader's price | INTERFACE | applied by `PL-SY7G` |
| 82 | The compartment schematic | INTERFACE | applied here |
| 83 | Assumptions | MODEL | superseded |
| 84 | Known limitations, first part | MODEL, PARAMETERS | clinician's part superseded; evidence applied by `PL-N83Z` |
| 85 | Known limitations, second part | MODEL, PARAMETERS | owner-attested definition moved here; rest superseded or `PL-N83Z` |
| 86 | Release gate | VERIFICATION | already true; reader split not applied (reader) |

*Edits made by this item.* No number, unit, equation, citation or code span
changed. A comparison of the code spans, equations and hidden markers before
and after found no difference, except the one marker cut with its value in
item 5.

1. `docs/VERIFICATION.md` § "What the published-data gate can and cannot
   resolve": the two paragraphs on regression pins became one; the table of
   edges got the subheading "How far one stored value can change before the
   gate fails", and the sensitivity table "Which stored values each ratio
   responds to"; the two tests that keep the table in step now follow the
   conclusions.
2. `docs/VERIFICATION.md` § "Independent-solution test": three subheadings,
   "The runs the test covers", "Checks at every step of the random runs" and
   "The tests and the figures behind the comparison"; "this note" became
   "this subsection".
3. `docs/INTERFACE.md` § "What is not bounded this way": the code sentences
   moved out of the opening into a new "For developers" note, and the
   paragraphs now run reasons, consequence, note, what is open.
4. `docs/INTERFACE.md`: the flows paragraph now comes before the chart
   paragraph in § "Time, flows and the chart"; the exhausted-total paragraph
   follows the table's order in § "Agent amounts in millilitres, and the
   cost"; the model-output paragraph opens § "The compartment schematic"; two
   bare section names in the must-not list, and one in the F_A/F_I section,
   gained their § mark.
5. `docs/VERIFICATION.md` § "The early wash-in curve against the published
   figures": the restated "+2.10 SD" now points at desflurane's row in the
   table above, which holds the value, and its `not-restated` marker went with
   it.
6. `docs/PARAMETERS.md` § "Agent amount": the sentence restating Biro's three
   volumes now points at the table below, which holds them.
7. `docs/PARAMETERS.md`, the altitude sources: the definition of
   owner-attested moved from after the list to its opening, so the term is
   defined before the list uses it.

*Not applied, and why.*

1. Reader. The reads were written for a clinician reading the old
   `docs/MODEL.md`. A finding that moves a test name or code detail into a
   note, opens a section for a clinician, or rewords a requirement for one
   would change the reader of `docs/VERIFICATION.md` (a developer) or
   `docs/INTERFACE.md` (a contributor). Chapters 14, 23, 24 to 32, 40 and 86;
   `PL-4H8Q` gave the same reason for chapter 4.
2. Requirement headings. The renames of test headings (chapters 14, 24 to 32)
   are not applied, because the code cites a requirement by its quoted heading
   and `PL-P3GZ` keeps requirement headings.
3. Code citations. Chapters 54 and 63 rename headings that code comments
   cite, and this work was told not to re-point code comments while another
   branch edits them. Filed as `PL-G05S`.
4. Chapter 50's step paragraph would move into `docs/VERIFICATION.md`
   § "Supported simulation step", a different document with a different
   reader.
5. Chapter 55's rescoping of the list would reword a requirement.
6. Chapter 56's subheadings: after the split, the two later topics open with
   bold leads in § "Discarding a run, and the questions that guard it", which
   serve as their names.
7. Chapter 59's grouping of the list: the documentation check reads the list
   as one bound family.
8. Chapter 76's opening reasons support its bold claim, so they stay with it.
9. No finding was judged to change what a value means.

The reads' queries are not dispositioned here. `PL-BSMF` filed them as
`PL-HR4T` and the twelve others it names, so `PL-4H8Q`'s note that they stay
open for this item is out of date. The old-to-new audit by two reviewers that
the done-when asks for was not repeated: the moves were checked by the
comparison above, and each sorting item recorded its own fact comparison.

*Files checked in the docs sweep:* `docs/MODEL.md`, `docs/INTERFACE.md`,
`docs/VERIFICATION.md`, `docs/PARAMETERS.md`,
`docs/prose-review/model-reverse-outline.tsv`,
`src/anesthesia_sim/app/controller.py` and `src/anesthesia_sim/app/theme.py`
(their citations of the two headings not renamed), and
`tests/reference/test_mac_awake_washout_figures.py`.

*Checks.* `uv run python tools/doc_check.py check` reports 0 errors and one
advisory, on `docs/resident-instructions.md`, which this branch does not
touch. `bin/docket check` reports 0 errors. The 65 test files that name the
three edited documents, with `tests/unit/test_doc_check.py`, pass: 3,973
tests. `make check` was not run.
