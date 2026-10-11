---
id: PL-RQT1
title: Decide the live splitter handle: width, rest, hover, cursor and drag feedback, rather than the toolkit's default
priority: P2
effort: S
status: needs-decision
classes: ux, planning
feature: interface-areas
touches: src/anesthesia_sim/app/, docs/items
added: 2026-10-11
payoff: the live splitter handle looks and behaves the same on the owner's macOS and in the test container, and shows the reader what a drag will move before it moves
---

**Problem.** Decide the live splitter handle: width, rest, hover, cursor and
drag feedback, rather than the toolkit's default. `ROADMAP.md` § "v0.6.0" ->
"Required scope" entry 20, member 3. v0.4.26 built the handle inert
(`inert_splitter` in `app/qt_widgets.py`); `PL-W9P6` turns it live and entry 14
(`PL-2KXB`) makes a border drag move the collinear chain `borders()` returns.

**What the toolkit would give, measured 2026-10-11.** Qt's Fusion style sets
`PM_SplitterWidth` to 4 px and the macOS style to 7 (`qfusionstyle.cpp`,
`qmacstyle_mac.mm`, qt/qtbase `dev`, read at raw.githubusercontent.com); the
offscreen `QSplitter` here reports `handleWidth` 4. Each draws a handle whose
look is the host style's and differs between the owner's macOS and the test
container's Fusion, which is the inherited-from-the-toolkit case entry 20
exists to refuse.

**The reference.** Blender draws a 2 px border (`U.border_width = 2`,
`source/blender/makesdna/DNA_userdef_types.h`) in `TH_EDITOR_BORDER`
(`0x161616ff`) between editors whose corners are rounded at `EDITORRADIUS` 6 px,
so the gap reads as a dark seam; the hit band is `BORDERPADDING`, the border
width plus 3 px each side, 10 px in all at 1x
(`source/blender/editors/screen/screen_intern.hh`,
`screen_draw.cc::ED_screen_draw_edges`, `screen_ops.cc`); the cursor over it is
a double-headed arrow, Ctrl snaps and Shift moves only the border under the
pointer (Blender Manual, `interface/window_system/areas.html` § "Resizing",
read 2026-10-11, paraphrased). The Manual's Border Width preference says a
larger value increases the hit zone and nothing else, which is the separation
to keep: the seam is the hit zone.

## Design round 2026-10-11

**Q1. Width and rest.** **Recommendation: an 8 px logical gap that draws
nothing of its own at rest** - the `BACKGROUND` canvas showing between two
`PANEL` Areas, which is the seam today's dashboard already has between its
panels and the shape Blender's dark border has - and the gap *is* the hit zone,
as a `QSplitterHandle`'s rect is. 8 px is Blender's 10 px band less the rounded
corners this project does not draw, and twice Fusion's 4, which is too narrow
to find by trackpad. WCAG 2.2 SC 2.5.8 (Target Size (Minimum), AA) asks 24 px
of a target and exempts one whose function another control on the page also
provides; the Area menu's Split entries (`PL-MS34`) and the keyboard route
(`PL-M352`) are that control, so the handle is held to findable rather than to
24. (www.w3.org refused the connection from this container on 2026-10-11, so
the criterion's text was not re-read today; the project's own constants are
`tools/contrast_check.py`'s `AA_TEXT` and `AA_NON_TEXT`.) Expressed in
`app/theme.py` as one constant applied to every live splitter, so the budget
(`PL-84QX`) can count it. *Alternatives refused:* the host style's handle,
which varies by platform and is the inherited default; a drawn grip or dotted
texture at rest, standing decoration on every seam where the gap already says
"two things".

**Q2. Hover.** **Recommendation:** the cursor becomes `Qt::SplitHCursor` or
`Qt::SplitVCursor` (the platform's double-headed arrow, Blender's cue) and a
2 px `PRIMARY` line is drawn down the middle of the gap over the full length of
the collinear chain the drag would move - not only the handle under the pointer
- because the chain is the one behaviour this project's tree keeps from
Blender's graph (`PL-3J2P`) and the reader should see what will move before it
moves. `PRIMARY` on `BACKGROUND` is 5.60:1, clearing `AA_NON_TEXT`. No fade is
specified: Blender fades its zones over 0.15 s (`screen_intern.hh`), and
whether this project animates anything is item 33's.

**Q3. Drag feedback.** **Recommendation:** the line follows the pointer and the
Areas re-lay out live - Qt's non-opaque resize, which redraws only on release,
is refused because a chart that redraws late hides the resampling entry 18's
assertion (via `PL-9LNF`) checks for; the line turns `WARNING` when the drag has
reached a neighbour's minimum and will go no further; and Escape cancels the
drag back to the sizes it started from, which Blender gives every area
operator (Manual, `interface/window_system/areas.html`). Shift to move only the
border under the pointer is kept as Blender has it; Ctrl snapping is not built,
there being nothing to snap to while sizes are fractions and no grid exists.

**Decision needed.** Q1-Q3 above: an 8 px gap that is the hit zone and draws
nothing at rest (Q1); the split cursor and a `PRIMARY` line along the whole
chain on hover (Q2); live re-layout, a `WARNING` line at a neighbour's minimum,
Escape to cancel (Q3). Agreeing with the recommendations ratifies the three.

**Done when.** Q1-Q3 are recorded with the owner's kind and date, this item
closes on that record, `PL-W9P6` builds the handle to it and `PL-2KXB` the drag,
declaring `PRIMARY` and `WARNING` on `BACKGROUND` as non-text pairs in
`tools/contrast_check.py`.

**Why it matters.** The handle is the reader's first act of making the layout
theirs and the one piece of furniture repeated at every split; its width is the
budget's per-split cost.

**Generator check.** A one-off, and work the owner asked for: one of the
members `ROADMAP.md` Required-scope entry 20 names, scoped on 2026-09-21
(`PL-M3X6`) and filed by its round on 2026-10-11. `touches` reaches
`docs/items` only because the item closes on its own record once answered; no
apparatus fact was misread.
