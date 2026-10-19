---
id: PL-2KXB
title: Build the docking affordances a reader uses: border drag moving the collinear chain, corner drag to split and to join, and Area swap, with a join the splitter tree cannot express refused rather than approximated
priority: P2
effort: L
status: ready
classes: feature, ux
feature: interface-areas
touches: src/anesthesia_sim/app/, src/anesthesia_sim/layout/, tests/integration, tests/unit/test_layout_model.py, tools/contrast_check.py, docs/ARCHITECTURE.md
added: 2026-09-16
payoff: a reader can split, join and swap Areas and switch Workspaces with the mouse, and a join the layout cannot make is shown as unavailable rather than approximated
verify: grep -q 'def test_a_corner_drag_inside_its_area_previews_the_split_and_makes_it_on_release' tests/integration/test_layout_adapter.py && grep -q 'def test_a_join_the_layout_cannot_make_is_previewed_refused_and_release_does_nothing' tests/integration/test_layout_adapter.py && grep -q 'def test_a_tab_switches_the_layout_and_leaves_the_run' tests/integration/test_workspace_tabs.py
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

## [superseded 2026-10-18] Blocked on `PL-G60V`, 2026-10-12

[superseded 2026-10-18] `PL-G60V` closed on 2026-10-18 in `#1579`, so a join
already depends on the rectangles alone when this item starts. The owner answered `PL-G60V` on 2026-10-12 (ratified): whether two Areas can
be joined depends on the rectangles alone, never on which split came first.
This item builds the join a reader uses, where a refusal would first be seen,
so it waits for that change, as `PL-G60V`'s recommendation asked; the
ordering is a session's, recorded in `PL-G60V`.

**`PL-W9P6` built, 2026-10-18.** A border drag already moves the whole line:
`app/area_layout.py` turns a handle drag into `LayoutModel.resize` and sets
every splitter from the result, and a refused drag puts them back. What is
left here is the rest of the drag (Shift, Escape, the `WARNING` line at a
neighbour's minimum, from `PL-RQT1` Q3), corner drags to split and join,
swap, and Workspace tabs. `AreaLayout.set_model` already rebuilds the
splitters when the tree changes shape, so a split, join or swap reaches the
screen through it.


## Built 2026-10-19: the Area menu, the corner drag and the border drag

`#1618` lands the first three parts and leaves this item open for the fourth.

- **The Area menu** (`PL-MS34` Q2). Each Area's header ends in an `AreaMenu`
  with Split left and right, Split top and bottom, Join with each neighbour,
  Swap with every other Area, and Close Area. Each entry is worked out by
  asking `LayoutModel` for the layout it makes. An entry the model or the
  Area's size refuses is shown disabled, with the reason as its tooltip.
  `LayoutModel.rectangle` and `LayoutModel.neighbours` are new for it.
- **The corner drag** (`PL-30L5`). Each corner is a 16 px zone with a cross
  cursor and a MUTED grip shown while the pointer is in that Area. A drag
  inside the Area previews a split through the pointer, and a drag into a
  neighbour previews a join. Nothing changes until release, and Escape
  cancels. A refused split or join is drawn in WARNING and release does
  nothing.
- **The rest of the border drag** (`PL-RQT1` Q3). The adapter now works the
  drag out itself instead of Qt's splitter drag. The border stops where an
  Area beside a moved line reaches the least size Qt draws it at, and its
  line turns WARNING there. Shift moves one border alone
  (`LayoutModel.resize(..., alone=True)`), and Escape returns the layout to
  where the drag started. A drag the model refuses now stops at the farthest
  place it allows, where it used to change nothing.

**Placeholders decided here** (look, wording and placement, project owner
2026-10-18). The menu's wording. "Join with" keeps this Area's View. Close
gives the place to the first neighbour that shares a whole edge. The grip is
drawn in opaque MUTED rather than at 40% alpha, so it meets SC 1.4.11's 3:1.
The header has 16 px side margins so a corner zone never takes the chooser's
or the menu's click.

**What is left: the Workspace tab strip** (`PL-QW1Z`), with the lifecycle
from `PL-WV9K` and "Pin current run" on the tab. It waits on two things.
`PL-TH35` builds the Wash-in and Parameters Views that the shipped
Workspaces name, so the dashboard can open on them. `PL-7Z84` (`#1614`)
gives a Workspace its pinned run. The fourth part also wires a
`WorkspaceSet` into the dashboard, since nothing holds one yet. The rewritten
`verify:` names that part's test.
