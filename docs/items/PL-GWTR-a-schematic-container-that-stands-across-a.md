---
id: PL-GWTR
title: A schematic container that stands across a pinned run heading's lower edge shows only its lower part, so its fill can look like that of a container at or over the scale's top
status: untriaged
feature: interface-design-review
touches: src/anesthesia_sim/app/qt_schematic.py, src/anesthesia_sim/app/pinned_heading.py
added: 2026-11-27
---

**Problem.** A schematic container that stands across a pinned run heading's lower edge shows only its lower part, so its fill can look like that of a container at or over the scale's top

**What a user sees** (the review of `PL-3NGZ` after it merged, 2026-11-27,
offscreen platform). `_paint_container` in `app/qt_schematic.py` outlines
each container and, for a container above the scale, draws a line in the
warning colour along its top. A container whose upper part is under a pinned
run heading shows neither. Its fill can reach the heading's lower edge, with
its side outlines and gridline marks running up to it. In the Maintenance
Workspace at 1366 by 768 with two runs, every container shows this way,
because the schematic's box is never taller than about 24 px (`PL-C14T`).

**Present before `PL-3NGZ`.** The schematic has scrolled inside its Area
since `PL-CBYS`, and the box's top edge cut a container the same way. The
pinned heading moved the cut down to the heading's lower edge.

**A cut label line can be misread too** (the review of `PL-H55Q`'s pull
request, 2026-11-27). A label line that stands across the heading's lower edge
shows only the lower part of its characters. In the schematic's font on the
offscreen test platform, the lowest 4 px above the baseline of "3" and "8"
differ in 3 pixels, so a cut tension can be taken for another.

**The tension line does not help where this happens.** A first
recommendation, on 2026-11-27, classed this `defect` because a user could read
the value from the container's tension line. The same review found that the
tension line is not on screen in this state. At 1366 by 768 with two runs,
10 to 24 px of rows show under the heading (`PL-C14T`). A container's tension
line starts 22 px below its lower edge (`_BUS_GAP` and `_LABEL_GAP` in
`app/qt_schematic.py`), so no tension line is whole there. The readouts above
the Areas stay in view at any window height and through any scrolling
(`docs/INTERFACE.md` § "Where the unconditional values sit on screen",
`PL-NNML`), and
they print each compartment's tension in % of 1 atm. In this state the first
run's readouts were on screen and the branch's were not (measured offscreen,
2026-11-27).

**No fix is available inside the scrolling page.** Raising the schematic's
least height to hold its heading, a row of containers and their tension lines
(233 px, which gives a 189 px box) grows the page. After a branch the page
then scrolls the concentration chart's plot into view and leaves the chart
View's top 102 px above the window, with the chart's title and key out of view
(measured offscreen, 2026-11-27). That would make `PL-DKQ5`'s hazard live in a
shipped Workspace. The interface pass (`PL-9WDN`) replaces the scrolling page.

**Recommendation, put to the coordinator on 2026-11-27.** Class it `safety`,
because a cut container or a cut tension can be read as a wrong value. Work it
with `PL-C14T` in the interface pass, deferred from v0.7.0. The one fix
available before then would hide the chart's key instead. The first run's
tensions stay readable above the Areas, and the state arises in one Workspace,
at one screen size, with a branch open. Holding v0.7.0 for it is the
alternative. Either way, two ways to show a cut remain, and each needs a cited
convention before it is chosen: a break line across each cut container at the
heading's lower edge, or scrolling the box a whole row of containers at a time.

**Done when.** A container whose top is out of view cannot be read as one
filled to its top or above the scale, and a label line cut by the heading
cannot be read as another value.
