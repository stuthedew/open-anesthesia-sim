---
id: PL-9Z74
title: A too-small Area's floor is measured with its notice wrapped at the chooser's width, so in a wide column it reserves 30 to 50 px of wrapped lines it never uses and a neighbour gives up its View sooner than it needs to
status: untriaged
feature: area-layout-sizing
added: 2026-10-26
---

**Problem.** `AreaLayout._floor` (`app/area_layout.py`) measures the
too-small notice's height at `_structural_minimum`'s width, which is about the
chooser's width (140 to 170 px). It uses that height whatever width the Area
is drawn at. In a column of stacked Areas, each Area is as wide as the window,
for example 800 px. There, the title and the short statement each fit on one
line, but the floor reserves two or more lines for each.

**Why it matters.** Each too-small Area in a wide column claims roughly 30 to
50 px it does not use. A neighbour can then give up its View and show a
too-small notice although the window has room to draw it. `PL-Y65Q` chose
route B because it makes a neighbour give up its View least often, and this
works against that.

**Why it was not fixed in `PL-Y65Q`.** `layout/sizing.py`'s `settle` takes
each floor as one fixed `PixelSize`. A floor whose height depends on the
width the Area is given needs `settle` to take a function of width, or a
second pass once the widths are known. Measuring at the width the Area had in
the last layout is stale by one pass, and could clip the notice after a
narrowing. Route B as decided measured the floor at the floor's own width,
which is what `PL-Y65Q` built.

**Done when.** A too-small Area's floor holds the notice wrapped at the width
the Area is drawn at, and a test shows a wide stacked Area held at a floor
lower than the narrow one.

**Found by.** The blind review of `PL-Y65Q`'s branch, pass 1, finding F2,
2026-10-26.
