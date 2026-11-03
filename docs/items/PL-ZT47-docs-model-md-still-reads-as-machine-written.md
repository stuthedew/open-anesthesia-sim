---
id: PL-ZT47
title: docs/MODEL.md still reads as machine-written after PL-BZR4's rewrite: tautological asides, 'X, not Y' and 'rather than' contrasts, and narration about its own provenance; the plain-writing rule names none of these patterns, and the close-out prose review reads only .py files, so MODEL.md's 2,348 lines added since were never reviewed
priority: P2
effort: M
status: done
classes: docs, infra
feature: prose-quality
touches: .claude/rules/plain-writing.md, .claude/skills/docket/modes/close-out.md, docs/resident-instructions.md, docs/apparatus.md, docket.toml, tools/new_prose.py, tools/model_rewrite.py, tests/unit/test_new_prose.py, tests/unit/test_model_rewrite.py
added: 2026-11-02
closed: 2026-11-02
pr: 1943
payoff: every later change to the model specification gets the same plain-prose review as a docstring, and each section rewrite can show the reader what it removed
verify: grep -qF 'A table cell or paragraph that has grown into an essay' .claude/rules/plain-writing.md && uv run pytest -q -p no:cacheprovider tests/unit/test_model_rewrite.py tests/unit/test_new_prose.py
reenters: PL-PRCS
---

**Problem.** docs/MODEL.md still reads as machine-written after PL-BZR4's rewrite: tautological asides, 'X, not Y' and 'rather than' contrasts, and narration about its own provenance; the plain-writing rule names none of these patterns, and the close-out prose review reads only .py files, so MODEL.md's 2,348 lines added since were never reviewed

**The owner's reading (2026-11-02).** The document "just reads like the worst
kind of AI slop writing in terms of phrasing". The example given was line 395,
which `PL-BZR4`'s own rewrite (#1808, 2026-10-25) wrote: "The naming is
Hendrickx and De Wolf's, which is the field's naming."

**What was measured on 2026-11-02, at `main` 4007ad8e and later.**

- The file is 13,640 lines and about 140,800 words. It was 10,931 lines before
  `PL-BZR4` and 11,532 after it.
- 36 commits have changed it since `PL-BZR4` merged, adding 2,348 lines and
  removing 240. None of those lines passed a prose review, because
  `tools/new_prose.py` keeps only `.py` files.
- Counts of phrases that mark the style the owner objects to: "rather than"
  396, "That is" 238, ", not " 233, "is what" 76, "This is" 60, "so that" 48,
  ", which is the" 47, "deliberately" 37, "is recorded" 33, "the project
  owner" 28. A count is not a verdict, since many of these uses are fine.
- 439 lines cite an item id (489 ids in all). Much of the document narrates
  how a decision was reached and who supplied what, which is audit trail for
  sessions rather than specification for a clinician.

**Why the existing rule did not prevent it.** `.claude/rules/plain-writing.md`
targets compressed wording: dropped small words, private senses, stacked
clauses. `PL-8ZTQ` measured that as the main defect, and `PL-BZR4` fixed for
it. The patterns here are a different failure, and the rule names none of
them:

1. Tautological asides that restate the clause they sit in.
2. Reflexive contrast ("X, not Y", "rather than Z") where nobody claimed Z.
3. Narration about the document itself: "is recorded at that depth", "the
   pages above are what the citation is being used for".
4. Defensive scope statements that say what a passage does not rely on.
5. A table cell or paragraph that has grown into an essay. Prose ordinals
   ("First" to "Sixth") inside one table cell show that the content wanted to
   be a numbered list or a section of its own. The session that filed this
   item named it on 2026-11-02 as a structural problem rather than a phrasing
   one. The project owner then asked for it as the fifth pattern: "It should
   be five patterns" (project owner, 2026-11-02, in this item's thread).

**Example rewrite of line 395's paragraph.** "Symbols and the gas-phase
cascade ($`F_D`$, $`F_I`$, $`F_A`$) follow Hendrickx and De Wolf (pp.
161-162). They attribute the $`F_D - F_I`$ gradient to rebreathing (p. 169)
and the $`F_I - F_A`$ gradient to uptake (p. 171), and describe the teaching
role of the $`F_A/F_I`$ curve (p. 167)." The full citation follows unchanged.

**Decided 2026-11-02 (project owner, 2026-11-02).** This is a specified
decision, not a ratified one. The owner first agreed with the recommendation
and then said: "Strongly agree with item 1 actually in terms of making it a
document that clinicians can read. Not just a ratification." So the bar to
reopen it is a compelling argument, not ordinary evidence.

The goal is a `docs/MODEL.md` that a clinician can read. The decision history
comes out first, and the phrasing is rewritten after. The history means item
ids, re-measurement narratives, who-supplied-what notes and accounts of how a
choice was reached. It goes to the item that already holds it. Rewriting the
phrasing first would be undone by the next change that adds history in the
same style.

**Why it matters.** `docs/MODEL.md` is the document a clinician opens to
decide whether to trust a displayed number. Padding and decision history bury
the equation, the unit and the limitation that the reader came for. A reader
who has to skim past history to find the assumption may miss the assumption.

**The split, decided at triage on 2026-11-02.** The proposal that stood here
had four parts. Parts 3 and 4 stay in this item, together with the tool the
section parts need. Parts 1 and 2 are done together, one group of sections per
item, in the order the sections appear. Within each part the history comes out
first and the phrasing is rewritten after, in two commits. Doing both in one
pull request per group halves the number of reads of the same text.

This item builds four things, before any section part starts:

1. The five patterns in `.claude/rules/plain-writing.md`, with this item's
   line-395 paragraph as the before-and-after example.
2. `tools/new_prose.py` prints each changed paragraph, list-item paragraph
   and table row of `docs/MODEL.md` and `README.md` with 30 words or more. So
   the close-out prose review reads them, and `bin/docket arm` holds a branch
   until that review is recorded.
3. `tools/model_rewrite.py`, which a section part runs twice. `ids HEADING...`
   lists every item id that the named sections still cite outside the
   declared-none form ``no test yet (`PL-XXXX`)``. `lost` lists each equation,
   code span, number and citation that `docs/MODEL.md` held at the fork and no
   longer holds, and marks the ones the branch added to an item file. A
   section part's pull request body accounts for every line `lost` prints.
4. Step 8 of `.claude/skills/docket/modes/close-out.md` names the document
   paragraphs it now reviews.

The fourteen section parts, in document order (`bin/docket feature
prose-quality` lists them):

1. `PL-J8CG`: § "Status" through § "Model boundary", with the hazard table.
2. `PL-XTZW`: § "Conventions" through § "Conservation of agent mass".
3. `PL-TZ47`: § "Numerical method".
4. `PL-HJDK`: § "Source hierarchy: what may be cited as the authority for a
   value".
5. `PL-70B2`: the agent and MAC parameter sections, § "Required invariants",
   and § "Required tests" up to the published wash-in validation.
6. `PL-WBR3`: the published wash-in and elimination validation and the rest of
   § "Required tests".
7. `PL-QL0X`: § "Runtime controls" up to § "Supported input ranges".
8. `PL-QHR2`: § "Supported input ranges" and its subsections.
9. `PL-YVL0`: § "Reset behavior" through § "Interface boundary".
10. `PL-PS5H`: § "Minimum displayed outputs" up to § "The control-input
    timeline".
11. `PL-XT53`: § "The control-input timeline" through § "The six compartment
    traces: what separates them".
12. `PL-J37P`: § "Displayed precision".
13. `PL-XBJ3`: § "The chart's hover readout: what the tooltip may show"
    through § "The compartment schematic: what its heights, amounts and share
    bar assert".
14. `PL-9331`: § "Assumptions", § "Known limitations" and § "Release gate".

Each is blocked by this item, and moves to `ready` in the commit that closes
it, with its `verify:` written against `tools/model_rewrite.py ids`.

**How each section part is done.**

1. Run `python3 tools/model_rewrite.py ids` with the part's headings. It lists
   each item id the sections cite outside the declared-none form.
2. Take out the decision history: item ids, re-measurement narratives, notes on
   who supplied a source, ratification records, and accounts of how a choice
   was reached. Where the cited item already holds the passage, delete it.
   Where it does not, append the passage to that item's file under a dated
   paragraph, `**Moved from docs/MODEL.md on DATE.**`, naming the section it
   left. Where no item holds it, file one. Commit this step on its own.
3. Keep every equation, unit, value, assumption, limitation, citation with its
   locator, `provenance:`, `derived:` and `not-restated:` marker, named test,
   and declared-none form. `tools/doc_check.py` requires the last four. A fact
   may move to the section's note for developers, the paragraph at the
   section's end that opens with "**For developers.**", and a number may be
   restated in the reader's form with the same value, such as 4e-4 as 0.04%.
   Keep each heading's text, because `src/`, `tests/` and the item files cite
   sections by heading. Where a heading must change, update every citation of
   it in the same commit.
4. Rewrite the remaining prose against `.claude/rules/plain-writing.md`,
   including its five patterns. Before each paragraph, write down what its
   reader should take from it and do with it, and give each chosen value its
   reason from a record, as that rule says. Commit this step separately.
5. Run `python3 tools/model_rewrite.py lost` and account for each line it
   prints in the pull request body: moved to an item, history the item already
   held, restated with the same value, or restored. A fact moved to the note
   for developers prints nothing, because `lost` counts each fact across the
   whole document. A number restated with the same value prints as
   `restated`, beside the form that replaced it (`PL-TZ7R`).
6. Close out as usual. Step 8's prose review now reads the changed paragraphs.
   The pull request waits on the owner's read, since it changes
   `docs/MODEL.md`. The read can start from `lost`'s accounting rather than the
   whole diff.

**Revised 2026-11-02 (project owner, ratified, `PL-ZTZF`).** Step 6 no longer
holds every part for the owner's read. A part merges on green when `lost` lists
nothing added and each fact it lists as dropped is history or a duplicate the
document still holds. Only a sentence whose meaning needs a clinician's
judgment, such as what a hazard row promises, goes to the owner, quoted before
and after. A number that `lost` marks as restated counts as kept, and its new
form does not count as added, because the value is unchanged (`PL-TZ7R`,
following `PL-H76S`'s design round, ratified 2026-11-02 23:41Z, which lets a
reader's form replace e-notation).

Other open items change the same sections, so expect to resolve against
them. `PL-8YBS` changes a hazard-table row, `PL-19W8` and `PL-H94Q` hold
numeric paragraphs to tests, `PL-5C1H` does the same for the parameter
sections, and `PL-TCD3` changes how a marker holds a figure.

**Generator check.** A re-entry of `PL-PRCS`, closed 2026-10-18. The fact
misread is which prose the close-out review reads: `PL-PRCS` built the review
over `tools/new_prose.py`, which keeps only `.py` files, so every long
paragraph added to `docs/MODEL.md` since then reached `main` unreviewed. Part 2
of this item extends the same review to the document, which fixes the
mechanism rather than one instance of it.

**Constraint.** As in `PL-BZR4`: no equation, unit, assumption, limitation or
provenance note may be lost. A citation stays; narration about the citation
may go.

**Worked example for part 1 (drafted 2026-11-02, not yet checked against the
code).** The hazard-table row in `docs/MODEL.md` § "Reasonably foreseeable
misuse, and the hazards the presentation carries" for "reading one run's displayed value, or the record of
what was changed on it, as the other's while two are compared" has a
mitigation cell of 459 words (line 200 on 2026-11-02). The cell walks through
six places in prose ordinals, "First" to "Sixth", and cites six item ids:
`PL-L59K`, `PL-25DD`, `PL-C3GS`, `PL-TSZM`, `PL-T91K` and `PL-RNYV`. Prose
ordinals inside a table cell show that the content wanted to be a section.

The draft below keeps all six places, the condition on each, why visual cues
are not enough, and the three misreadings the names prevent. It drops the item
ids and the account of how each place was added, since those items already
hold it. The row's 13 tests stay in its last cell. Before adopting the draft,
check each numbered place against those tests, and decide whether "travels
with the panel rather than with its position in the column" is a design
reason the specification should keep.

The mitigation cell becomes:

> Every place that shows a value, or the record of what was changed, names
> its run in text while more than one run is drawn. § "Naming the run in a
> comparison" lists the six places.

The new section:

> ### Naming the run in a comparison
>
> While two or more runs are drawn, each of these names its run in text:
>
> 1. Each run's readout panel (§ "Minimum displayed outputs").
> 2. The chart's hover readout. With one run under the pointer, the name is
>    on the first line. With several, it is on each value line. Every run
>    inside the hover radius is reported, so a small pointer movement cannot
>    swap which run is read (§ "Where more than one trace answers").
> 3. The three advisory lines inside a chart: the wash-in state, the
>    off-scale notice, and the count of control changes the chart could not
>    mark. They stack one line per run.
> 4. The headings of the two record panels: the agent-accounting validation
>    in the sidebar, and the control-change record.
> 5. The notice banner between the transport controls and the readouts. Both
>    runs use the same place, and a banner with nothing to say is hidden, so
>    its position does not show whose it is.
> 6. The heading over each run's compartment schematic.
>
> Colour, line width and stacking order cannot do this job. The hover is
> separate from the legend, line width has no text equivalent, and no
> stacking order is shown on screen. Without the names, a learner could
> misread the comparison in three ways:
>
> - The control-change record, read as the other run's, says a run received
>   an intervention it never got.
> - A halt banner, read as covering the whole dashboard, says both runs are
>   frozen when one is still running.
> - One run's F_A/F_I could be read as the other's.
>
> With only one run drawn, the hover, the chart's advisory lines, the sidebar
> panel headings and the banner show no run name.

**Done when.** `.claude/rules/plain-writing.md` names the five patterns with
the line-395 example. `tools/new_prose.py` prints the changed long paragraphs
and table rows of `docs/MODEL.md` and `README.md`, and `--count` counts them,
so `bin/docket arm` holds a branch that changed one until its prose review is
recorded. `tools/model_rewrite.py ids` and `lost` work as described above, with
tests. Close-out step 8 says it reviews those paragraphs. The fourteen section
parts are `ready`, each with its `verify:`. The section parts themselves are
not this item's work.
