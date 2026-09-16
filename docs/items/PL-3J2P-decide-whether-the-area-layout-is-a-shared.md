---
id: PL-3J2P
title: Decide whether the area layout is a shared-vertex graph or a nested-splitter tree before the Qt layout work starts, because ROADMAP item 34 already specifies aligned-border dragging, four-way corner operations and arbitrary area swap, and a QSplitter tree makes all three expensive
priority: P2
effort: S
status: done
classes: planning
feature: interface-areas
touches: ROADMAP.md, docs/
added: 2026-09-16
closed: 2026-09-16
pr: 623
verify: python3 tools/doc_check.py check && grep -qF 'The layout is a nested-splitter tree, and Blender' ROADMAP.md
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

---

## Recommendation, 2026-09-16: the tree, behind a layout interface of our own

This reverses the recommendation the first two drafts of this item carried. The
project owner asked directly whether the choice is a preference or a real
trade-off, and weighing the cost side properly changes the answer.

**There is a real trade-off, and it is ownership.** A shared-vertex planar
subdivision is not a few hundred lines of geometry; it is a few hundred lines of
geometry plus the cases that make it correct — minimum-size propagation
cascading across every area touching a moved vertex column, join validity when a
shared edge does not span both areas, and the degenerate states reachable by
dragging one border past another. Blender carries real code for each. Every bug
in ours is a layout a learner can enter and not leave, in code that is not the
science, maintained forever by one person.

**The payoff is smaller here than in Blender, for a specific reason.** Blender
is a professional tool re-tiled constantly across wildly different tasks. A
resident picks a workspace tab and leaves it. The graph buys *authoring*
fidelity, which this audience exercises rarely; what they exercise constantly is
the *result*, which both representations deliver identically.

**And the default layout this project specified is already a tree.** Item 34's
"central graph of the compartments with the other views arranged around it" is
an outer split into three bands with the middle band split into three columns.
The top and bottom bands span the full width, so no border has a perpendicular
partner to come apart from. The junction problem does not arise in our own
stated default.

**What would falsify this** — stated before building, per
`.claude/rules/expert-review.md`. The graph wins the moment a wanted layout puts
a border running the full width or height *past* a perpendicular one: a 2×2 or
3×3 grid of views. That is the tell, and it is measurable once the first real
workspaces exist. It is not measurable now, which is the argument against paying
for the graph now: no one knows whether the maintenance workspace wants a grid,
and item 36's catalogue is unscoped.

**The condition that makes this safe to defer**, and the half that is not
optional: a `LayoutModel` of our own owns split / join / resize / swap and
layout persistence, with `QSplitter` behind it as an implementation detail. No
widget calls `saveState()`, no widget reaches for a parent splitter, no layout
state lives in a widget. `PL-LH18`'s path-scoped rule already requires views to
be interchangeable rather than merely movable, which is most of this; what this
adds is that the *container* is also behind an interface. Without that
condition the recommendation flips, because the tree stops being reversible.

**Not decided here.** This is a recommendation to the project owner, not a
decision taken. `ROADMAP.md` item 34 and § "v0.4.26" Required scope item 2
already name nested `QSplitter`s, so adopting this changes nothing in the
roadmap except to record why; adopting the graph changes both.


---

## Provisional direction 2026-09-16: the nested-splitter tree, pending research

**Reopened 2026-09-16, deliberately.** This was briefly written up as a closed
decision. The project owner reversed that on method, and is right: "I think that
decision is correct, but I don't like making a rigid decision like that off the
cuff before doing research on how something I know behaves like I want, actually
works." The evidence below is a targeted read of two functions, not a study of
the interaction model they sit in — enough to form a direction, not enough to
close. `PL-FTP5` is the research; this item decides after it.

**The direction, and the owner's own reading of it.** The owner
said "Splitter tree is what I want, And I'm pretty sure that's what blender
does" - and on the source, they are right, where the first two drafts of this
item and the comparison artifact built alongside it were wrong.

**What the source actually says.** `screen_geom_select_connected_edge`
(`source/blender/editors/screen/screen_geometry.cc`) is the default border drag.
It flood-fills from the dragged edge and flags the maximal **connected
collinear** chain - collinearity alone is not enough, the edges must also be
connected. A layout built by successive splits puts most borders in their own
chain, so the default feel is a splitter tree's. Two borders sharing a
coordinate but separated by an area spanning across them move independently, and
Blender treats that as a permitted state, not a broken one.

The two behaviours a tree cannot express are both opt-in:

- `screen_geom_select_extended_edge` takes every vertex within
  `EDGE_ALIGN_TOLERANCE` of the dragged coordinate regardless of connectivity.
  It runs only under an explicit extend flag - `screen_ops.cc` guards it with
  `if (md->can_extend && extend)`, so it is not the default path.
- `screen_geom_edge_aligned_merge` snaps near-aligned borders onto one
  coordinate and fuses them, after which they are one chain permanently.

**Where this item was wrong.** It framed the tree's independent borders as a
failure mode ("come apart", drawn in alarm red in the artifact) and the graph's
unified drag as Blender's ordinary behaviour. It is the other way round: the
tree matches Blender's default, and the graph buys two deliberate extras. The
recommendation happened to land on the tree anyway, on cost-of-ownership
grounds, but it got there past a wrong description of the alternative.

**What the research has to check before this closes.** Whether extend-drag or
snap-merge is load-bearing in the interaction model rather than an accessory —
which is a question about how the borders, corner actions and area operations
work *together*, and cannot be answered from these two functions alone. If the
prose sources or a wider read show either is central to how a layout is
actually built, this direction is wrong and the graph wins.

**Recorded in** `ROADMAP.md` item 34, with the correction and the reversibility
condition (the container behind a layout model of our own, so no view knows
`QSplitter` exists).


---

## DECIDED 2026-09-16: the nested-splitter tree

The direction this item carried survived the research it was blocked on. It was
tested to be falsified, not confirmed, and the evidence is in
`docs/interface-provenance.md` rather than restated here.

### (a) Are extend-drag and snap-merge load-bearing? No. Both are opt-in.

Read end to end rather than as two functions, and both mechanisms are now named
precisely:

- **Extend-drag is the Shift key.** In `screen_ops.cc`, the area-move operator's
  interactive entry point passes `event->modifier & KM_SHIFT` as its `extend`
  argument; the non-interactive `exec` path passes `false`. A helper exists so
  the user can toggle extension *mid-drag*, which is itself the clearest
  evidence it is a mode entered rather than the default.
- **Snap-merge is a separate operator.** `screen_geom_edge_aligned_merge` has
  exactly one caller: `SCREEN_OT_edge_merge` ("Merge aligned area edges"). It is
  not part of any drag. It appears in one place in the interface - the area
  border's right-click menu - and only when the edge qualifies.

### (b) What is a user expected to do to build a layout?

The border context menu (`SCREEN_OT_area_options`, "Operations for splitting and
merging") is the complete inventory: horizontal split, vertical split, join in
either direction, swap the two areas, and conditionally merge the edge. The
corner action zone is a modal drag whose direction and threshold select join or
split, with a modifier for swap. **Nothing in the documented workflow leans on
four-way corner operations**, which is what would have overturned this.

### (c) The count: 0 of 11, and 0 of 32

Threshold written down before counting, per `.claude/rules/expert-review.md`; it
is reproduced in `docs/interface-provenance.md` with the rest of the method.
Measured from Blender's shipped startup data rather than from Manual
screenshots.

| | pre-registered (11 defaults) | extended (21 template workspaces) |
|---|---|---|
| non-slicing - a tree **cannot express** it | **0** | **0** |
| contains a four-way junction | 1 (Shading) | 1 (inherited copy) |

Pre-registered rule: *zero non-slicing and at most one of eleven junctions
confirms the tree.* It landed exactly there, and the extended set - the
templates built for tasks furthest from the default - found nothing further.

### What it costs, stated exactly

One thing, and it is bounded. At a four-way junction Blender's two crossing
borders are each a single connected collinear chain, so dragging either moves
its whole length. A slicing tree can preserve **one** of the two as a single
handle and never both; all four decompositions of the Shading screen were
enumerated and each loses exactly one.

**The fix is not the graph.** It is for the layout model to resolve, on a drag,
the set of handles collinear and adjacent to the one being dragged, and move
them together - a query over the tree rather than a change of representation.
`PL-C842` carries it as part of the model's shape.

### One supporting argument did NOT survive, and the decision is restated without it

The pre-registration named the condition that would make the count the wrong
measurement: *the shipped defaults are the wrong proxy if Blender chose them to
be teachable rather than to exercise the representation.* **That condition
fires.** It was found by trying to falsify the convenient answer rather than to
confirm it.

The hypothesis was that split being full-span and join requiring a full shared
edge would confine a user to slicing layouts. Split is full-span - `area_split`
puts its new vertices on the area's own edges - but **join is not so confined,
and one ordinary join leaves the slicing class**. Five full-span splits produce
six areas including a left column in two parts; those two share a full edge, so
joining them is admitted, and the result is the five-area pinwheel that no
sequence of full-span cuts can produce. Six ordinary operations.

Two further findings the same way: `area_getorientation` requires a
perpendicular overlap of only `min(tolerance, extent of A, extent of B)`, so
**partial neighbours can be joined** and `screen_area_join_ex` trims the
overhang; and every aligned join runs `BKE_screen_remove_double_scrverts` over
the whole screen, so **four-way junctions are produced as a matter of course**
by joining rather than arising by coincidence.

So the claim that the graph buys expressiveness Blender's own model never
reaches is **false**. A splitter tree is strictly less expressive than Blender's
representation, not merely differently organised.

### Why the tree is still the decision

The argument that survives is narrower than the one this item started with, and
it is worth stating in the weaker form rather than pretending the count settled
more than it did:

1. **Blender's designers never used it.** Zero non-slicing layouts in 32
   shipped workspaces, by people who had the capability available and are
   expert in the tool. Reachable-but-never-shipped is weak evidence that the
   capability matters; it is not no evidence.
2. **The audience differs in the way that matters.** Blender is re-tiled
   constantly across wildly different tasks by professionals authoring layouts.
   A resident picks a workspace and leaves it. The graph buys *authoring*
   generality; what this audience exercises is the *result*, which both
   representations deliver identically.
3. **The tree's limitation surfaces as a refusal, not as a wrong value.** With
   a splitter tree the pinwheel is simply not offered - the join is unavailable
   between panes in different splitters. That is a visible interface
   limitation. It produces no wrong clinical number, so it is not a safety
   question, which is the only kind that would force the expensive answer.
4. **The cost of the graph falls on one person forever.** Minimum-size
   propagation across every area touching a moved vertex column, join validity,
   the degenerate states reachable by dragging one border past another. Every
   bug in ours is a layout a learner can enter and not leave, in code that is
   not the science.

### What would overturn it

Sharper than before, because the expressiveness question is now settled and only
the need is open: **a workspace this project actually wants that is
non-slicing.** Item 36's editor catalogue is where that would appear. If one
does, this is a representation change rather than a tweak, so reopen this item
rather than working around it.

A second, cheaper trigger: if learners are observed trying to join two panes
and finding it unavailable. That is the tree's one visible limitation, and it
is measurable once there are learners.

### Recorded in

`ROADMAP.md` item 34, and `docs/interface-provenance.md` § "The measurement:
what Blender's own shipped layouts actually contain".
