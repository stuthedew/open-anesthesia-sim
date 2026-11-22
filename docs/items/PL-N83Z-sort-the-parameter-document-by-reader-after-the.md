---
id: PL-N83Z
title: Sort the parameter document by reader after the split: move or cut each paragraph the reverse outline gives another home, and apply the structure findings for its section (stage 3 of the split PL-P3GZ decided)
priority: P2
effort: M
status: done
classes: docs
feature: model-md-structure
touches: docs/PARAMETERS.md, docs/apparatus.md, tools/source_tier_counts.py
blocked-by: PL-48MX
added: 2026-11-11
closed: 2026-11-22
pr: 2232
payoff: each paragraph of the document is for its reader, and none restates what a docstring, a test or an item already says
verify: grep -qF '#### The stored values, by data file and key' docs/PARAMETERS.md
---

**Problem.** Sort the parameter document by reader after the split: move or cut each paragraph the reverse outline gives another home, and apply the structure findings for its section (stage 3 of the split PL-P3GZ decided)

**Why it matters.** The project owner decided on 2026-11-11 to split
`docs/MODEL.md` by reader (`PL-P3GZ`). Stage 1 moves whole sections word for
word, so the parameter document starts with every paragraph its sections held, whoever the
paragraph is for. The reverse outline
(`docs/prose-review/model-reverse-outline.tsv`, `PL-9RLM`) gives each
paragraph a best home. That section holds 13,176 words.

**What to do.**

1. For each paragraph of § "Parameter provenance", which `PL-FWR6` moves that the outline gives another home,
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

**Done when.** Each paragraph of the parameter document is for its reader or has moved to
its home, no paragraph restates a docstring, a test or an item, the
findings named in step 3 are applied for these sections, and `make check`
passes.

**Generator check.** Part of the fix for the cause that `PL-P3GZ` records:
the repository named no home but `docs/MODEL.md` for a test's description,
an interface requirement or a value's source history, so each change added
them there. No new head.

**Added 2026-11-20.** Write each requirement or claim in this document as the requirement, followed by the test that checks it. Where the document holds a parameter table, a test compares the table with its data file. History stays in the item (project owner, 2026-11-20, ratified, "Agree with recs", over leaving the form to each sorting item). `PL-WKKH` (the streamlining questions from the study of the one-shot rewrite) holds the measurements and the sources.

**Checked 2026-11-22** against `d4e8200`: still applies and is still blocked. Its blocker `PL-48MX` (stage 2 of the split) is itself still blocked, because neither stage 1 move has merged: the move of § "Parameter provenance" and the move of the verification sections. No parameter document exists under `docs/`, and § "Parameter provenance" is still in `docs/MODEL.md`. It now holds 13,403 words by `wc -w`, not 13,176.

**Built 2026-11-22** on `wip-n83z` from `13a8bb23`. A second reading of every
outline row for `docs/PARAMETERS.md`, with each row matched to today's text by
its words. This document's reader is a developer, or a clinician checking a
stored value against its source, so its developer material and its reading
records belong here. That changed the disposition of most rows the outline
labelled `code` or `item record`.

*Moved.* No paragraph moved to another document. Every model-description fact
that left this document was already stated in `docs/MODEL.md`, so it was cut
instead (below). No paragraph moved to an item file either, because each item
that took a decision already held its history. A match of the old text's
paragraphs against the new text's finds 164 paragraphs in their old order (31
of them reworded, mostly to re-point a citation), 31 moved within the
document, 16 cut, one merged into another developer note, and 7 new: five
added sentences or pointers and two former list items. The moves are these:

1. The developer paragraphs `U0482`, `U0483` and `U0527` to `U0531` moved from
   mid-section to the "**For developers.**" note that ends their subsection.
   The patient's data-file path joined the patient's weight and flow-fraction
   checks in one note.
2. The other moves put each paragraph where its reader needs it. The
   full-text and republication rules (`U0448`, `U0449`) now follow the tier
   list, ahead of the adoption rule. The provenance table and its introduction (`U0502` to `U0504`) now
   follow the counts. The notes on the table's rows now follow it, grouped by
   the table's order: blood:gas (`U0459`, `U0460`), tissue:blood (`U0519` to
   `U0526`), the reference patient (`U0462`, `U0463`, `U0505` to `U0507`), the
   source chain, the cardiac-output relation (`U0491` to `U0495`), the venous
   pool, and the machine rows. The 100 kg paragraph (`U0490`) now precedes the
   ICRP row comparison that relies on it. "The stored MAC carries clinical
   weight" (`U0562`) now follows the paragraph on the MAC's two uses.

*Cut*, sixteen outline units, each after confirming that its destination holds
every fact:

1. `U0450`, the data-file fields: § "What the data-file format requires of a
   `sources` entry".
2. `U0453`, citing Gas Man as a measurement: § "Republication does not promote
   a value between tiers" and the tier-3 definition.
3. `U0461`, the patient adopts no primary source: reason 1 in § "Source
   hierarchy", § "Where this project stands", the machine-rows paragraph and
   the format section.
4. `U0468`, the Workbook pages promote nothing: the republication paragraph,
   the "Nothing is promoted" paragraph and § "The venous pool".
5. `U0486`, Mapleson's fixed-fraction assumption: `docs/MODEL.md` § "Blood
   flow to the tissue groups" quotes it word for word. A pointer replaces it.
6. `U0489`, Mapleson is not the Workbook's source: the Workbook-attribution
   paragraph and the paragraph on Mapleson 1963.
7. `U0501`, Gas Man's 1.0 L is not an arterial pool: `PL-8ZJQ`'s brief, in its
   "Read at the source 2026-09-07" paragraph, holds the 0.98 L, the 4.9 L, the
   799 ml, the 15.4% and 1222/6480 = 11.3 s.
8. `U0518`, Candries and Hoffmann's flow ranges: `docs/machine-survey.md`
   (the `PL-NM7X` paragraph) holds the ranges and the argument, and
   `docs/MODEL.md` § "Gas Man in patients" holds Candries' 28 patients.
9. `U0537`, the blood:gas values compare because they share one table: the
   opening of § "v0.2.0: isoflurane and desflurane" and § "Where this project
   stands".
10. `U0557`, the two vaporizer designs: `docs/MODEL.md` § "The agents". The
    Dosch and Tharp source note now points there.
11. `U0559` to `U0561`, what the model does not do with MAC and why the display
    shows ×MAC: `docs/MODEL.md` § "MAC multiples" and § "The agents",
    `docs/INTERFACE.md` § "MAC multiples as a display unit", and the developer
    note under § "The maximum delivered concentration", which names the two
    places `core/` reads the MAC.
12. `U0577`, the circuit and the dial read one number: the developer note
    above it.
13. `U0100`, the 5.8 % overstatement: `docs/MODEL.md` § "Units and symbols".
14. `U1613`, a learner can move cardiac output: `docs/MODEL.md` § "Cardiac
    output and flow distribution are fixed", and the developer note naming the
    directional checks.

Sentences cut for restating their own bold opening: "Only the recorded source
and grade changed. No number did." and "A reader should take the table as
evidence that the division is the right operation". "These were two separate
decisions" is cut because `PL-FN5F`'s title states both decisions. The
data-file format's version history is cut because `PL-1JDD` (version 2),
`PL-9LXK` (version 3) and `PL-KZ99` (version 4) hold it. The current versions
stay.

*Outline labels I disagreed with.*

1. `code`: all kept except `U0450`. A developer who changes a stored
   value is this document's reader, so the data-file format, the checks and
   the tests stay, each in a section-end developer note. The marker and
   format sections stay too. `doc_check.py`'s docstrings explain how the check
   works, and these sections tell the writer of this document what to do.
2. `item record`: all kept except `U0501`. The reading records give
   the route and the depth that `.claude/rules/citing-sources.md` requires in
   the note itself. The source-chain findings are the evidence a clinician
   needs to check a value against its source. The reasons a value was chosen
   are what this document says it holds. A decision tag that names what the
   value was chosen over stays, as `CLAUDE.md` asks.
3. `model description`: kept where the paragraph explains a stored value or
   qualifies a table row (`U0098`, `U0099`, `U0505`, `U0507`, `U0515`,
   `U0517`, `U0533`, `U0534`, `U0538`, `U0553`, `U0554`, `U0558`, `U0562`).
   `U0564` to `U0566`, the Mapleson table and the 22%, stay because
   `docs/INTERFACE.md`, `tests/unit/test_parameters.py` and the three agent
   files cite them in this document. `U1632` stays because `docs/MODEL.md`
   does not hold its PET and washout readings. `U0099` stays because
   `docs/MODEL.md` does not state its mass-balance and 37 °C claims.
4. `verification and validation report`: `U0500`, `U0520` to `U0525` and
   `U0550` kept. They give the cost of a parameter choice and check derived
   values against a published table, which is this reader's job.
5. `cut`: the thirteen marker-only units stay, because the documentation check
   requires each marker. `U0498` stays as the single statement that nothing is
   promoted, as the 2026-11-05 chapter read of § "Source hierarchy" proposes.
   `U1647` stays because it holds the only citation of IAPWS-95.
6. `interface requirements`, `U0555`: kept with its tests, because it is the
   requirement on the stored maximum.

*Structure findings applied.*

1. `PL-YKKC` point 3: the introduction now says what the hidden markers are
   and points at the section that explains them, ahead of the first marker.
2. `PL-YKKC` point 5: every subsection of § "Parameter provenance" now ends
   in its developer note, and none sits mid-section.
3. `PL-YKKC` point 2: § "Source hierarchy" now covers only the hierarchy.
   § "Where each stored value comes from" is now a level-3 section with
   subheadings.
4. Chapter 17: the parameter list names § "Source hierarchy" instead of "the
   hierarchy below", and a paragraph says which checks enforce which
   requirements.
5. Chapter 18: the subheadings it proposes, with the bold phrase "Where this
   project stands" made a heading. The full-text and republication rules now
   follow the tier list. The bold opener "The lineage is Lowe and Ernst's, not
   Mapleson's", which the Mapleson finding contradicts, now reads "The
   Workbook attributes the values to Lowe and Ernst 1981". The 100 kg
   paragraph now precedes the row comparison, and the forward pointers now
   name their section.
6. Chapter 19: the table has its own subsection after the counts, and the row
   notes follow the table's order. The two machine-row list items are now
   paragraphs. The circuit-volume ruling names `PL-4YY1`, and the Candries and
   Hoffmann paragraph is cut.
7. Chapter 20: the lead-in "Two further points" is cut and its two bullets are
   paragraphs. The package-insert credit sits beside its resolution. The
   subheadings "Where the tissue:gas coefficients come from" and "Why the
   stored values were kept" are added.
8. Chapter 21: the subheadings "The maximum delivered concentration" and "The
   stored MAC" are added, each with its own developer note. The clinical
   weight follows the two uses.

*Not applied, and why.* Chapter 18's proposals to move the source chain to
`docs/references/` and to reorder it by stored value were not applied.
`.claude/rules/sources-and-docstrings.md` makes this document the home of a
value's source and its evidence, and the reorder would rewrite about 5,000
words of evidence. The merges of repeated figures were not applied either:
4.84 L/min, 64.0%, "reference 26 has no flows", the circuit time constants and
the Targ comparison. Chapter 19's question of where the marker rules belong is
the owner's. Chapter 21's proposal to move the reasons for keeping the stored
MACs into the developer note was not applied, because those reasons are this
document's content. The evidence section keeps its developer notes between
paragraphs. Its chapter reads (84 and 85) were not read in this session, and
the documentation check ties each numeric paragraph to the developer note
below it. The chapter reads' queries are queries, not structure, and stay
open for `PL-1VXY`.

*Requirement and test.* Each requirement in this document's developer notes
now names its test. The refusal of a dial above the vaporizer maximum names
`test_rejects_construction_above_the_vaporizer_maximum` and
`test_rejects_delivered_concentration_above_the_vaporizer_maximum`, and zero
names `test_accepts_a_delivered_concentration_of_zero`. The MAC check names
`test_rejects_mac_percent_exceeding_max_delivered_concentration_percent`. The
flow-fraction tolerance names
`test_the_perfusion_allowance_admits_rounding_and_refuses_a_transcription_error`.
The three rules for a `sources` entry say which a check enforces and which a
reviewer checks.

*Headings.* No heading was renamed. "Where each stored value comes from"
moved from level 4 to level 3. Thirteen subheadings were added. The counts
left § "Source hierarchy", so three citations of the counts now name § "Where
this project stands": one in this document's format section, one in
`tools/source_tier_counts.py` and one in `docs/apparatus.md`. The format
section's citation of the provenance table now names § "Where each stored
value comes from".

*Pointers.* Fourteen pointers to `docs/MODEL.md` § "Known limitations", to
§ "Tissue groups", to "Conservation of agent mass" or to
`docs/VERIFICATION.md` § "How this document is held to the tree" now name the
section that holds the fact. Two pointers to § "Known limitations" stay,
because they name the whole section, and three left with cut paragraphs. Two
examples: the Gas Man patient figures now point to § "Gas Man in patients",
and the 4.84 L/min figure to § "The reference adult". `PL-52KB`'s one pointer
in this document is not broken: the full Yasuda, Targ and Eger citation is in
`docs/VERIFICATION.md` § "Desflurane's residual, and why the parameter file
was not changed".

*Fact comparison.* `tools/model_rewrite.py lost --base 13a8bb23` lists 47
tokens held fewer times than at the base. A whitespace-blind search finds 44
of them still stated in the four documents. The other three, 0.98 L, 4.9 L and
11.3 s, came from `U0501` and are in `PL-8ZJQ`'s brief. The tool also lists
five added test names and three added test-file paths, from the
requirement-and-test change, and two more mentions of `sources`, from the
sentences that say which rules for a `sources` entry a check enforces. It
lists three added numbers: one repeated `derived:` marker for
90 s, one added `provenance:` marker for the 6.0 L circuit, and "1981" in the
new bold opener. None of these is a new fact.

Files checked in the docs sweep: `docs/PARAMETERS.md`, `docs/MODEL.md`
(§ "Parameters: values and sources", § "MAC multiples", § "Units and
symbols", § "Blood flow to the tissue groups" and the known-limitations
subsections), `docs/INTERFACE.md` § "MAC multiples as a display unit",
`docs/VERIFICATION.md` § "Desflurane's residual, and why the parameter file
was not changed", `docs/machine-survey.md`, `docs/machine-abstraction.md`,
`docs/references/README.md`, `docs/apparatus.md` and
`tools/source_tier_counts.py`.

*Checks.* `uv run python tools/doc_check.py check` reports 0 errors and one
advisory, on `docs/resident-instructions.md`, which this branch does not
touch. `make check` passes: 12,240 tests passed and 3 were skipped, and
coverage of `core/` is 100%.

*Replayed 2026-11-22* onto `PL-48MX`'s final commit, after its two blind
reviews. The one conflict was in `docs/PARAMETERS.md`. This branch's text was
kept, and each of `PL-48MX`'s later fixes to the same lines was applied to it
where the line survives. Most of those fixes re-pointed a citation that this
branch had already re-pointed the same way. The cardiac-output paragraph's
`provenance:` marker was added again.

*Subheadings in § "The evidence behind the known limitations".* The second
blind review of `PL-48MX` found passages there that read as the end of a
section they no longer follow. The section now has nine subheadings. Seven
take the name of the `docs/MODEL.md` limitation whose evidence they hold, in
that document's order. "Desflurane's washout through the circle system" holds
the note on the four tests behind `docs/MODEL.md` § "Elimination at five
minutes: does not agree", and "The tests and code behind this section" holds
the two notes that close it. Two pointers that said "the note below" and "the
note above" now name § "The fat group's blood flow". Each citation in this
document of a `docs/MODEL.md` section with one of these names already named
`docs/MODEL.md`, so none now resolves to the new heading by mistake.

*`PL-XLDN` closes here.* Its sentence, "which is the second of the three
rules below", was in `U0461`, which this branch cuts (cut 3 above). No
sentence in the document points at the three rules by position.
