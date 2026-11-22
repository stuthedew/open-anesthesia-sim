---
id: PL-K4CZ
title: At 1366 by 768 the concentration chart's legend and reference lines take more of its Area than the plot does: the plot widget is 228 px tall of a 480 px Area in Default and 120 px in Induction
status: untriaged
feature: interface-design-review
added: 2026-11-22
---

**Problem.** At 1366 by 768 the concentration chart's legend and reference lines take more of its Area than the plot does: the plot widget is 228 px tall of a 480 px Area in Default and 120 px in Induction

**Go-ahead.** The design review that found this was approved by the project owner (project owner, 2026-11-22). It ran offscreen on `a7eb53f`, with screenshots of each Workspace and each View at 1366 by 768 and 1920 by 1080 in `/mnt/project-files/v0.7.0/design-review/`.

**What a learner sees.** Above the plot sit the caption, the 1 MAC line, the
MAC-awake line, the compartment check boxes in two or three wrapped rows, the
clinical references in two rows and the run record row, about 190 px in all at
1366 by 768 (`ws0-Default-1366x768.png`). The plot widget, axes included, is
228 px of a 480 px Area in Default and 120 px in Induction (measured offscreen).

**Why it matters.** The plot is the chart's reason to exist, and at the
smallest supported screen the text that explains it gets more height than it
does. The lines are required, so they cannot simply go. The question is
where they sit.

**What to do.** This is design input for the grey-box layouts in `PL-2V6V`.
Two directions to try there: a legend in one column beside the plot, which
uses the width the chart has spare at 1366 px, and folding the 1 MAC and
MAC-awake reference values into their legend rows so each fact is stated
once. Either must keep every value `docs/INTERFACE.md` § "Minimum displayed
outputs" requires on screen, which makes the final choice the owner's.

**Done when.** `PL-2V6V`'s layouts show the plot taking at least half the
chart Area at 1366 by 768 with every required line visible, or record why
not.
