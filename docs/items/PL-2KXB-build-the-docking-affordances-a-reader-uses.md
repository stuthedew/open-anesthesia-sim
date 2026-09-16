---
id: PL-2KXB
title: Build the docking affordances a reader uses: border drag moving the collinear chain, corner drag to split and to join, and Area swap, with a join the splitter tree cannot express refused rather than approximated
status: blocked
feature: interface-areas
added: 2026-09-16
priority: P2
effort: L
blocked-by: PL-W9P6
classes: feature, ux
touches: src/anesthesia_sim/app/, tests/integration
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
