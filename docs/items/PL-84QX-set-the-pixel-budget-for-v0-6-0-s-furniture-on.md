---
id: PL-84QX
title: Set the pixel budget for v0.6.0's furniture on the 1366 px laptop reference before the tab strip, the Area headers and the live handles consume it
priority: P2
effort: S
status: needs-decision
classes: ux, planning
feature: interface-areas
touches: ROADMAP.md, docs/items
added: 2026-10-11
payoff: the three new consumers of screen are sized against one measured number instead of each on its own, so the chart keeps its minimum on a 1366 px laptop
---

**Problem.** Set the pixel budget for v0.6.0's furniture on the 1366 px laptop
reference before the tab strip, the Area headers and the live handles consume
it. `ROADMAP.md` § "v0.6.0" -> "Required scope" entry 20 names it as the one
question none of the seven members carries alone. `PL-Z4K6` asked whether seven
readout columns are wanted on a 1366 px laptop on a window carrying none of
this furniture; the Nielsen Norman Group's name for the failure is chrome
obesity (`PL-M3X6`).

**The reference and the numbers, measured 2026-10-11.** Offscreen, Fusion,
"Sans Serif 9 pt" fallback, tree `1ee4e78e`; the owner's macOS font moves each
row by a pixel or two. The reference is a 1366 by 768 display, which leaves
about 700 px of client height after the system menu bar and the window title;
the desktop comparison is 1920 by 1000.

| Consumer, one run, 1366 by 700 | px |
| --- | ---: |
| page padding, top and bottom | 32 |
| title row (26 px title, version badge) and its spacing | 44 |
| transport row and its spacing | 60 |
| readout row (seven panels) and its spacing | 134 |
| disclaimer line | 15 |
| **region as it stands** | **285** |
| parameter row and its handle | 90 |
| concentration chart at its `CHART_HEIGHT` minimum | 360 |

Today the page is 1589 px tall at that width and scrolls inside the 700 px
viewport: the concentration chart sits at its 360 px minimum and the wash-in
chart under it is reached by scrolling. At 1920 by 1000 the chart is still 360
and the page still scrolls. v0.6.0 removes the page scroll: Areas fill the
window and sizes are fractions (`PL-HJPY` Q5), so what does not fit is not
scrolled to but refused (`PL-K285`).

The furniture at the sizes `PL-QW1Z`, `PL-MS34` and `PL-RQT1` recommend: tab
strip 27 + first Area header 27 + one handle 8 = 62 px before the first Area's
content, and 35 px more for each further Area stacked under it. A second run
adds about 170 px to the region (a transport row and a readout row; inferred
from `run_view.py`'s per-run builders - the two-run measurement failed on a
scripting error, `BranchedCase.fork_points_s` being a property, and is still to
be re-run).

**The arithmetic.** 700 - 285 - 62 = 353 px for the first Area's content with
one run and nothing else on screen: 7 px short of the chart's minimum before
the parameter View is placed anywhere. With the title row gone (`PL-J8K2` Q2):
700 - 241 - 62 = 397 px, the chart fits with 37 px to spare, and the parameter
View - 86 px today as a row of four, roughly 350 to 380 px as a column - goes
beside the chart in a right column at today's sidebar width, which the 370 px
under that column's header holds only just; the accounting View is not in the
shipped defaults (`PL-KXTL`), so the column carries nothing else. With two
runs: 700 - 411 - 62 = 227 px, 133 px short with the furniture and 71 px short
with none at all, so compare mode on this reference is past the chart's minimum
today and is held up by the region, not by the furniture.

## Design round 2026-10-11

**Q1. The budget.** **Recommendation:** on the 1366 by 700 reference with one
run, the shipped default Workspace shows the concentration chart at no less
than its current 360 px minimum with the parameter View visible; the furniture
above the first Area is capped at two text rows (the tab strip and one Area
header, about 54 px at the reference font) plus 8 px per handle; and the region
gives back the title row's 44 px (`PL-J8K2` Q2). Expressed as rows and the
chart's own minimum rather than as a pixel ladder (`PL-3355`), so it holds on
the owner's font. *Alternatives refused:* lowering the chart's 360 px minimum
to make room, which is a decision about the chart's legibility that nothing
here has measured; keeping the title row and accepting a chart that fits only
on a desktop, which makes the shipped default a laptop regression against
v0.5.0's definition of done.

**Q2. Compare mode.** **Recommendation: name it and hand it on, not solve it
here.** Two runs are 71 px past the chart's minimum on this reference before
any furniture, and the one-run arrangement leaves 37 px of slack, which no
second row of controls fits. So the budget above holds for one run, and the
per-substance tier's density for two - two values in one panel, or two runs in
one row - is `PL-W54S`'s design, constrained by this number: compare mode on
the laptop reference either accepts a chart under 360 px or rethinks the
per-run rows, and the furniture is the same either way.

**Q3. Where it is recorded.** In `ROADMAP.md` Required-scope entry 20, as the
sentence that closes it, and `PL-KXTL`'s shipped Workspaces are composed within
it; this item then closes on its record.

**Decision needed.** Q1-Q2 above: the budget as a rule - the chart at its
minimum with the parameter View visible on the 1366 by 700 reference, two text
rows of furniture plus 8 px per handle, the title row's 44 px given back (Q1) -
and compare mode named with its number and handed to `PL-W54S` rather than
solved here (Q2). Agreeing with the recommendations ratifies both.

**Done when.** Q1-Q2 are answered, entry 20 carries the budget as decided, and
the two-run measurement has been run and its number has replaced the inferred
170 px above.

**Why it matters.** Three new consumers are about to be built against a chart
that already sits at its minimum on a laptop; without the number, each one is
sized on its own and the chart pays the sum.

**Generator check.** A one-off, and work the owner asked for: one of the
members `ROADMAP.md` Required-scope entry 20 names, scoped on 2026-09-21
(`PL-M3X6`) and filed by its round on 2026-10-11. `touches` reaches
`docs/items` only because the item closes on its own record once answered; no
apparatus fact was misread.
