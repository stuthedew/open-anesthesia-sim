---
id: PL-SY7G
title: Sort the interface document by reader after the split: move or cut each paragraph the reverse outline gives another home, and apply the structure findings for its sections (stage 3 of the split PL-P3GZ decided)
priority: P2
effort: L
status: ready
classes: docs
feature: model-md-structure
touches: docs/INTERFACE.md
blocked-by: PL-48MX
added: 2026-11-11
payoff: each paragraph of the document is for its reader, and none restates what a docstring, a test or an item already says
---

**Problem.** Sort the interface document by reader after the split: move or cut each paragraph the reverse outline gives another home, and apply the structure findings for its sections (stage 3 of the split PL-P3GZ decided)

**Why it matters.** The project owner decided on 2026-11-11 to split
`docs/MODEL.md` by reader (`PL-P3GZ`). Stage 1 moves whole sections word for
word, so the interface document starts with every paragraph its sections held, whoever the
paragraph is for. The reverse outline
(`docs/prose-review/model-reverse-outline.tsv`, `PL-9RLM`) gives each
paragraph a best home. Those sections hold 59,940 words. § "Minimum displayed outputs" alone held 33,567 on 2026-11-10, of which the outline gives 1,856 to a model description.

**What to do.**

1. For each paragraph of the seven interface sections that `PL-CTXZ` moves that the outline gives another home,
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

**Done when.** Each paragraph of the interface document is for its reader or has moved to
its home, no paragraph restates a docstring, a test or an item, the
findings named in step 3 are applied for these sections, and `make check`
passes.

**Generator check.** Part of the fix for the cause that `PL-P3GZ` records:
the repository named no home but `docs/MODEL.md` for a test's description,
an interface requirement or a value's source history, so each change added
them there. No new head.

**Left for this item by `PL-CTXZ`, 2026-11-11.** Two things the move could
not finish, because it changed no word of the moved text beyond its section
pointers:

- The moved text still says "above", "below" and "in this document" about
  things that are now in `docs/MODEL.md`, where no section mark stands beside
  the words. A blind review pass found two, which `PL-CTXZ` fixed: the
  provenance table, and the reference measurements. Read the document for the
  rest.
- [superseded 2026-11-14: `PL-GL45` removed the copy editor and its
  instructions, so nothing is left to change] `.claude/agents/copy-editor.md`
  says that in `docs/MODEL.md` a note that opens "**For developers.**" serves
  the developer. `docs/INTERFACE.md` has such notes too. Say so there when the
  hold on copy editor runs ends for this document. A change to those
  instructions needs a run of the review's test set, as
  `docs/prose-review/README.md` says.

<!-- absent: .claude/agents/copy-editor.md -->

**Added 2026-11-20.** Write each requirement or claim in this document as the requirement, followed by the test that checks it. Where the document holds a parameter table, a test compares the table with its data file. History stays in the item (project owner, 2026-11-20, ratified, "Agree with recs", over leaving the form to each sorting item). `PL-WKKH` (the streamlining questions from the study of the one-shot rewrite) holds the measurements and the sources.

**Checked 2026-11-22** against `d4e8200`: still applies, and still blocked: `PL-48MX` (replace what is left of `docs/MODEL.md` with the accepted description) is itself still blocked. `docs/INTERFACE.md` exists, since `PL-CTXZ` moved its sections (#2109). `PL-5FMC` (#2181) then corrected what it says the code does, but that work changed facts and did not sort paragraphs by reader, so none of this item's four steps has been done.

**Built 2026-11-22** on `wip-sy7g` from `65a4937b`. A first pass over the
whole document, which is the seven sections `PL-CTXZ` moved and nothing else.
Each outline row was matched to today's text by its words. 694 of the 767 rows
for these sections match a paragraph; the other 73 are rows of the old
"The run is that record" and "The canonical evaluation rule", which the
whole-second stepping work (#2180) rewrote, so their labels no longer describe
any paragraph. This document's reader is a contributor who changes the
interface, a developer who needs each requirement, its reason and its test. So
most rows labelled `code` or `item record` stay, as in `PL-N83Z`. The pass is
not complete: "What is left" below lists what it did not do.

*Moved.* No paragraph moved to another document. Of the 746 paragraphs,
tables, markers and headings at the base, 702 are unchanged in text, and 694
of those are in their old order. Twelve paragraphs moved within the document:

1. In § "Color contrast, and the standard this interface is held to", six
   paragraphs left the note for developers for the body, beside the
   requirement each supports: the Understanding document's line-graph example
   (after the list of where the interface goes beyond AA), the gridline
   exemption's grounds and the refusal to darken the grey (after "The
   gridline grey is exempt"), the cost of supporting dark appearance (after
   "The window is always light"), and the alert color's rule for new elements
   with the unestablished IEC 60601-1-8 mapping (after the IEC paragraph). The
   focus-ring note joined the section's one note for developers.
2. In § "Why the readouts show two decimals", the note naming the
   one-SD tests moved from mid-section to the note that ends it.
3. In § "Halting on a marked crossing", the note on how a crossing is decided
   moved ahead of the new subheading "What a mark's row reports", because it
   is about halting.
4. In § "MAC multiples as a display unit", the three note paragraphs on the
   conversion, the two units and the stored 1 MAC now end the new subsection
   "What a MAC multiple means", and the rest end "The chart's fixed MAC axis".

*Cut*, 26 blocks (22 paragraphs, 3 tables and 1 marker that went with its
table), each after confirming that its home holds every fact in it:

1. The timeline note's "Capping the timeline would not bound memory use" and
   its measurements of timeline growth and grouping cost (ten entries per
   real second, 0.88 ms, 8.8 ms, 200 ms, three hours, 9 MB): `PL-1PSX`'s
   "Decided, 2026-09-14" paragraphs. The doc said 0.9 ms; the item says
   0.88 ms. Its first sentence, that the timeline grows with the settings
   changed and not with the run's length, joined "The timeline itself has no
   limit". A pointer to `AdjustmentGrouping` and `PL-1PSX` replaces the rest.
2. "Nothing marked enters a governing equation, opens a segment or moves a
   keyframe": the section's opening, "A run that halts at its marks computes
   exactly the values that an unmarked run computes".
3. The height band's 965 halts in ten minutes: the `HEIGHT_BAND` docstring in
   `core/rounding.py` (`PL-QVBR`). The note now points there.
4. "The flow maxima began as the interface sliders' maxima": the paragraph
   "The maxima for fresh gas flow, ventilation and cardiac output come from no
   source", `PL-0MLQ`, and § "What a setting outside the range costs" for
   exactness at any flow. Its example value, 10.01 L/min, is gone with it.
5. The page heights before the region was fixed (1087 px and 1505 px at
   1366 px wide, 2026-10-20): `PL-NNML`'s "Why it matters".
6. "Each drawn point is evaluated from the run's definition", in § "The
   chart's time base": a restatement of § "What the chart draws".
7. "Measuring text on the panel alone once hid a shortfall" (4.28:1 and
   3.98:1): `PL-X0RG`. The rule it led to stays in the body.
8. The hover's overlap table under the nearest-point rule, with its setup and
   its 83.3–95.3%, 43.8–81.4% and 75.4–99.9% figures: `PL-JVHL`'s "Measured
   2026-09-17".
9. The sixteen blocks that scored the five targeting rules and the scans
   behind the current rule, in § "Where more than one trace answers": the
   rule scores and the refused tie-break, `PL-JVHL`; the compartment
   contention table and the reach figures, `PL-0RZ0`; the mixed-instant
   table, the rejected alternative and the chosen rule's cost, `PL-1K9G`;
   the logarithmic axis, `PL-QYBW` option 3. The wash-in plot's "one set of
   drawn instants" is in the docstring of `nearest_wash_in_point`. A
   two-sentence pointer to the four items replaces them.

Sentences cut inside kept paragraphs: the second and third definitions of
trunk, branch and fork (in § "Reset behavior", § "Discarding a run" and
§ "What is compared"), "A branch is a run taken from another run" in the
preview's note, and the two sentences of the moved gridline paragraph that
repeated the body's reasons for the header line and the groove.

*Added*: one paragraph that says what § "Runtime controls" holds, a rewritten
opening for § "The control-input record" that names its three records, one
definition of trunk, branch and fork, three pointer paragraphs, and seven
headings (below).

*Outline labels I disagreed with.*

1. `code`: all kept. Most sit in a section's note for developers already. The
   long note in § "Supported input ranges" describes `core/`'s validation in
   detail that its docstrings also give, but confirming every fact was not
   done, so it stays (see "What is left").
2. `item record`: kept except the cuts above. Most of these rows are the
   reason for a requirement ("why a bookmark is reported passed", "why the
   ceiling is 3 ×MAC", "why the alert color does not follow the alarm
   convention"). A contributor needs the reason before changing what the
   interface shows. Measurements of rejected designs were cut.
3. `model description`: kept. The rows in § "Runtime controls", § "Supported
   input ranges", § "Supported run length", § "Neither run is a prediction for
   a patient" and § "MAC multiples as a display unit" state what the interface
   claims or the reason for a displayed limit. `PL-N83Z` already treats
   § "MAC multiples as a display unit" as a home.
4. `cut`: `U0661` ("So no divergence is left over to bound") stays, because it
   says why no bound is drawn for a learner. The marker-only rows stay. `U0605`
   was rewritten rather than cut.
5. `parameter source register`: kept, but the Katoh block in § "MAC-awake as a
   chart reference" belongs in `docs/PARAMETERS.md` (see "What is left").

*Structure findings applied.*

1. `PL-YKKC` point 2: § "Runtime controls" opens with what it holds.
   Branching, which sat under § "Each second has one stored state", has its
   own heading, § "What this requires of a branch", made from its bold lead.
   § "Interface boundary" has three subheadings: "What the chart draws" (made
   from its bold lead), "What the reader chooses: traces, window and playback
   rate", and "The code and tests behind the interface boundary".
2. `PL-YKKC` point 3: "canonical" no longer appears. The two sentences that
   used "keyframe" and "stretch" in § "Halting on a marked crossing" and
   § "The control-input timeline" before their definition were cut (cuts 1
   and 2).
3. `PL-YKKC` point 4: trunk, branch and fork are defined once, in § "What this
   requires of a branch". The definition says a branch is never taken from
   another branch, which `SimulationController` refuses.
4. `PL-YKKC` point 5: no note for developers sits mid-section now. In § "Time,
   flows and the chart" the first note was the reason for the clock's form,
   so it became body text. § "Color contrast" has one note.
5. Chapter 46: the subheading "What a mark's row reports".
6. Chapter 61: the subheadings "What a MAC multiple means" and "The chart's
   fixed MAC axis", each ending in its own note.
7. Chapter 63: the reasons in the contrast note moved to the body, as above.
8. `PL-52KB`: both of its pointers into this document resolve ("The chart's
   vertical range is set in MAC, and fixed" and "The axis is fixed rather than
   fitted"). The vague "(see the section above)" in § "The chart's time base"
   now names the first.

*Not applied, and why.* `PL-YKKC` point 5's long notes in § "Supported input
ranges" and § "What this list requires once the layout is the reader's" stay
long. The chapter reads' other proposals for subheadings (49, 53, 57, 60, 64,
66, 79, 81) and for renamed headings (51, 74, 77) were not checked one by
one: many concern text since rewritten, and a rename needs every citation
re-pointed. `PL-1VXY` stays open for them.

*Headings.* None renamed or removed. Seven added: "What this requires of a
branch" (level 3, from a bold lead), "What the chart draws" (level 3, from a
bold lead), "What the reader chooses: traces, window and playback rate", "The
code and tests behind the interface boundary", "What a mark's row reports",
"What a MAC multiple means" and "The chart's fixed MAC axis". Citations of
§ "Each second has one stored state" that meant branching now name § "What
this requires of a branch": in this document's § "Reset behavior",
`docs/ARCHITECTURE.md`, `ROADMAP.md` and
`tests/integration/controller/controller_support.py`.

*Statements that contradict the code, not changed.* Each says charts are
computed from the run's definition, but `SimulationController.drawn_window`
reads the stored states, as § "Each second has one stored state" says:

1. § "What the chart draws": "The model computes each point from the run's
   definition, which gives the run's state at any instant directly, by
   formula. No stored series of values lies behind a trace, so none can
   disagree with it."
2. § "The code and tests behind the interface boundary": "The controller
   evaluates them from the run's definition (`SimulationController.drawn_window`,
   `core/run_definition.py`). Keeping no stored samples of the run is a
   decision (project owner, 2026-09-05, recorded here when the sample store
   was deleted)."
3. The same note: "The stored state drawn at a control change is a keyframe,
   not one propagated from an earlier instant."

The cut sentence "the run itself holds one stretch and one keyframe for each
accepted change" was also out of date. Two docstrings in `app/controller.py`, near lines 1636 and 1749, say that
§ "What this requires of a branch" gives "two conditions", which it no longer
does.

*Fact comparison.* `tools/model_rewrite.py lost --base 65a4937b` lists 121
tokens held fewer times. A whitespace-blind search finds 56 of them still in
the four documents. The other 65 came from the cuts above, and each is in the
home named there: 63 in `PL-JVHL`, `PL-0RZ0`, `PL-1K9G`, `PL-QYBW`,
`PL-1PSX`, `PL-NNML`, `PL-X0RG` or the `HEIGHT_BAND` docstring, 0.9 ms as
0.88 ms in `PL-1PSX`, and 10.01 L/min as the example of cut 4. The tool lists
two added code spans (`AdjustmentGrouping`, `app/control_timeline.py`) and
one added number (1.4.11, in "Because SC 1.4.11 does not require"), none a new
fact.

*What is left.*

1. The note in § "Supported input ranges" (about 2,000 words on `core/`'s
   checked types, pickling, `__setattr__` and rollback) restates the
   docstrings of `core/checked_record.py`, `core/checked_number.py` and
   `core/supported_ranges.py`. Cut it after a fact-by-fact check.
2. The Katoh block in § "MAC-awake as a chart reference" (`U0990` to
   `U1000`, `U1006`, about 1,100 words) is a source reading for the stored
   MAC-awake values. `docs/PARAMETERS.md` names Katoh once. Moving it means
   moving its `derived:` markers and re-pointing what cites it here.
3. The requirement-then-test form from "Added 2026-11-20" was not audited
   requirement by requirement.
4. Of the 186 uses of "above", "below" and "this document", those with a
   section mark or "the section above" were checked. None of the rest pointed
   into `docs/MODEL.md` on a reading of their lines, but not every one was
   read.
5. The three statements above that contradict the code.

Files checked in the docs sweep: `docs/INTERFACE.md`, `docs/ARCHITECTURE.md`
(its two citations of the branch sections), `docs/VERIFICATION.md` (the
two citations of § "Each second has one stored state"), `ROADMAP.md`,
`docs/references/README.md` (its citations of § "What the chart draws"),
`src/anesthesia_sim/app/controller.py`, `src/anesthesia_sim/app/formatting.py`
(the axis comment), `src/anesthesia_sim/app/chart_frame.py`,
`src/anesthesia_sim/app/control_timeline.py`,
`src/anesthesia_sim/core/rounding.py`, `src/anesthesia_sim/core/stored_states.py`
and `tests/integration/controller/controller_support.py`.

*Checks.* `uv run python tools/doc_check.py check` reports 0 errors and one
advisory, on `docs/resident-instructions.md`, which this branch does not
touch. `bin/docket check` reports 0 errors and 2 advisories. The 37 test files
that name `docs/INTERFACE.md`, with `tests/unit/test_doc_check.py`, pass:
2,692 tests. `make check` was not run.
