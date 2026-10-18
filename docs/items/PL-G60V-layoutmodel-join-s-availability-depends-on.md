---
id: PL-G60V
title: LayoutModel.join's availability depends on which split was made first wherever four Areas meet at a point: a 2x2 grid built columns-first refuses joining its two left Areas, which rows-first allows, so decide whether join re-slices a cross junction
priority: P2
effort: M
status: done
classes: feature, ux
feature: interface-areas
touches: src/anesthesia_sim/layout/model.py, src/anesthesia_sim/layout/tree.py, tests/unit/test_layout_model.py, docs/interface-provenance.md, docs/items/PL-2KXB-build-the-docking-affordances-a-reader-uses.md
added: 2026-10-12
closed: 2026-10-18
pr: 1579
payoff: a join a reader is offered depends only on the rectangles they see, never on which split happened to come first
verify: grep -q 'def test_where_four_areas_meet_a_join_is_taken_whichever_cut_came_first' tests/unit/test_layout_model.py
falsifies: only where they sit next to each other
---

**Problem.** `PL-1FT6`'s close-out review (`#1448`) found that the layout
model's one-form-per-arrangement rule does not make a join's availability
independent of build order wherever four Areas meet at a point. A 2x2 grid
split columns-first is held as `column[row[1,3], row[2,4]]`, and `join(1, 2)`
(top-left with bottom-left) is refused as "only where they sit next to each
other in the same split"; the identical rectangles split rows-first are held
as `row[column[1,2], column[3,4]]`, and the same join is taken. The refused
result is expressible (`row[1, column[3,4]]`), so this is not `PL-3J2P`'s "a
join the tree cannot express". Blender's Shading workspace has exactly this
2x2 block, and Blender holds its Areas as a graph of shared vertices and
edges rather than a tree, so it has no build order for a join to depend on
(inferred from its data structure; its join was not read at source here).

`#1448` corrected the docstrings that claimed otherwise and pins today's
behaviour with a test, so this item is the decision rather than the
discovery.
Reproduced 2026-10-12 at triage: that test,
`test_where_four_areas_meet_a_join_depends_on_which_cut_came_first`, passes
on `#1448`'s head.

**Question.** Should `join` re-slice a cross junction - rebuild the
surrounding splits so that two Areas sharing a whole edge can be joined
however the grid was built?

**Recommendation:** yes. A reader sees rectangles, never the tree, so a join
offered or refused by which split happened to come first is a hidden mode
of exactly the kind `.claude/rules/expert-review.md` asks this interface to
remove. It belongs before `PL-2KXB` builds the join a reader uses, since
that is where the refusal would first be seen. The cost is a second shape
of `join` in `src/anesthesia_sim/layout/model.py` and its tests; nothing is
stored yet, so nothing has to migrate.

**Answered 2026-10-12: yes, `join` re-slices a junction where four Areas
meet** (project owner, 2026-10-12, ratified, over keeping today's `join`,
which takes or refuses such a join by which split came first). Given as
"Agree with recs" in the project thread at 19:16Z, on the review summary of
`#1448` that put this item as "Recommendation: fix it". `PL-2KXB` now waits
on this item, as the recommendation above asks. That ordering is the
recommendation's own and the summary did not repeat it, so it is a session's
sequencing rather than part of what he ratified. The rows-first tree in the
problem statement read `row[column[1,3], column[2,4]]` until this answer,
which is not the same rectangles; it is corrected above.

**Why it matters.** A reader sees rectangles and never the tree, so a join
taken in one 2x2 grid and refused in an identical one is a hidden mode, the
kind `.claude/rules/expert-review.md` asks this interface to remove. A reader
meets it the first time they join two Areas of a 2x2 grid.

**Done when.** Whether `LayoutModel.join` takes a join depends on the
rectangles alone, never on the order the splits were made in: two Areas that
share a whole edge are joined wherever a tree can hold the result, and the
only refusals left are a pair sharing no whole edge and a result no tree can
hold (`PL-3J2P`). In the 2x2 grid each of the four edge-sharing joins is taken
from both build orders and gives the same rectangles. The test pinning
today's refusal,
`test_where_four_areas_meet_a_join_depends_on_which_cut_came_first` in
`tests/unit/test_layout_model.py`, gives way to one asserting this; the
passages that call it an open decision or name the split as the rule
(`layout/tree.py`'s module docstring, and `join`'s docstring and refusal
wording in `layout/model.py`) say what the model now does.

**Built 2026-10-18 (`#1579`).** `join` no longer looks for the pair in one
split. It merges the two rectangles and divides the region of the lowest split
holding both again by straight cuts (`_resliced`). It tries first with each
subtree beside the pair kept whole, so that it changes no split it need not,
and then from every Area in the region, because a subtree's own border can be
the only line that divides the region. The refusals left are a pair that
shares no whole edge, an arrangement no straight cut divides (`PL-3J2P`), and a
result past `TREE_DEPTH_MAXIMUM`. A join can need one level of splits more
than the tree held, so where the lowest split's region is too deep, the region
of each split above it is re-sliced in turn, up to the whole window. An
adversarial review found the depth refusal depending on which cut came first
before that climb; a depth fuzz against a whole-window oracle then went from 52
wrong refusals in 6,536 joins to none. Blender's join was read at source this time:
`area_getorientation` and `screen_area_join_aligned` in
`source/blender/editors/screen/screen_edit.cc` (`blender/blender` `main`,
read 2026-10-18) decide and make a join from the two Areas' corners alone,
which confirms the inference above. A randomized check against an independent
area-level slicing oracle, on four seeds and about 180,000 joins, found no join
taken or refused differently from the rectangles; its first run is what found
the case where a subtree had to be opened.
