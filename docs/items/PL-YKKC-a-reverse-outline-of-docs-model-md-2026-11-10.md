---
id: PL-YKKC
title: A reverse outline of docs/MODEL.md (2026-11-10) found structural problems to weigh in the next structure pass: the model's own sections are about 11% of the document, several headings do not name what they hold, terms are used before they are defined, and developer notes sit mid-section or fill half of one
priority: P3
effort: M
status: done
classes: docs
feature: model-md-structure
milestone: v0.6.20
touches: docs/MODEL.md
blocked-by: PL-1VXY
added: 2026-11-10
closed: 2026-11-22
pr: 2235
payoff: the replaced model document is checked for the structural problems the old one had, so they are not carried over
verify: grep -qF 'Record 2026-11-22: the five points checked against the split documents' docs/items/PL-YKKC-a-reverse-outline-of-docs-model-md-2026-11-10.md
---

**Problem.** A reverse outline of docs/MODEL.md (2026-11-10) found structural problems to weigh in the next structure pass: the model's own sections are about 11% of the document, several headings do not name what they hold, terms are used before they are defined, and developer notes sit mid-section or fill half of one

**What was done.** On 2026-11-10 a session made an editors' reverse outline of
`docs/MODEL.md` at `main` `f54250086`. It followed King CL, "Reverse
outlining: a method for effective revision of document structure", IEEE Trans
Prof Commun 2012;55(3):254-261, doi:10.1109/TPC.2012.2207838, with the
"says / does" descriptive outline credited to Bruffee. Ten subagents each
outlined one part. The outline itself, 1,506 paragraph entries, lived in that
session's scratchpad and is not kept. This brief keeps the assessment. Findings
marked *verified* were checked against the text. The rest are a subagent's
reading and were not checked.

**Overlap.** The copy editor's structure read of 2026-11-05 covers some of the
same ground. `PL-BSMF` applied its outline read, and `PL-1VXY` holds its
within-section findings. Check each point below against `PL-1VXY` before acting
on it.

A second reverse outline was made the same day in another session, on branch
`claude/elegant-babbage-m7igyw` (pull request #2088). Its items share this
item's feature: `PL-9RLM` commits that outline as
`docs/prose-review/model-reverse-outline.tsv`, `PL-B07T` drafts a clinician's
model description from it, and `PL-P3GZ` asks whether to split
`docs/MODEL.md` by reader. Point 5 below overlaps `PL-P3GZ`, so decide that
question first.

**That outline takes precedence** (project owner, 2026-11-10: the other session
runs a more capable model, so defer to it where appropriate). Treat each point
below as a second reading to check against that outline. Where the two
disagree, that outline wins. Where it already covers a point, drop the point
here.

**Findings, by consequence.**

1. **Proportion** (verified by counting lines per `##` section). Model
   boundary through Conservation of agent mass, the equations and what they
   rest on, is about 11% of the document. Minimum displayed outputs is 26.7%.
   Required tests is 13.5%, and its "Published wash-in and elimination
   validation test" subsection alone is 8.8%. Runtime controls is 12.9%,
   Parameter provenance 9.9% and Known limitations 7.9%. A clinician looking
   for the equations behind a value finds them in about one-ninth of the text.
   Inside Governing equations, Arterial blood, Tissue uptake and return, and
   Venous blood are short next to the closed-circuit material under Breathing
   circuit.
2. **Headings that do not name what they hold.**
   - Known limitations has no subheadings over about 1,000 lines (verified):
     a 41-item list, then about 20 untitled essays.
   - Runtime controls is mostly marks, halts, the run record, the evaluation
     paths, branching and input limits. Only its opening paragraphs are about
     the four controls.
   - Branching sits under "The canonical evaluation rule".
   - "Supported simulation step" sits under "Selected method (as
     implemented)", though it is about the step's limits and playback timing.
   - Interface boundary is mostly chart sampling and playback.
   - Purpose holds the v0.1.0 milestone checklist (verified).
3. **Terms used before they are defined.**
   - "Canonical", "stretch" and "keyframe" are used in § "Halting on a marked
     crossing" and § "The control-input timeline", before the subsections that
     define them.
   - The hidden-marker vocabulary is used in § "How this document is held to
     the tree" before § "The provenance table, and the markers over restated
     values" introduces it.
   - Required tests has no opening paragraph. The paragraph that frames it,
     saying every test above is verification and none validates, opens
     § "Published wash-in and elimination validation test".
4. **Restatement.**
   - The closed-circuit point appears about six times across the boundary,
     circuit and mass-balance sections.
   - F_a ≡ F_A appears four times.
   - The 0.99 fraction limit is argued five times in Numerical method.
   - Trunk, branch and fork are defined three times, in Reset behavior,
     Discarding a run, and What a branch comparison asserts.
5. **The two readers mixed.**
   - Developer notes sit mid-section in Numerical method, Parameter provenance
     and Displayed precision.
   - Developer notes fill half or more of these subsections: Supported
     simulation step, The run is that record, Supported input ranges, What this
     list requires once the layout is the reader's, Color contrast, and
     Independent-solution test.
   - Clinician-facing reasons sit inside developer notes in The numerical
     envelope and Supported input ranges.

**Withdrawn after checking.** The outline flagged § citations of "What this
requires of a branch" as pointing at a non-heading. That paragraph is a
bold-led paragraph, which the doc check treats as a citable target (see
`PL-97S1`), so it is not a defect. The stale disclaimer paragraph it found is
already `PL-DQD8`, and the misdirected "rules below" pointer is `PL-XLDN`.

**Why it matters.** Each point that is still true after `docs/MODEL.md` is replaced makes the model harder for a clinician to find and follow: the equations behind a value sit in a small share of the text, and terms appear before their definitions.

**Done when.** After `PL-48MX` replaces `docs/MODEL.md`, each of the five points is checked against the new documents and against the committed outline (`docs/prose-review/model-reverse-outline.tsv`, `PL-9RLM`). Each point still true is fixed or filed as an item, and the result is recorded here.

**Blocked on the replacement of `docs/MODEL.md`.** The owner decided on 2026-11-11 to split `docs/MODEL.md` by reader (`PL-P3GZ`). `PL-48MX` replaces what is left of it, so most of the text these points describe will move or go.

**Generator check.** `PL-P3GZ` found the cause: an instance of the fact that `PL-J1ZM` states, that no rule says what a reader can do without.

[superseded 2026-11-22] **Checked 2026-11-22** against `d4e8200`: still applied, and was still blocked on `PL-48MX`, which was then open behind two earlier stages of the split of `docs/MODEL.md`. Part of the outline is out of date. #2109 (`PL-CTXZ`) moved Runtime controls, Interface boundary and Minimum displayed outputs to `docs/INTERFACE.md`, so the points about those sections now concern that document. By `##` headings, the sections from Model boundary to Conservation of agent mass are now about 20% of the 7,044-line `docs/MODEL.md`, not 11%. Required tests is about 24%, Parameter provenance 18% and Known limitations 15%. The committed outline that the done-when names exists at `docs/prose-review/model-reverse-outline.tsv` (`PL-9RLM` is done).

**Record 2026-11-22: the five points checked against the split documents.**
Checked on branch `wip-chain` after `PL-1VXY`'s commit, against
`docs/MODEL.md`, `docs/INTERFACE.md`, `docs/VERIFICATION.md`,
`docs/PARAMETERS.md` and `docs/prose-review/model-reverse-outline.tsv`. None
of the five still holds as a structural problem, so nothing was fixed or
filed under this item.

1. Proportion: no longer holds. The new `docs/MODEL.md` (2,014 lines) holds
   only the model. By `##` section, Equations is 11.8%, What the model
   represents 5.2%, Parameters 16.2% and Known limitations 18.0%. The interface
   and test material that filled the old document is in `docs/INTERFACE.md`
   and `docs/VERIFICATION.md`. The breathing circuit is still the longest
   subsection of Equations, because it explains the fresh gas flow label and
   the circuit volume; it no longer carries the closed-circuit material.
2. Headings: no longer holds. Known limitations in `docs/MODEL.md` has 13
   subheadings. Runtime controls in `docs/INTERFACE.md` has an opening about
   the controls (`PL-SY7G`). Branching has its own § "What this requires of a
   branch". "Supported simulation step" in `docs/VERIFICATION.md` has its own
   subheadings (`PL-4H8Q`). Interface boundary has subheadings, with its code
   in § "The code and tests behind the interface boundary". The v0.1.0
   milestone text is gone from `docs/MODEL.md`.
3. Terms before definitions: holds no longer, with one residue that is not
   structural. "Canonical" no longer appears in `docs/INTERFACE.md`, and
   "stretch" is defined where it is first used. Both `docs/VERIFICATION.md`
   and `docs/PARAMETERS.md` introduce the hidden markers in their opening
   paragraphs. § "Required tests" now has an opening that says each test is
   verification except the published-data test. The residue is "keyframe" in
   the code note of `docs/INTERFACE.md` § "Interface boundary": "The stored
   state drawn at a control change is a keyframe, not one propagated from an
   earlier instant." It is one of the three statements that `PL-SY7G`
   recorded as contradicting the code, which is a factual correction, not a
   structural one. No item on this branch holds those three statements yet;
   `PL-SY7G` says they are being filed separately.
4. Restatement: no longer holds. F_a ≡ F_A appears in `docs/MODEL.md` at its
   definition, in the symbol table and in the reason for the display, and
   `docs/INTERFACE.md` cites `docs/MODEL.md` for it. The closed circuit is one
   list item and one section in `docs/MODEL.md`, with the code note in
   `docs/VERIFICATION.md`. `PL-4H8Q` grouped the 0.99 limit's arguments.
   Trunk, branch and fork are defined once in `docs/INTERFACE.md`
   (`PL-SY7G`).
5. Two readers mixed: no longer holds. The split gave each document one
   reader (`PL-P3GZ`). `docs/VERIFICATION.md` is a developer's document with
   no developer labels (`PL-4H8Q`). `docs/PARAMETERS.md`'s notes close their
   subsections (`PL-N83Z`). The long note in § "Supported input ranges"
   was cut to one paragraph of pointers to the code (`PL-SY7G`). The note
   under "What this list requires once the layout is the reader's" is
   about a third of its section, in a document whose reader is a contributor.

The committed outline records `docs/MODEL.md` at `50af1a2e`, before the
split, and the three sorting items dispositioned its rows. It stays as the
record of that text.

*Files checked:* `docs/MODEL.md`, `docs/INTERFACE.md`,
`docs/VERIFICATION.md`, `docs/PARAMETERS.md` and
`docs/prose-review/model-reverse-outline.tsv`.
