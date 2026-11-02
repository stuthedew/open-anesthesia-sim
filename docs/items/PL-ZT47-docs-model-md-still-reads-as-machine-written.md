---
id: PL-ZT47
title: docs/MODEL.md still reads as machine-written after PL-BZR4's rewrite: tautological asides, 'X, not Y' and 'rather than' contrasts, and narration about its own provenance; the plain-writing rule names none of these patterns, and the close-out prose review reads only .py files, so MODEL.md's 2,348 lines added since were never reviewed
status: untriaged
feature: prose-quality
added: 2026-11-02
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

**Proposed split, for the session that triages this.** Each section-sized
part fits one session, since the whole file is about 140,800 words.

1. Move the decision history out, one group of sections per item. Each moved
   passage lands in its item file, or in a new one where no item holds it.
2. Rewrite the remaining prose of the same sections, against the four
   patterns above as well as `.claude/rules/plain-writing.md`.
3. Add the four patterns to `.claude/rules/plain-writing.md`, with this item's
   line-395 paragraph as the before-and-after example.
4. Make `tools/new_prose.py` return changed paragraphs of `docs/MODEL.md`, so
   the close-out prose review reads them. Parts 3 and 4 are workflow changes,
   so check the generator pause in `CLAUDE.md` before building them.

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
