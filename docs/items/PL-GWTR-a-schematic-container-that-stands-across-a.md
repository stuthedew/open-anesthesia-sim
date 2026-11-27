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

**Recommendation, not yet decided.** Class it `defect` rather than `safety`,
and work it with `PL-C14T` in the interface pass, because the fix is a choice
of how a cut is drawn. A container's cut is visible: its side outlines run
into the heading's edge, and the box's scroll bar shows that more lies above.
A user who needs the value reads it from the container's tension line, which
names it in % of 1 atm. Two ways to show the cut are open, and each needs a
cited convention before it is chosen. One draws a break line across each cut
container at the heading's lower edge. The other keeps whole containers in
view by scrolling the box a container at a time.

**Done when.** A container whose top is out of view cannot be read as one
filled to its top or above the scale.
