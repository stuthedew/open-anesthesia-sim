---
id: PL-G60V
title: LayoutModel.join's availability depends on which split was made first wherever four Areas meet at a point: a 2x2 grid built columns-first refuses joining its two left Areas, which rows-first allows, so decide whether join re-slices a cross junction
status: untriaged
feature: interface-areas
added: 2026-10-12
---

**Problem.** `PL-1FT6`'s close-out review (`#1448`) found that the layout
model's one-form-per-arrangement rule does not make a join's availability
independent of build order wherever four Areas meet at a point. A 2x2 grid
split columns-first is held as `column[row[1,3], row[2,4]]`, and `join(1, 2)`
(top-left with bottom-left) is refused as "only where they sit next to each
other in the same split"; the identical rectangles split rows-first are held
as `row[column[1,3], column[2,4]]`, and the same join is taken. The refused
result is expressible (`row[1, column[3,4]]`), so this is not `PL-3J2P`'s "a
join the tree cannot express". Blender's Shading workspace has exactly this
2x2 block, and Blender holds its Areas as a graph of shared vertices and
edges rather than a tree, so it has no build order for a join to depend on
(inferred from its data structure; its join was not read at source here).

`#1448` corrected the docstrings that claimed otherwise and pins today's
behaviour with a test, so this item is the decision rather than the
discovery.

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
