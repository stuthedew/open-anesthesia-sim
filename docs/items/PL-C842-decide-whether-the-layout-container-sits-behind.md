---
id: PL-C842
title: Decide whether the layout container sits behind a layout model of our own with QSplitter as an implementation detail, deferred by the project owner until the Blender deep dive shows how Blender actually separates container from view
status: untriaged
touches: ROADMAP.md, src/anesthesia_sim/app/
added: 2026-09-16
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
