---
id: PL-DB5G
title: Decide the look of the two Area failure states, an unknown View kind and a refused size, as presentation safety rather than taste
priority: P1
effort: S
status: done
classes: safety, ux, planning
feature: interface-areas
touches: src/anesthesia_sim/app/, docs/items
added: 2026-10-11
closed: 2026-10-11
pr: 1395
payoff: an Area that cannot show its View shows one unmistakable notice and never a plausible number
verify: grep -qF 'Answered 2026-10-11' docs/items/PL-DB5G-decide-the-look-of-the-two-area-failure-states.md
---

**Problem.** Decide the look of the two Area failure states, an unknown View
kind and a refused size, as presentation safety rather than taste. `ROADMAP.md`
§ "v0.6.0" -> "Required scope" entry 20, member 6. What each state *does* is
decided: `PL-R1WQ` has an Area whose saved View kind this build lacks fail
visibly in that Area, substitute nothing, keep the tag in the model, and give
the renamed and the removed case their own messages through `RETIRED_TAGS`;
`PL-K285` has an Area that cannot be given the size its View needs keep its
header naming the View, replace the content with a statement of needed against
available, and scale, clip or collapse nothing. Both diverge from Blender on
purpose: Blender collapses a too-small region to nothing (`RGN_FLAG_TOO_SMALL`,
recorded in `PL-K285`). What is open is what the two look like.

## Design round 2026-10-11

**Q1. One component or two.** **Recommendation: one Area notice, with the two
failure states and the empty Area (`PL-WV9K`: text in the rectangle) as its
instances** - and, should `PL-7Z84`'s run binding ever leave an Area without
its run, that case too. A learner then meets one shape for "this Area is not
showing a View right now" and learns it once. The notice is drawn by the
container on the Area's `PANEL` surface under the header, aligned top-left at
`PANEL_PADDING`, and is text alone: a title line in `WARNING` bold at
`METRIC_NAME_SIZE` and a body in `INK` regular at the same size, wrapped to the
Area's width. No fill, no border, no icon, no axes, no placeholder number.
`WARNING` is already the project's colour for a condition needing attention
(`NoticeLabel` in `app/qt_widgets.py`), and `.claude/rules/ui-reader.md`
admits conditional text that fires only while its condition holds, which these
are. Both pairs clear `AA_TEXT` on `PANEL` (`WARNING` 6.79:1, `INK` 11.50:1,
computed from `app/theme.py` on 2026-10-11). *Alternatives refused:* a red or
tinted fill over the Area, which is an alarm register the dashboard does not
use and would read as a clinical alarm; a dialog, which Blender never raises
for layout and which hides the Area it is about; a smaller, muted body, which
is the only content in the Area and is read standing back from a laptop.

**Q2. The unknown-kind instance.** Title: "This Area's View is not in this
build." Body: the saved kind by its tag; then `RETIRED_TAGS`'s sentence where
the tag is known (renamed to X; removed in version Y), or "This build does not
know it." where it is not; then one line of what to do: "Choose a View from the
menu above. The saved name is kept until you do." The last sentence is the
model keeping the tag (`PL-R1WQ`), said where it matters: a learner who saves
without choosing has lost nothing.

**Q3. The too-small instance.** Title: "Too small for <View title>." Body: "It
needs at least W by H px; this Area is w by h." in whole pixels, then "Drag a
border to enlarge it, or choose a smaller View from the menu above." The
numbers are the View's declared minimum and the Area's current content size,
both facts the container holds; they are not model outputs and carry no
clinical unit, which is the one place a number in a failure state is safe. The
header stays, the chooser stays usable, and the statement updates as the Area
is dragged, so the learner sees it clear the moment the size is enough.

**Q4. What must never appear.** No value from any run: not a last-known
concentration, not a stale chart frame, not a greyed readout. A failure state
showing a plausible number is the hazard `CLAUDE.md`'s clinical-output standard
names, and the tests `PL-R1WQ` and `PL-K285` owe assert that the Area's visible
strings are the notice's and nothing else.

[superseded 2026-10-11: answered below, every recommendation ratified]
**Decision needed.** Q1-Q3 above: one text-only Area notice for every state in
which an Area shows no View (Q1), and the wording of its unknown-kind (Q2) and
too-small (Q3) instances. Q4 restates the clinical-output standard and is not a
choice. Agreeing with the recommendations ratifies the three.

**Done when.** Q1-Q4 are recorded with the owner's kind and date, this item
closes on that record, and `PL-R1WQ` and `PL-K285` build their states to it
with the regression tests their class owes, declaring the notice's pairs in
`tools/contrast_check.py`.

**Why it matters.** These two states are seen by a learner, not a developer:
one is reached by opening a layout saved under another build, the other by
dragging a border too far on a laptop. A failure state that looks like a dimmed
View is read as a View.

**Generator check.** A one-off, and work the owner asked for: one of the
members `ROADMAP.md` Required-scope entry 20 names, scoped on 2026-09-21
(`PL-M3X6`) and filed by its round on 2026-10-11. `touches` reaches
`docs/items` only because the item closes on its own record once answered; no
apparatus fact was misread.

## Answers 2026-10-11

**Answered 2026-10-11: Q1-Q3 ratified** (project owner, 2026-10-11, ratified,
over the alternatives each question names - a tinted fill, a dialog, a smaller
muted body, and two components), given in the project thread as "Agree with
recs" after the recommendations were put one line each with the mock-up
(https://claude.ai/artifact/3KmFvWB3nXmjLBHKogNiNE) and the 1366 by 768 floor
confirmed by the same word. This item closes on that record; the build items
named in its Done-when carry the look.
