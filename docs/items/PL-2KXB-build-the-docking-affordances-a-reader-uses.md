---
id: PL-2KXB
title: Build the docking affordances a reader uses: border drag moving the collinear chain, corner drag to split and to join, and Area swap, with a join the splitter tree cannot express refused rather than approximated
priority: P2
effort: L
status: blocked
classes: feature, ux
feature: interface-areas
touches: src/anesthesia_sim/app/, tests/integration
blocked-by: PL-W9P6, PL-G60V
added: 2026-09-16
---

**Problem.** Build the docking affordances a reader uses: border drag moving the collinear chain, corner drag to split and to join, and Area swap, with a join the splitter tree cannot express refused rather than approximated

**Why it matters.** This is what a reader actually does, and it is the half the
layout model cannot check for itself. Border drag has to move the collinear
chain `borders()` returns rather than one handle, which is how the splitter tree
recovers the one behaviour `PL-3J2P` measured it as giving up against Blender's
graph - differing exactly once across thirty-two shipped Blender Workspaces, at
a four-way junction. A join the tree cannot express must be unavailable in the
interface rather than silently producing a different layout.

**Done when.** A reader can drag a border (with the chain moving together),
drag a corner to split and to join, swap two Areas, and switch Workspaces by
tab; an unavailable join is visibly unavailable rather than approximated; and
each operation goes through the `LayoutModel` rather than through the widget
tree.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 14.

## Blocked on `PL-G60V`, 2026-10-12

[superseded 2026-10-18] `PL-G60V` closed on 2026-10-18 in `#1579`, so a join
already depends on the rectangles alone when this item starts. The owner answered `PL-G60V` on 2026-10-12 (ratified): whether two Areas can
be joined depends on the rectangles alone, never on which split came first.
This item builds the join a reader uses, where a refusal would first be seen,
so it waits for that change, as `PL-G60V`'s recommendation asked; the
ordering is a session's, recorded in `PL-G60V`.
