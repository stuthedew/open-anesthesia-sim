---
id: PL-D5J4
title: At 1366 by 768 the shipped Workspaces put each View's lesson below its Area's fold: Induction's wash-in curve, Maintenance's share bar and most of its schematic, and the Edit bookmarks button, while the Parameters Area has spare height
status: untriaged
feature: interface-design-review
added: 2026-11-22
---

**Problem.** At 1366 by 768 the shipped Workspaces put each View's lesson below its Area's fold: Induction's wash-in curve, Maintenance's share bar and most of its schematic, and the Edit bookmarks button, while the Parameters Area has spare height

**Go-ahead.** The design review that found this was approved by the project owner (project owner, 2026-11-22). It ran offscreen on `a7eb53f`, with screenshots of each Workspace and each View at 1366 by 768 and 1920 by 1080 in `/mnt/project-files/v0.7.0/design-review/`.

**What a learner sees at 1366 by 768.**

1. Induction: the wash-in Area shows its heading, caption and legend, and its
   curve starts at the Area's bottom edge, so the curve is off screen until
   the reader scrolls (`ws1-Induction-1366x768.png`). The concentration plot
   above it is 120 px tall including its axes.
2. Maintenance: the compartment schematic shows the tops of its containers
   only. The fills, the labels and the share bar, which is why the schematic is
   in Maintenance (`PL-PR1W`), are below the fold (`ws2-Maintenance-1366x768.png`).
3. Default, Induction and Maintenance: the Edit bookmarks button is cut by the
   Bookmarks Area's lower edge.

Meanwhile the Parameters Area holds about 86 px of controls in a taller Area
(`PL-4JCC`).

**Why it matters.** 1366 by 768 is the size the shipped layouts are budgeted
for (`data/workspaces/__init__.py`). A Workspace named for a task should show
that task's View whole there, without scrolling.

**What to do.** Re-share the shipped Workspaces' splits so that each
Workspace's own View fits at 1366 by 768: give the wash-in and schematic
Areas the height, and take it from the Parameters, Bookmarks and Branch Areas.
Work it with `PL-4JCC`, which touches the same files. The shares are
placeholders the session decides.

**Done when.** A test opens each shipped Workspace at 1366 by 768 and finds
the wash-in plot, the schematic's share bar and the Edit bookmarks button
inside their Areas' visible rectangles.
