---
id: PL-C842
title: Decide whether the layout container sits behind a layout model of our own with QSplitter as an implementation detail, deferred by the project owner until the Blender deep dive shows how Blender actually separates container from view
priority: P2
effort: M
status: done
classes: planning
feature: interface-areas
touches: ROADMAP.md, src/anesthesia_sim/app/
added: 2026-09-16
closed: 2026-09-16
verify: python3 tools/doc_check.py check && grep -qF 'The container sits behind a layout model of this project' ROADMAP.md
---

**Problem.** Decide whether the layout container sits behind a layout model of our own with QSplitter as an implementation detail, deferred by the project owner until the Blender deep dive shows how Blender actually separates container from view

**Why it matters.** The container is the one piece of the area system every
view sits inside, so getting it wrong is not a local mistake: a view that knows
`QSplitter` exists is a view that cannot be moved, and a layout whose source of
truth is an opaque widget blob cannot be tested, reviewed, or made to fail
loudly when it no longer matches the application. `PL-25KS` builds the container,
so this wants answering before that item is worked.

**Decision needed.** Whether to accept the recommendation below - a pure-Python
`LayoutModel` as the source of truth, with `QSplitter` an implementation detail
behind one adapter module, and the four additions the Blender read produced
(border chains, a per-pane view stack, loud failure on an unknown view kind, and
the required display set held outside the model). The alternative is to let the
widget tree be the source of truth, which the measurement recorded below rules
out on this project's own standard. Answering it is the project owner's word on
a recommendation, not a fresh investigation.

**Where this came from.** `PL-3J2P` decided the layout is a nested-splitter
tree (project owner, 2026-09-16). It recommended, without deciding, that the
container sit behind a layout model of this project's own — owning split, join,
resize, swap and persistence, with `QSplitter` an implementation detail, so no
view calls `saveState()`, reaches for a parent splitter, or stores layout state
in itself.

**Deferred, deliberately** (project owner, 2026-09-16): "Let's defer 1 till
after we do the blender deep dive ... so we can actually see how they implement
rather than trying to make it up." The recommendation was reasoned from first
principles; Blender has a working answer, and reading it beats inventing one.

**What the deep dive has to come back with** for this to be decidable. Each is
a question about the container/view boundary, and `PL-FTP5` carries them as its
primary objective:

1. What does an area own and what does the editor own? The read so far says
   geometry and identity sit on `ScrArea` (four corner vertices, `totrct`,
   `winx`/`winy`) and editor state sits on `SpaceLink`, so an editor never
   stores its own rectangle. Confirm, and find where the line is crossed if it
   is.
2. How is an editor told its size, and can it refuse one? `ARegionType` appears
   to carry minimum sizes; establish whether a minimum is a request or a
   constraint the container honours.
3. Does an editor ever read its own position, its neighbours, or what else is
   open? If not, that is the interchangeability property with teeth, and it is
   what this project would be buying.
4. How is layout persistence separated from editor persistence? `bScreen` is an
   ID; `SpaceType` carries its own `blend_write`. Establish who writes what, and
   in what order.
5. What survives a resize, a split, a join, and an editor swapped out and back?
   `ScrArea.spacedata` keeps previously-open editors, so the answer for the last
   one is "its state" — confirm the others.
6. What must an editor implement for the container, and what is optional?
   `SpaceType`'s required-versus-optional split is the answer, and it is also
   `PL-TH35`'s Editor contract.

**Done when.** `ROADMAP.md` item 34 records whether the container sits behind a
layout model of our own, with the evidence from Blender's implementation behind
the answer rather than a first-principles argument.

**Blocks nothing yet, gates one thing.** `PL-25KS` (the dashboard port) builds
the container, so this wants answering before that item is worked.


---

## Direction 2026-09-16: a layout model of our own — settled on the negative,
## open on the shape

**Two halves, and only one of them is closed.** The *negative* is settled and the
research cannot overturn it: `QSplitter.saveState()` will not be the source of
truth, because the measurement below is a fact about Qt rather than about
Blender. The *positive* — the shape the model takes, what a pane owns, what a
view must implement — is open, and `PL-FTP5` is what informs it. Recorded this
way after the owner's correction on `PL-3J2P`: a targeted measurement supports a
direction, not a closed design.

**Taken on rather than handed back.** The project owner asked for this one to
be taken off their desk: "that architecture stuff ... is really what I need your
help with. That's not something I really can make an informed decision on."
`CLAUDE.md` delegates exactly this, so the deferral to the Blender read is
withdrawn — and it turned out not to be needed, because the argument never
depended on Blender. What still wants the Blender read is `PL-TH35`, the
*content* of the Editor contract, where their experience beats reasoning.

**What settled it: measuring `QSplitter.saveState()` rather than arguing about
it.** Run against the project's own PySide6:

```
QT_QPA_PLATFORM=offscreen uv run python -c "
from PySide6.QtWidgets import QApplication, QSplitter, QWidget
from PySide6.QtCore import Qt
app = QApplication([])
s = QSplitter(Qt.Horizontal)
for n in ('a','b','c'):
    w = QWidget(); w.setObjectName(n); s.addWidget(w)
s.resize(600, 400); s.setSizes([200, 200, 200])
blob = s.saveState()
print(len(blob), 'bytes', bytes(blob)[:24])
s2 = QSplitter(Qt.Horizontal)
for n in ('a','b'):
    w = QWidget(); w.setObjectName(n); s2.addWidget(w)
print('restore into 2 children:', s2.restoreState(blob), s2.sizes())
"
```

Three findings, each one disqualifying on its own:

1. **It is 35 opaque bytes.** A `QByteArray` of packed integers — the three
   `200`s appear as `\x00\x00\x00\xc8`. Not inspectable, not diffable, not
   reviewable in a pull request. Shipped default workspaces would be binary
   blobs in a tree where every other shipped parameter is a validated,
   versioned JSON file.
2. **It cannot say which view is in which pane.** It encodes sizes, a child
   count and a couple of flags, and nothing about contents. Item 34's
   workspaces are *named task layouts* — induction with the graph zoomed,
   maintenance big-picture — which is exactly the view-to-pane mapping
   `saveState()` does not carry. So it is not sufficient on its own; a second
   structure has to hold that mapping, and then two sources of truth can
   disagree about the same layout.
3. **Restoring a mismatched tree silently succeeds.** Restoring a three-child
   state into a two-child splitter returned `True` and produced `[318, 318]`.
   No exception, no `False`, no warning. `CLAUDE.md` requires an obvious failure
   state in preference to a plausible-looking wrong one, and treats stale or
   mis-contexted presentation as a safety failure in its own right. A workspace
   format that cannot report "this no longer matches the application" fails that
   directly.

**Three further reasons, none of which needed the measurement.**

- **Testability.** An opaque `QByteArray` cannot be asserted against. A model
  makes "after joining panes 2 and 3 the layout has three panes in this
  arrangement" an ordinary unit test, headless, with no `QApplication`.
- **Break-out windows.** Item 34 wants an area taken into its own top-level
  window, itself tiled. `saveState()` is per-splitter; a multi-window layout has
  no single call to save. A structure spanning windows is required either way —
  the only question is whether it is designed or accreted.
- **House discipline.** `tools/import_boundary_check.py` already confines the UI
  toolkit by declared boundary with the reason written beside it, including
  "the toolkit the interface left, out of everything". This is the same rule one
  level further out, and the same tool can enforce it.

**What this is not.** Not a reimplementation of `QSplitter`. Qt still draws the
panes, drags the handles and honours minimum sizes; the model is the source of
truth and Qt is the renderer. The shape:

- `LayoutModel` — pure Python, no Qt import. A tree of `Split(orientation,
  children, sizes)` and `Pane(pane_id, view_kind)`, with `split`, `join`,
  `resize`, `swap`, `set_view`, and `to_dict()`/`from_dict()` over versioned
  JSON.
- One adapter module — the only place that imports `QSplitter`. Builds the
  widget tree from the model, and writes sizes back on `splitterMoved`.
- Views are `QWidget`s registered by `view_kind`. A view never sees a splitter,
  never calls `saveState()`, never stores its own geometry.

**Robust to `PL-3J2P` either way.** If the research overturns the splitter tree
and the layout becomes a shared-vertex graph, a layout model of our own becomes
*more* necessary rather than less — `saveState()` cannot express a graph at all.
So this direction does not depend on that one.

**Recorded in** `ROADMAP.md` item 34, as a direction rather than a settled
design. `PL-FTP5`'s six container/view questions feed the shape here and the
contract in `PL-TH35`.


---

## RECOMMENDATION 2026-09-16, with the Blender read behind it

**Yes - and the research strengthened the case rather than merely confirming
it.** The six container/view questions are answered in
`docs/interface-provenance.md`; this is what they mean for the shape.

### The finding that changes the recommendation

Going in, the expectation was that a layout model of our own would mostly
*re-implement* what Blender gets for free, and the argument for it was
testability and the `saveState()` measurement. That is not what the read found.

**Three properties this project needs are ones Blender does not have.** They are
not inherited by adopting the model; they have to be built, and a layout model of
our own is where they live:

1. **Loud failure on an unknown view kind.** Blender silently neutralises an
   area whose editor type is not registered, then rewrites it into a 3D viewport
   at the next refresh, with nothing naming the substitution. The tell that this
   is an oversight rather than a considered choice: thirty lines above it, the
   analogous *region* case emits a warning naming what it discards. Stated
   precisely, because the first reading of this overstated it: Blender *does*
   warn when the file came from a newer version - a persistent status-bar
   indicator and a save dialog - but that is a **file-level** warning saying
   data may have been lost, never that this pane now shows something other than
   what was saved; and an editor missing for any other reason trips it not at
   all. This is the same silent-success shape that disqualified
   `QSplitter.restoreState()`, so **neither Qt nor Blender supplies the
   pane-level behaviour the safety standard needs.**
2. **A required value is never hidden to make room.** Blender's answer when a
   region will not fit is a flag and a collapse to zero extent. And there is no
   minimum-size contract to appeal to: `minsizex`/`minsizey` occur exactly once
   in the tree - the declaration - and nothing reads them.
3. **Isolation with teeth.** Editors are isolated by convention, not by
   construction: 10 of 21 editor directories walk the screen's whole area list,
   and 2 search it for another area by type. A view that is *handed* what it
   draws and given no route to the container is a deliberate narrowing.

### The shape

Mostly as sketched, with four additions the research produced. Named here as a
recommendation to react to, not as a design to implement.

- **`LayoutModel`** - pure Python, no Qt import. A tree of `Split(orientation,
  children, sizes)` and `Pane(pane_id, view_kind)`, with `split`, `join`,
  `resize`, `swap`, `set_view`, and versioned JSON serialization.
- **A view is given its rectangle and owns no geometry.** Straight from Blender,
  where the base struct for every editor's state has nowhere to put one.
- **NEW - border chains.** A `borders()` query returning, for any handle, the
  set of handles collinear and adjacent to it, so a drag moves the whole border.
  This is the one behaviour the tree loses against Blender (`PL-3J2P`), and it
  is a query over the tree rather than a change of representation.
- **NEW - a pane stack.** Each pane keeps the views it previously held, so
  switching a pane to another view and back restores the first one's state.
  Blender does this by swapping *region* lists; the property to copy is that the
  outgoing view's state is kept rather than destroyed. Blender's stack needs no
  cap because it is bounded by construction - at most one entry per editor type
  - and the same holds here if a pane stores at most one instance per
  `view_kind`.
- **NEW - loud load failure.** Deserializing a layout naming an unknown
  `view_kind` fails visibly. It does not substitute, and it does not drop the
  pane.
- **NEW - the required set is not the model's to place.** `docs/MODEL.md`'s
  unconditional displayed outputs sit outside the area system, so the model
  never has a state in which one of them is collapsed or removed.
- **One adapter module** - the only place importing `QSplitter`. Builds the
  widget tree, writes sizes back on `splitterMoved`, and applies a border-chain
  drag across the several splitters it spans.
- **Views registered by kind.** A view never sees a splitter, never calls
  `saveState()`, never stores its own geometry.

### Where the evidence is thin, stated plainly

- **The contract's content is not settled here, and should not be.** `PL-TH35`
  is where the Editor contract is written, validated against two views that
  already exist. What this read contributes to it is the required/practised/dead
  three-way split in `docs/interface-provenance.md` - and the warning that
  Blender's own contract accumulated hooks nothing implements and a field
  nothing assigns.
- **Split fidelity is per-view, not a layout property.** Blender delegates it to
  each editor's `duplicate`. What a split of our panes should copy is therefore a
  question this recommendation does not answer.
- **Break-out windows are still unmodelled.** Item 34 wants an area taken into
  its own top-level window. Blender's answer is a second screen under the same
  workspace, with the per-window relation held separately. Nothing here designs
  that, and it is the part most likely to change the model's shape.
- **The unbounded pane stack is Blender's choice, not a validated one.** Nothing
  evicts. Whether that is right here is undecided.

### CLOSED 2026-09-16, on the standing delegation

Held open at `needs-decision` for a few hours first, on the reasoning that the
session writing a recommendation is not the one to accept it. `docket check
--verify` disagreed and was right: this item's `verify:` command specifies that
`ROADMAP.md` item 34 records the container sitting behind a layout model of this
project's own, and item 34 now records exactly that, with the Blender evidence
behind it rather than a first-principles argument - which is this item's "Done
when", met. An open item whose command already passes is the shape that would
let `docket verify` ACCEPT a branch doing none of the work, so leaving it open
was costing a live check its meaning.

Closing it is also what the project owner asked for when they handed the
architecture call over, which the section above records. `CLAUDE.md` delegates
exactly this. The decision is therefore taken rather than proposed - **the
container sits behind a layout model of this project's own** - with the
recommendation above as the record of what was decided and why.

**Reversing it costs one sentence.** Nothing has been built against it; the
first code it binds is `PL-25KS`'s container. If the project owner wants the
widget tree to be the source of truth after all, reopen this and item 34's
paragraph goes with it.
