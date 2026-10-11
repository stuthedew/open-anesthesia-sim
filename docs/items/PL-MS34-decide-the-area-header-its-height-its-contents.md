---
id: PL-MS34
title: Decide the Area header: its height, its contents and their order, with the View name and the chooser in it
priority: P2
effort: S
status: needs-decision
classes: ux, planning
feature: interface-areas
touches: src/anesthesia_sim/app/, docs/items
added: 2026-10-11
payoff: every Area carries one row that names its View and its run and reaches every Area operation, at a height the budget can count
---

**Problem.** Decide the Area header: its height, its contents and their order,
with the View name and the chooser in it. `ROADMAP.md` § "v0.6.0" ->
"Required scope" entry 20, member 2. The member asked first whether there is a
header at all, and that half is answered: `PL-TH35` Q11 (ratified 2026-09-27)
has the container draw one header per Area carrying the registry title, the
run's name where the Area's View is bound to a run, the View chooser and the
Area operations, and `PL-50PZ` Q4 puts the chooser in it, one per Area. What is
open is what that header looks like. `PL-W9P6`'s adapter builds it.

**The reference, re-read 2026-10-11.** Blender's header is a small horizontal
strip at the top or bottom of an editor holding its menus, with the editor-type
selector as the first button at its left (Blender Manual,
`interface/window_system/regions.html` and `editors/index.html`, paraphrased).
It is `ED_area_headersize()` tall - `U.widget_unit` plus `UI_SCALE_FAC *
HEADER_PADDING_Y`, 20 + 6 = 26 px at 1x (`source/blender/editors/screen/area.cc`;
`HEADERY` and `HEADER_PADDING_Y` in `source/blender/makesdna/DNA_screen_types.h`,
`blender/blender` `main`, read at raw.githubusercontent.com) - and is drawn in
a shade of the editor's own surface (`header 0x303030b3` in
`release/datafiles/userdef/userdef_default_theme.c`). This project diverges in
who draws it (the container, not the View; `PL-TH35`) and keeps the shape.

## Design round 2026-10-11

**Q1. Height.** **Recommendation: one text row, derived from the font and never
a literal pixel count** - the `METRIC_NAME_SIZE` line height plus the vertical
padding a flat `QToolButton` takes, which is 27 px at the offscreen fallback
font ("Sans Serif 9 pt", tree `1ee4e78e`, measured 2026-10-11) and the same
row unit the tab strip uses (`PL-QW1Z` Q2). Blender's 26 at 1x is the check
that the number is in the right place. `PL-3355` and `PL-Z4K6` are why it is
derived: a recorded pixel ladder is wrong on the next font.

**Q2. Contents and their order, left to right.** **Recommendation:** (1) the
View chooser, showing the current View's registry title and a chevron
(`PL-RBXL` decides its look), the header's leftmost control exactly as
Blender's editor-type button is; (2) the run's name, in `MUTED` at
`METRIC_NAME_SIZE`, only where `docs/MODEL.md`'s rule puts it on this Area
(`PL-W54S`, `PL-7Z84`), and nothing in its place otherwise; (3) a stretch;
(4) the Area menu, a flat button labelled "Area" with a chevron, holding Split
horizontally, Split vertically, Join with..., Swap with..., Close Area - the
menu route entry 15 (`PL-M352`) requires, visible rather than Blender's
right-click-only header menu, because the corner affordance (`PL-30L5`) is
the thing most learners will not find and this button is where they find the
same operations by reading. No title text beside the chooser: the chooser *is*
the title. Blender shows the editor's icon there; this project has no icon set
until item 33, so the title is text. No caption and no "View:" label
(`.claude/rules/ui-reader.md`).

**Q3. Surface.** **Recommendation: the header shares the Area's `PANEL`
surface, with a 1 px `GRIDLINE` rule beneath it** - today's panel-heading
composition (`run_view.py`'s heading rows) carried to the Area, so a learner
meets no new surface. `GRIDLINE` is decorative here and owes no contrast
minimum; the header's edge is given by its controls, not by the line.
*Alternative refused:* Blender's tinted header band, a second surface the theme
would have to declare for no information gain.

**Q4. The too-small case in the header.** `PL-K285` decided the header still
names the View when the content is replaced by the needed-against-available
statement, and `PL-DB5G` carries what that statement looks like. This item adds
only that the header never shrinks below its row unit: an Area too short for
its own header is the refused size, not a shorter header.

**Decision needed.** Q1-Q3 above: a one-row header derived from the font (Q1);
chooser, run name, stretch, Area menu, left to right (Q2); the Area's own
surface with a rule beneath (Q3). Q4 follows from `PL-K285` and is recorded
rather than asked. Agreeing with the recommendations ratifies the three.

**Done when.** Q1-Q3 are recorded with the owner's kind and date, this item
closes on that record, and `PL-W9P6` builds the header to it, declaring its
colour pairs in `tools/contrast_check.py`.

**Why it matters.** The header is on every Area in every Workspace, so its
height is paid once per Area out of the chart's budget (`PL-84QX`), and it is
the one place the reader learns which View, and whose run, they are looking at.

**Generator check.** A one-off, and work the owner asked for: one of the
members `ROADMAP.md` Required-scope entry 20 names, scoped on 2026-09-21
(`PL-M3X6`) and filed by its round on 2026-10-11. `touches` reaches
`docs/items` only because the item closes on its own record once answered; no
apparatus fact was misread.
