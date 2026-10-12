---
id: PL-5HSG
title: LayoutModel.resize re-proportions Areas off the dragged line, so dragging a root border moves a nested border no reader touched, where Blender moves only the borders on the line: decide which a reader gets before PL-W9P6 turns the handles live
status: untriaged
feature: interface-areas
added: 2026-10-12
---

**Problem.** `PL-1FT6`'s close-out review (`#1448`) found that
`LayoutModel.resize` moves borders off the line being dragged. In
`row[1, column[row[2,4], 3]]`, dragging the root border from 0.5 to 0.25
widens Area 4 from 0.25 to 0.375 of the window and moves the 2|4 border,
although Area 4 touches no moved line: sizes are proportions of their
parent, so a nested split re-proportions with it. Blender's
`area_move_apply_do` (`screen_ops.cc`) moves only the vertices flagged
`editflag`, so there Area 4 keeps its width. `#1448` corrected the
`resize` docstring and `docs/interface-provenance.md`, which had claimed the
line-merging rule was the only difference from Blender; the behaviour is
unchanged.

**Question.** When a reader drags one border, should every other border
stay where it is on screen (Blender), or move in proportion (today)?

**Recommendation:** match Blender. A border the reader did not touch moving
under a drag is a surprise on the interface `PL-W9P6` turns live, and a
plot or table resized as a side effect is a stale-context hazard the
expert-review standard names. The fix converts the off-line borders'
absolute positions back into proportions after the drag. Decide it before
`PL-W9P6` lands, because that is when a reader first drags anything.
