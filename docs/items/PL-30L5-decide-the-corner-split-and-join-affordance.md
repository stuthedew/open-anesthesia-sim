---
id: PL-30L5
title: Decide the corner split and join affordance: visible grip or hot zone, and whether a drag previews the split before it commits
priority: P2
effort: S
status: done
classes: ux, planning
feature: interface-areas
milestone: v0.5.23
touches: src/anesthesia_sim/app/, docs/items
added: 2026-10-11
closed: 2026-10-11
pr: 1395
payoff: a learner discovers that an Area's corners split and join it, and sees what a drag will do before it commits
verify: grep -qF 'Answered 2026-10-11' docs/items/PL-30L5-decide-the-corner-split-and-join-affordance.md
---

**Problem.** Decide the corner split and join affordance: visible grip or hot
zone, and whether a drag previews the split before it commits. `ROADMAP.md`
§ "v0.6.0" -> "Required scope" entry 20, member 4, which the entry calls the
most learnable-or-not interaction in the milestone. Entry 14 (`PL-2KXB`) builds
corner drag to split and to join.

**The reference, re-read 2026-10-11.** Blender's corner is an invisible action
zone: the cursor becomes a cross over it, dragging inward splits (left or right
for a vertical split, up or down for a horizontal one), dragging into a
neighbour joins, the two can be one gesture, the areas about to be joined are
shown brighter, and Escape or right-click cancels (Blender Manual,
`interface/window_system/areas.html` § "Docking", paraphrased). The zone is
`UI_AZONESPOTW_LEFT` or `_RIGHT` by `UI_AZONESPOTH` - about 8 by 12 px at 1x
(`source/blender/editors/include/UI_interface_c.hh`,
`source/blender/editors/screen/area.cc::area_azone_init`, `blender/blender`
`main`, read at raw.githubusercontent.com). A visible grip exists only behind
the Interface preference "Corner Handles", off by default and described as
especially useful on touch devices (Manual, `editors/preferences/interface.html`);
when on, `area_draw_azone` draws `ICON_GRIP_V` at alpha 0.4 in the header's
corners (`area.cc`; `USER_AREA_CORNER_HANDLE` in `DNA_userdef_types.h`). The
split is previewed before it commits: `screen_draw_split_preview` outlines the
two halves and draws the split line at twice the border width in the border
colour, and `screen_draw_join_highlight` darkens the part that will close
(`source/blender/editors/screen/screen_draw.cc`). A split is refused when the
area is narrower than twice `AREAMINX` (29 px) or shorter than twice the header
(`screen_ops.cc`).

## Design round 2026-10-11

**Q1. Grip or hot zone.** **Recommendation: a hot zone at all four corners of
every Area, with a grip drawn only while the pointer is inside that Area** -
between Blender's default (invisible) and its preference (always on). The zone
is a 16 px square at 1x inside the Area's corner, twice Blender's and under
SC 2.5.8's 24 because the header's leftmost control, the chooser, begins
`PANEL_PADDING` (14 px) in and the zone must not take its first click; the Area
menu's Split and Join entries (`PL-MS34`, `PL-M352`) are the equivalent control
that criterion allows. The grip is three short `MUTED` strokes at 40 % alpha in
the corner patch, Blender's `ICON_GRIP_V` in shape, shown when the pointer
enters the Area and gone when it leaves, so an Area being handled shows its
corners work and an Area being read shows nothing. The cursor over a zone is
the platform's cross (`Qt::CrossCursor`; Blender's `WM_CURSOR_EDIT`).
*Alternatives refused:* invisible zones, Blender's default, which the entry
names as the way most learners never find the layout is theirs; always-visible
grips, four marks on every Area forever, which `.claude/rules/ui-reader.md` and
the budget both argue against; a split button in the header, which exists
already as the Area menu.

**Q2. Preview before commit.** **Recommendation: yes, both ways.** A drag inward
draws a 2 px `PRIMARY` line across the Area where the split will fall, moving
with the pointer; a drag into a neighbour tints the Area that will close with
`MUTED` at 40 % alpha and outlines the combined Area in `PRIMARY`, with the
arrow cursor for the join direction (Blender's N/S/E/W cursors in
`screen_ops.cc`). Nothing in the model changes until release; Escape cancels
and restores the cursor. A split is refused during the drag only below the
structural minimum - a half that could not hold its own header row and one
line of `PL-DB5G`'s notice - with the line turning `WARNING` and the release
doing nothing, as Blender refuses below twice `AREAMINX`; a half too small for
the *View* it inherits is allowed, and shows `PL-K285`'s statement, which names
how to fix it. Refusing at the View's minimum instead would make a chart Area
unsplittable on a laptop.

**Q3. Blender's extras.** Not built in v0.6.0: Ctrl-drag corner swap, Area
Options on a border's right-click, drag-into-the-middle replace, Maximize,
Focus Mode, Duplicate Area into New Window. Swap is in the Area menu
(`PL-MS34`); the rest is `ROADMAP.md` § "Explicitly out of scope for v0.6.0"
or item 33's.

[superseded 2026-10-11: answered below, every recommendation ratified]
**Decision needed.** Q1-Q2 above: hot zones at every corner with a grip shown
only while the pointer is in the Area (Q1), and a preview before every split
and join commits, refused only below the structural minimum (Q2). Q3 is scope
already decided and is recorded rather than asked. Agreeing with the
recommendations ratifies both.

**Done when.** Q1-Q2 are recorded with the owner's kind and date, this item
closes on that record, and `PL-2KXB` builds corner drag to it, declaring the
grip and overlay colours in `tools/contrast_check.py`.

**Why it matters.** Entry 20 says it: an invisible affordance means most
learners never discover the layout is theirs, and an always-visible one costs
every Area a mark forever. Hover-revealed is the cheapest thing that teaches.

**Generator check.** A one-off, and work the owner asked for: one of the
members `ROADMAP.md` Required-scope entry 20 names, scoped on 2026-09-21
(`PL-M3X6`) and filed by its round on 2026-10-11. `touches` reaches
`docs/items` only because the item closes on its own record once answered; no
apparatus fact was misread.

## Answers 2026-10-11

**Answered 2026-10-11: Q1-Q2 ratified** (project owner, 2026-10-11, ratified,
over the alternatives each question names - invisible zones, always-visible
grips, a split button in the header, and refusing a split at the View's
minimum), given in the project thread as "Agree with recs" after the
recommendations were put one line each with the mock-up
(https://claude.ai/artifact/3KmFvWB3nXmjLBHKogNiNE) and the 1366 by 768 floor
confirmed by the same word. This item closes on that record; the build items
named in its Done-when carry the look.
