---
id: PL-4H8Q
title: Sort the verification document by reader after the split: move or cut each paragraph the reverse outline gives another home, and apply the structure findings for its sections (stage 3 of the split PL-P3GZ decided)
priority: P2
effort: L
status: ready
classes: docs
feature: model-md-structure
touches: docs/VERIFICATION.md
blocked-by: PL-48MX
added: 2026-11-11
payoff: each paragraph of the document is for its reader, and none restates what a docstring, a test or an item already says
---

**Problem.** Sort the verification document by reader after the split: move or cut each paragraph the reverse outline gives another home, and apply the structure findings for its sections (stage 3 of the split PL-P3GZ decided)

**Why it matters.** The project owner decided on 2026-11-11 to split
`docs/MODEL.md` by reader (`PL-P3GZ`). Stage 1 moves whole sections word for
word, so the verification document starts with every paragraph its sections held, whoever the
paragraph is for. The reverse outline
(`docs/prose-review/model-reverse-outline.tsv`, `PL-9RLM`) gives each
paragraph a best home. Those sections hold 32,206 words.

**What to do.**

1. For each paragraph of the six verification sections that `PL-6PPZ` moves that the outline gives another home,
   have a reader confirm the label, then move the paragraph there. The
   labels are one model's judgement with no second rater. The outline's
   line numbers are those of `docs/MODEL.md` at `50af1a2e`.
2. Cut a paragraph that restates a docstring, a test or an item only after
   confirming that the home holds the fact. Decision history goes to the
   item that took the decision, and planned work to `ROADMAP.md`.
3. Apply, for these sections, the structure findings of `PL-YKKC` (the
   second reverse outline) and `PL-1VXY` (the chapter reads of 2026-11-05),
   and fix any pointer of `PL-52KB` (five broken section pointers) that is
   still broken in them. The session that applies the last of `PL-1VXY`'s
   findings across the three stage 3 items closes `PL-1VXY`.
4. Re-point each citation of a heading that changes.

**What it must not do.** Change no value, unit, equation, condition or
citation. Set no word target (`PL-J1ZM`). `PL-P3GZ` decided that no table is
generated and that requirements keep their headings and get no numbers. If
this work finds a table that neither the provenance check nor the named-test
check holds, reopen that call there.

**What ends with it.** The owner's hold of 2026-11-10 on within-section
restructuring ends for this document when this item closes. The hold also
covered copy editor runs, and the copy editor was removed on 2026-11-14
(`PL-GL45`).

**Done when.** Each paragraph of the verification document is for its reader or has moved to
its home, no paragraph restates a docstring, a test or an item, the
findings named in step 3 are applied for these sections, and `make check`
passes.

**Generator check.** Part of the fix for the cause that `PL-P3GZ` records:
the repository named no home but `docs/MODEL.md` for a test's description,
an interface requirement or a value's source history, so each change added
them there. No new head.

**Added 2026-11-20.** Write each requirement or claim in this document as the requirement, followed by the test that checks it. Where the document holds a parameter table, a test compares the table with its data file. History stays in the item (project owner, 2026-11-20, ratified, "Agree with recs", over leaving the form to each sorting item). `PL-WKKH` (the streamlining questions from the study of the one-shot rewrite) holds the measurements and the sources.

**Checked 2026-11-22** against `d4e8200`: still applies, and still blocked. Its blocker `PL-48MX` is itself blocked, behind `PL-FWR6` and then `PL-6PPZ` (move the six verification sections), which is ready and has not moved them, so the verification document this item sorts does not exist yet. The reverse outline it reads, `docs/prose-review/model-reverse-outline.tsv`, is still in the tree.

**Built 2026-11-22** on `wip-4h8q` from `65a4937b`. This document's reader is
a developer who changes the model's code or its tests. So its code names, test
names and reading records stay, and the "**For developers.**" labels mean
nothing here. Every label is removed, and each former note now sits in the
paragraph or section it serves. `.claude/rules/sources-and-docstrings.md`
gives such notes only to `docs/PARAMETERS.md` and `docs/INTERFACE.md`.

*Moved.* No paragraph moved to another document or to an item. A match of the
old text's paragraphs against the new text's finds 447 in their old order (72
of them reworded, mostly to drop the label or re-point a citation), 38 moved
within the document, 12 cut, 11 merged into or rebuilt as other paragraphs,
and three new: the opening paragraph on the last two sections and the hidden
markers, the opening of § "Required tests", and the opening of the hazard
table, rebuilt from two old paragraphs. The moves are these:

1. § "Conservation of agent mass": the compensated-summation paragraph now
   follows the paragraph that introduces the running totals. The former note
   became a paragraph on Higham's bound, and its other facts joined the
   paragraphs they concern.
2. § "Numerical method": the paragraph on cancelling transfer pairs now follows
   the requirements it meets. The reason for the all-or-nothing rule joined the
   rule.
3. The two paragraphs on a run that stops when a step drives an amount out of
   range moved from the step section to the end of § "Step atomicity".
4. § "Supported simulation step" is now a level-3 section under § "Numerical
   method". It opens with the step and why it is one second. Three
   subsections follow: "Control timing at the one-second step", "Playback, and
   when a control change acts" and "A compartment stepped on its own". The
   16% arithmetic now follows its claim.
5. § "The numerical envelope" has six subsections: "Every input's range",
   "The tests across the envelope", "The margin between 0.99 and 1",
   "Squarings, and why the limits were kept", "The mass-balance check at the
   hardest corners" and "Volumes outside the envelope". The mass-balance
   bound for the corners joined the corner table.
6. § "Required invariants" is now five short lists by kind: ranges, agent
   conservation, controls, zero flows and time steps. Equilibrium moved beside
   internal transfers.
7. The paragraph that says every required test but one is verification moved
   from § "Published wash-in and elimination validation test" to the opening
   of § "Required tests".
8. § "Desflurane's residual, and why the parameter file was not changed": the
   explanations of the table's rows now follow the table's order, and the
   paragraph that says the cause is not identified now closes them.
9. § "Notes for developers on the model description": the misuse paragraph
   opens § "What keeps a real patient's data out of a run". The 2% example
   follows the percent formula. In § "Symbols", each paragraph now follows
   the row or paragraph it explains.
10. § "How this document is held to the tree": the rules a reader relies on
    come first, and the rules for writers follow under a new subheading,
    "What the documentation check confirms, and what only a review finds".

*Cut*, each after confirming that its home states every fact in it:

1. The pointer from § "Conservation of agent mass" to `docs/MODEL.md`
   § "Low flow and the closed circuit": § "Circuit exhaust" already gives it.
2. The note's denominator sentence: the formula for the relative error, now
   naming `MINIMUM_RELATIVE_SCALE_L`. "Each total stays within a few units in
   the last place": the table and its reading.
3. "The step is undone in full, simulated time does not advance, and the run
   must stop": the first paragraph of § "Step atomicity".
4. "A run with identical initial state, settings and events must produce
   identical results": § "Deterministic replay test" and § "The
   reproducibility guarantee".
5. "At the hardest corners of the envelope, one step has a larger error bound
   than any calculation that a shipped run makes": the corner table and the
   bound beside it.
6. "The corners' one-second steps have errors of up to 1.3e-9": the corner
   table.
7. The note's "A settings record and the stepped system's dial setter both
   refuse a dial above 99%": the input table and "A dial above 99% is
   refused".
8. "Isoflurane is compared against both of its cohorts, in both directions":
   the two tables. "With rebreathing, the same run settles at 0.30 to 0.32":
   the earlier sentence "the simulated value at five minutes was 0.30 to
   0.32".
9. "*What follows if the bias is real.*": the end-tidal bullet that ends "So
   the measured 0.140 understates the true arterial ratio".
10. "**A mechanism that belongs to this model's circle system cannot explain a
    disagreement with a measurement made without one.**": the three bullets
    after it.
11. "**Two of the three questions about the published protocol are
    answered**": the paragraphs on the published apparatus, its 50 ml dead
    space and "Neither paper publishes a ventilation".
12. "So one candidate is left": the reworded paragraph that says the cause is
    not identified, and the one candidate it lists.
13. "The intertissue-diffusion note is where a reader of that tail is sent":
    the two pointers to `docs/MODEL.md` § "Intertissue diffusion: the missing
    fourth compartment".
14. "A learner can still set cardiac output or alveolar ventilation to a value
    measured in a real patient": `docs/MODEL.md` § "What the simulator is
    for" and the hazard table's row for a real patient's data.
15. "A caller cannot ask for a step of another length": § "Supported
    simulation step".
16. "The breathing circuit's quantities carry the subscript C": the rows for
    $`V_C`$ and $`M_C`$ in § "Symbols".
17. "Never shorten the "Fresh gas flow" label to its first line":
    `docs/INTERFACE.md` § "Minimum displayed outputs".

Merged into the paragraph they concern: the flow round trip (into § "Time"),
the check in `AgentUptakeSystem._write_state_vector` (into § "Concentrations"),
the repeated blood:gas sentence in the tissue-group notes, the class names and
`Fraction` from the envelope's note, and the first test's name in § "Step-refinement test".

*Outline labels I disagreed with.* The outline gives 413 rows in these
sections.

1. `code` (81 rows): all kept, because a developer is this document's reader.
2. `item record` (26 rows): kept, as the evidence for a stored value or a
   chosen limit.
3. `model description` (20 rows): kept where the paragraph states the rule the
   code keeps. `U0351` was cut (cut 4).
4. `cut` (40 rows): the marker-only rows stay, because the documentation check
   requires each marker. `U0249`, `U0351`, `U1486`, `U1492`, `U1494` and
   `U1495` were cut. `U0253`, `U0259`, `U0260` and `U1350` stay: the first
   explains the identity, the next two are its equations, and the last is the
   hazard table's reason. `U0328` and `U1397` describe text that no longer
   exists.
5. `interface requirements`, `U0386`: kept, because it says which code
   refuses a chart state at 1.

*Structure findings applied.*

1. `PL-YKKC` point 2: § "Supported simulation step" is a level-3 section with
   subheadings.
2. `PL-YKKC` point 3: the opening says what the hidden markers are and points
   at `docs/PARAMETERS.md` § "The provenance table, and the markers over
   restated values". § "Required tests" has an opening.
3. `PL-YKKC` point 4: the envelope's 0.99 paragraphs now stand under two
   subheadings. § "Selected method (as implemented)" and § "Concentrations"
   keep one-sentence pointers.
4. `PL-YKKC` point 5: no developer note is left mid-section.
5. `PL-1VXY` chapter reads: chapter 2 (the misuse paragraph moved, and the
   heading "This is an engineering bar" is renamed), chapters 3, 7, 8, 12, 13,
   15 and 16 (the moves above), chapter 22 (the grouped invariants), chapter 35
   (two cuts and the re-pointed caveat), chapter 36 (the circuit-wall bullet
   re-pointed, and the cuts) and chapter 39 (the intertissue pointers).
6. `PL-52KB`: none of its pointers is broken in these sections.

*Not applied, and why.* Naming a test for each invariant is `PL-8LDF`'s work.
Chapter 4's heading change and its split by a clinician reader do not apply to
a developer's document. The chapter reads' queries stay open for `PL-1VXY`.
Repeated figures that sit in a table and in its reading were left, because the
reading says what the figure means.

*Requirement and test.* The opening of § "Required tests" says that each
subsection states its requirement and then the test that checks it. The first
test of § "Step-refinement test" is now named in its list item.

*Headings.* "This is an engineering bar, not a regulatory status" is now
"Class C is an engineering bar, not a regulatory status". Only closed items
and `docs/prose-review/model-reverse-outline.tsv` cite the old name, and they
record `docs/MODEL.md` as it was, so none was changed. "Supported simulation
step" moved from level 4 to level 3. Ten subheadings were added. No bold lead
that was cut is cited anywhere.

*Pointers.* Six pointers to `docs/MODEL.md` § "Known limitations" now name
the subsection that holds the fact: "What the model does not represent",
"Absorption by the circuit", "The fat group's blood flow" and "Intertissue
diffusion: the missing fourth compartment". One left with cut 10. Two stay:
the pointer for missing metabolism, because that section's list states it, and
the one that names the whole section that
`tests/reference/test_known_limitations_figures.py` reads. `ROADMAP.md` § "Planned
milestones" is now cited for the decision not to model the circuit walls.

*Fact comparison.* `uv run python tools/model_rewrite.py lost --base 65a4937b`
lists 19 tokens held fewer times than at the base. A whitespace-blind search
of the four documents finds 18 still stated. One of them, the path
`docs/VERIFICATION.md`, is held nine fewer times, because citations inside
this document no longer name the document itself. The one now absent is the code expression
`max(initial + delivered, MINIMUM_RELATIVE_SCALE_L)`; the relative-error
formula states it, and now names `MINIMUM_RELATIVE_SCALE_L`. The tool lists
8 added tokens. Each is a restatement in a new opening or a list lead-in, and
none is a new fact.

*A statement corrected.* § "Symbols" said "$`F_a`$ is the only such symbol",
for a Code cell that starts with an em dash. The $`\Delta t`$ row also does.
The sentence now names both.

Files checked in the docs sweep: `docs/VERIFICATION.md`, `docs/MODEL.md`
(§ "What the simulator is for", § "Assumptions", § "Known limitations" and its
subsections), `docs/INTERFACE.md` § "Minimum displayed outputs",
`docs/PARAMETERS.md` § "The provenance table, and the markers over restated
values", `ROADMAP.md` § "Planned milestones", and the citations of
VERIFICATION headings in `src/`, `tests/`, `tools/`, `.claude/`,
`docs/items/`, `docs/prose-review/` and `subprojects/`.

*Checks.* `uv run python tools/doc_check.py check` reports 0 errors and one
advisory, on `docs/resident-instructions.md`, which this branch does not
touch. `bin/docket check` reports 0 errors. `tools/core_vocabulary_check.py`
and `tools/import_boundary_check.py` report 0 errors.
`uv run pytest -q tests/reference tests/unit/test_doc_check.py
tests/unit/test_import_boundary_check.py tests/unit/test_core_vocabulary_check.py`
passes 1646 tests. `make check` was not run here.
