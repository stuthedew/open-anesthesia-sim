---
id: PL-C842
title: Decide whether the layout container sits behind a layout model of our own with QSplitter as an implementation detail, deferred by the project owner until the Blender deep dive shows how Blender actually separates container from view
status: blocked
touches: ROADMAP.md, src/anesthesia_sim/app/
added: 2026-09-16
blocked-by: PL-FTP5
verify: python3 tools/doc_check.py check && grep -qF 'The container sits behind a layout model of this project' ROADMAP.md
---

**Problem.** Decide whether the layout container sits behind a layout model of our own with QSplitter as an implementation detail, deferred by the project owner until the Blender deep dive shows how Blender actually separates container from view

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
