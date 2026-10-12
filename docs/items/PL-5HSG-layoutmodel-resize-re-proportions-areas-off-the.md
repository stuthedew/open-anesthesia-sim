---
id: PL-5HSG
title: LayoutModel.resize re-proportions Areas off the dragged line, so dragging a root border moves a nested border no reader touched, where Blender moves only the borders on the line: decide which a reader gets before PL-W9P6 turns the handles live
priority: P2
effort: M
status: ready
classes: ux
feature: interface-areas
touches: src/anesthesia_sim/layout/model.py, tests/unit/test_layout_model.py, docs/interface-provenance.md
added: 2026-10-12
payoff: dragging one border moves only that border's line, so no plot or table the reader did not touch resizes under them
verify: grep -q 'def test_a_drag_moves_only_the_borders_on_its_line' tests/unit/test_layout_model.py
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
unchanged. Reproduced 2026-10-12 at triage: the test that pins it,
`test_a_drag_keeps_each_childs_proportions_so_a_border_inside_one_moves`,
passes on `#1448`'s head.

**Question.** When a reader drags one border, should every other border
stay where it is on screen (Blender), or move in proportion (today)?

**Recommendation:** match Blender. A border the reader did not touch moving
under a drag is a surprise on the interface `PL-W9P6` turns live, and a
plot or table resized as a side effect is a stale-context hazard the
expert-review standard names. The fix converts the off-line borders'
absolute positions back into proportions after the drag. Decide it before
`PL-W9P6` lands, because that is when a reader first drags anything.

**Answered 2026-10-12: match Blender, before `PL-W9P6` lands** (project
owner, 2026-10-12, ratified, over keeping today's drag, which keeps the
proportions inside each child of the dragged split and so moves the borders
nested in them). Given as "Agree with recs" in the project thread at 19:16Z,
on the review summary of `#1448` that put this item as "Recommendation:
match Blender, before PL-W9P6 lands". So `PL-W9P6`'s `blocked-by` now names
this item too.

**Why it matters.** `PL-W9P6` turns the handles live, so its first drag is
the first a reader makes. A border they did not touch moving under that
drag, and a plot or table resized as a side effect, is the surprise and
stale-context hazard `.claude/rules/expert-review.md` names, and Blender,
this project's reference for how Areas behave (`docs/interface-provenance.md`),
moves only the dragged line.

**Done when.** `LayoutModel.resize` moves only the borders on the dragged
line, the handles `borders()` gives for it, and every other border keeps its
place in the window: in `row[1, column[row[2,4], 3]]`, dragging the root
border from 0.5 to 0.25 leaves Area 4 a quarter of the window wide and the
2|4 border at 0.75. A drag that would leave an Area beside the line no room
is refused, as `resize` refuses one today, until `PL-K285` makes it a clamp.
The test pinning today's drag,
`test_a_drag_keeps_each_childs_proportions_so_a_border_inside_one_moves` in
`tests/unit/test_layout_model.py`, gives way to one asserting this, and
`resize`'s docstring and `docs/interface-provenance.md` no longer name it as
a difference from Blender.
