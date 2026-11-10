---
id: PL-YKKC
title: A reverse outline of docs/MODEL.md (2026-11-10) found structural problems to weigh in the next structure pass: the model's own sections are about 11% of the document, several headings do not name what they hold, terms are used before they are defined, and developer notes sit mid-section or fill half of one
status: untriaged
feature: model-md-structure
added: 2026-11-10
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
