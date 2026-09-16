---
id: PL-3J2P
title: Decide whether the area layout is a shared-vertex graph or a nested-splitter tree before the Qt layout work starts, because ROADMAP item 34 already specifies aligned-border dragging, four-way corner operations and arbitrary area swap, and a QSplitter tree makes all three expensive
status: untriaged
touches: ROADMAP.md
added: 2026-09-16
---

**Problem.** Decide whether the area layout is a shared-vertex graph or a nested-splitter tree before the Qt layout work starts, because ROADMAP item 34 already specifies aligned-border dragging, four-way corner operations and arbitrary area swap, and a QSplitter tree makes all three expensive

**Why it matters.** This is the one decision from the 2026-09-16 Blender read
(`PL-FTP5`) that is hard to reverse, and it will otherwise be made by default by
whoever first reaches for `QSplitter`.

**The two representations.**

*Nested-splitter tree.* What Qt hands you. `QSplitter` inside `QSplitter`,
`saveState()`/`restoreState()` for persistence, near-zero code. A layout is a
binary tree of horizontal and vertical divisions.

*Shared-vertex graph.* What Blender does: a set of vertices, a set of edges
joining them, and areas that name four corner vertices shared with their
neighbours. A layout is a planar subdivision, not a tree.

**What the tree cannot express cheaply.** ROADMAP item 34 already records three
behaviours as wanted, and each is free in the graph and hand-written in the tree:

1. *Dragging a border moves every aligned border with it.* In the graph the
   borders are the same vertices, so this is one move. In a tree, aligned
   borders in different subtrees are unrelated objects that must be found and
   moved in sync.
2. *Four-way corner operations* — drag a corner to split, join, do both at once,
   or replace a neighbour. A tree has no representation of "four areas meet at
   this point"; that configuration is two nested splitters, and which two
   depends on insertion order.
3. *Swapping any two areas in a window.* Cheap in the graph (swap the contents
   of two nodes). In a tree, two areas at different depths cannot swap without
   restructuring.

None of the three is safety-critical, and a tree would ship a usable tiled
layout. The question is whether item 34's recorded interaction model is the
point or is polish, and that is the project owner's call, not a session's.

**A third option, and the one to argue for.** Keep the layout model as pure
Python — vertices, edges, areas, and the operations on them — with no Qt import
at all, and drive plain `QWidget.setGeometry()` from it. The graph is
straightforward once it is not fighting a widget container: a planar subdivision
with axis-aligned edges is a small amount of code, and it is testable without a
running interface, which `QSplitter.saveState()` is not. This also satisfies
`CLAUDE.md`'s rule that the toolkit stays out of the logic, which a
`QSplitter`-as-source-of-truth design would violate by construction.

**Done when.** ROADMAP item 34 records which representation the layout uses and
why, so the Qt work starts from a decision rather than from whichever container
was reached for first.

**Timing.** Before `PL-LH18` (the item building main UI elements as Blender-style
areas, in flight on another branch) reaches its layout work.
