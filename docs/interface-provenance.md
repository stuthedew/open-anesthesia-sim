# Interface provenance: what this project studied of Blender, and what it took

`ROADMAP.md` planned-milestone item 34 takes Blender's window system as the
model for this application's interface: a window subdivided into
non-overlapping resizable **areas**, each holding one **editor**, grouped into
named **workspaces**. This file is the record behind that decision — what was
read, under what rules, what it established, and where this project
deliberately does something else.

It exists because the alternative is that a session meeting the question cold
either re-derives a full research round or guesses. Both have happened. It is
also the answer to a question the project owner asked directly on 2026-09-16:
whether there is a good-faith way to study Blender's architecture for
inspiration. There is, and the rules are narrow enough to be worth writing
down once.

`docs/ARCHITECTURE.md` maps *this* codebase's layering and is the place to look
for where our own code goes. This file is about the outside model we studied,
not about our tree.

## The study protocol

### Reading is not a restricted act; copying, translating and porting are

Blender's source files carry `SPDX-License-Identifier: GPL-2.0-or-later`, and
the binary as a whole ships under GPL-3.0-or-later. This project is Apache-2.0
(`LICENSE`, `pyproject.toml`). The two are not compatible in the direction that
matters: GPL code cannot be absorbed into an Apache-2.0 tree without making the
stated license wrong.

What the GPL restricts is narrower than "using Blender to learn from", though,
and the distinction is the whole basis of this study. GPLv2 § 0 puts activities
other than copying, distribution and modification outside the license's scope;
§ 2 is what covers modification, and it names translation into another language
explicitly. So:

- **Reading the source to understand it is unrestricted.** It is not one of the
  acts the license reaches.
- **Copying, adapting, transliterating or porting it is restricted**, and
  nothing of the sort has been done here or may be done later. Rewriting a C++
  function in Python is translation, not inspiration.
- **Describing what was read, in this project's own words, is the deliverable.**
  Everything in the architecture account below was written that way, with file
  and function names given so that a later session can re-check a claim against
  the source instead of trusting this file.

Identifiers — file paths, function names, struct and field names — are given
throughout. A name is what makes a claim checkable, and naming the function
that implements a behaviour is not reproducing its expression.

**Read the header of the file you are actually reading.** The tree is mixed,
which the usual shorthand "Blender is GPL" hides. Counted across the checkout
used for this study: 2,092 files declare `GPL-2.0-or-later`, 10 declare
`Apache-2.0` (they are unit tests), and 2 declare `GPL-3.0-or-later`
(`source/blender/editors/uvedit/uvedit_clipboard_graph_iso.cc` and its header).
Blender's own README states the position exactly — the work as a whole is
GPL-3.0, and individual files may carry a different but compatible license.
Every file this study read carries `GPL-2.0-or-later`.

### The prose is the encumbered half, not the source

This is the constraint most likely to be got backwards, because the
weaker-sounding license is the one that actually reaches this tree.

The **Blender Manual** and the **Blender Developer Documentation** — which
includes the Human Interface Guidelines — are both licensed **CC-BY-SA 4.0**,
a share-alike license. Pasting their prose into `ROADMAP.md` or into `docs/`
*is* copying, where reading GPL source is not. So the rule reverses between the
two kinds of source:

| Source | Licence | What this project may do |
|---|---|---|
| Blender source code | GPL-2.0-or-later (per file) | Read freely. Never copy, translate or port. |
| Manual, Developer Docs, HIG | CC-BY-SA 4.0 | **Paraphrase and cite. Never paste.** |

Attribution for the documentation goes to the Blender Documentation Team and
the Blender Developer Documentation Team respectively, with a link. Both
licence statements were re-confirmed on 2026-09-16, by the weaker of the two
routes below — a search engine rather than the pages themselves.

Blender's own Copyright Rules handbook draws the same line from the other side:
it bars copyrighted elements of other software from entering Blender, while
encouraging designs that build on Blender's own design history. Studying the
design and re-expressing it is the behaviour that document asks for; lifting
assets or prose is the behaviour it refuses.

### What this project attributes

Not legally required for ideas — 17 U.S.C. § 102(b) excludes procedures,
processes, methods of operation and concepts from copyright — but this
project's own provenance standard asks for it, and it is the answer to the
spirit of the question rather than the letter.

`README.md` and `ROADMAP.md` item 34 record that the workspace / area / editor
model is modelled on Blender's, studied from its published source and design
documentation. The three words *Area*, *Editor* and *Workspace* are Blender's
and are used here for the same three things deliberately, so that this
project's code and its roadmap do not drift into a private vocabulary.

Where the abstraction is pitched matters to more than manners. *Tiled
non-overlapping panes, each hosting a swappable view kind, saved as named
workspaces* is a method of operation. A transliterated `bScreen` / `ScrArea` /
`ARegion` struct graph would be structure, and **Computer Associates Int'l v.
Altai**, 982 F.2d 693 (2d Cir. 1992) holds that non-literal structure can be
protected, giving the abstraction-filtration-comparison test for telling which
is which. The higher the abstraction carried across, the safer — and, as it
happens, the more useful, because what is worth taking from Blender here is the
shape of the boundary rather than its field layout.

### How this study was conducted, and where it could not reach

Recorded because `.claude/rules/citing-sources.md` makes the same demand of a
stored constant: name **which route** you took to a source and **how deeply**
you read it, so that a citation read at the source and one taken from a search
summary are not indistinguishable later. That rule is scoped to the data files,
but its reasoning applies here unchanged, and this study's two halves have very
different evidence grades.

**The source: read directly, in full.** `blender/blender` was cloned at commit
`931bb2e7` (Blender 5.3) and read as implementation, not only as headers —
`area.cc`, `screen_edit.cc`, `screen_ops.cc`, `screen_geometry.cc`, the
`space_*` directories, and the blend read/write paths. Every claim in the
architecture account below names the file and the function behind it. This is
first-hand evidence and the strongest thing in this document.

**The shipped layouts: measured, not eyeballed.** The count below was taken
from Blender's own shipped startup data rather than from screenshots in the
Manual. See that section for how.

**The prose: reached only through a search engine, and that is a real
weakness.** Every `blender.org` host — `developer.blender.org`,
`docs.blender.org`, `www.blender.org`, `archive.blender.org`,
`projects.blender.org` — is refused by this environment's egress proxy, as is
`web.archive.org`. The Manual and the Developer Documentation could not be
opened. What the "stated rationale" section below reports therefore rests on
search-engine summaries of those pages, which `.claude/rules/citing-sources.md`
warns is the thing likeliest to be mistaken for a reading. **Every claim in
that section carries its grade**, and a claim graded thin or second-hand should
be re-checked against the page itself by any session that can reach it. Where
the honest answer was that Blender does not appear to state something, that is
what is recorded, rather than a confident summary assembled from general
knowledge.

## The measurement: what Blender's own shipped layouts actually contain

The architectural fork this project had to decide was whether its layout is
stored as Blender's **shared-vertex graph** — areas naming four corner points,
neighbours sharing them — or as a **nested-splitter tree**, which is what Qt
hands you and what `ROADMAP.md` item 34 already named. `PL-3J2P` is the item
that decided it.

Arguing it from the two representations' expressive power is a trap, because
the graph is strictly more expressive and the argument then ends before it has
weighed anything. The question worth answering is narrower: **does Blender, in
the layouts it actually ships, use the power the graph has and the tree does
not?** That is a count, and it was taken rather than estimated.

### The threshold, stated before the count

Per `.claude/rules/expert-review.md` § "Name the number that would change your
mind, then go and count it", the thresholds below were written down before any
counting code was run:

- **A — non-slicing.** Is the arrangement expressible as recursive subdivision
  by full-span cuts (a *slicing floorplan*)? The minimal non-slicing
  arrangement is the pinwheel: five rectangles with no full-span cut anywhere.
  A non-slicing screen is one a splitter tree **cannot represent at all**.
  *Two or more of eleven and the tree is wrong outright.*
- **B — cross junction.** Does any interior point have four areas meeting at
  it? This *is* expressible in a slicing tree — two cuts at the same coordinate
  — but it is not *represented*: the two collinear border segments become
  independent handles where Blender's share one vertex. *Zero non-slicing and
  at most one of eleven here, and the tree is confirmed; four or more and the
  tree is expressible but behaviourally wrong at a configuration Blender uses
  routinely.*
- **C — drag fidelity.** Does any decomposition into splitters reproduce
  Blender's border-drag behaviour exactly?

### How it was measured

Blender's shipped workspaces live in `release/datafiles/startup.blend`, which
is stored in Git LFS and arrives as a pointer stub on an anonymous clone. The
data was instead read from the `bpy` package on PyPI — Blender built as a
Python module, **version 5.0.1**, which embeds the same startup data — by
enumerating `bpy.data.screens` and each area's rectangle. Each screen was
reduced to an exact integer grid, then tested for all three properties, with
every possible slicing decomposition enumerated so that the tree was judged on
its best case rather than on the first decomposition tried.

Two honest limitations. The `bpy` build is **5.0.1** where the source read was
**5.3**, so the layouts are one minor version behind the code; the default
workspace set has been stable across that range, but it is a gap. And a
rectangle-level reconstruction recovers the *arrangement*, not Blender's
vertex and edge objects themselves, which RNA does not expose.

### The result

Against the pre-registered denominator — Blender's eleven default workspaces:

| | count |
|---|---|
| **A** non-slicing (a splitter tree cannot express it) | **0 of 11** |
| **B** contains a cross junction | **1 of 11** (Shading) |
| **C** no splitter decomposition reproduces the drag | **1 of 11** (Shading) |

Extended, as a secondary check never folded into the pre-registered figure, to
the twenty-one workspaces in Blender's five shipped application templates (2D
Animation, Sculpting, Storyboarding, VFX, Video Editing) — the layouts built
for tasks furthest from the default, and so where a non-slicing arrangement
would appear if anywhere: **0 of 21 non-slicing, 1 of 21 with a cross
junction**, and that one is the same four-editor arrangement inherited from
the Shading workspace.

**Across all thirty-two shipped workspaces, not one uses a layout a nested
splitter tree cannot express.**

The single exception is worth stating precisely, because it is the whole of
what the tree costs. The Shading workspace puts four editors in a 2×2 block —
image editor and node editor along the bottom, file browser and 3D viewport
along the top. In Blender the two borders crossing at the centre of that block
each consist of two edges sharing the centre vertex, so each is one *maximal
connected collinear chain* and dragging either moves its whole length. A
slicing tree can preserve **one** of the two as a single handle, never both:
whichever cut it takes first spans the block, and the other becomes two
independent handles. This is not an artefact of a particular decomposition —
all four decompositions of that screen were enumerated and each loses exactly
one of the two.

So the count lands squarely on the pre-registered "confirmed" row, with one
named and bounded divergence rather than none.

### What would have made this the wrong measurement

Also stated before the count: the shipped defaults are a proxy for "layouts a
professional tiling interface actually needs", and they would be the wrong
proxy if Blender chose them to be *teachable* rather than to exercise the
representation. The check on that is whether the interaction model *permits*
arrangements the defaults avoid — which is the next section's subject, and the
answer there is that it largely does not: the operations a user has reach only
a small distance beyond what the defaults show.

## What Blender's window system is

Read at `blender/blender` commit `931bb2e7` (Blender 5.3). Implementation, not
only headers. Described in this project's own words; every claim names the file
and function that carries it.

The centrepiece is the **boundary between the container and the view**, because
that is the part this project is actually buying. Everything else in this
section exists to locate that line.

### An area owns its rectangle; an editor owns no geometry at all

This is the cleanest thing in the design and the single most transferable.

`ScrArea` (`source/blender/makesdna/DNA_screen_types.h`) holds the geometry and
the identity: four corner vertices `v1`–`v4`, a `totrct` the header comments
describe as the rect bound by those four, `winx`/`winy`, the `spacetype` tag
naming which editor is active, a runtime `type` pointer to the registered
`SpaceType`, the live `regionbase`, and `spacedata` — the stack of editors this
area has previously held.

`SpaceLink` (`source/blender/makesdna/DNA_space_types.h`, the implicit base of
every concrete `Space*` struct) holds: list links, a `regionbase` the comment
describes as storage of regions for inactive spaces, the `spacetype` tag, a flag
and padding. **There is no rectangle, no size and no position on it.** An
editor's saved state cannot express where it is, because the struct has nowhere
to put it.

The nuance that keeps this honest: *regions* do have geometry — `ARegion` carries
a `winrct`. But a region's rect is **computed by the container**, in
`region_rect_recursive` in `source/blender/editors/screen/area.cc`, from the
area's rect and the region's declared alignment and size. The editor declares
what kind of region it wants and how big it would like to be; it never assigns a
rectangle. So the rule holds in the form that matters: **geometry flows
downward from the area, and never upward from the editor.**

### An editor cannot refuse a size, and the container's fallback is to hide

`ARegionType` (`source/blender/blenkernel/BKE_screen.hh`) carries `minsizex` /
`minsizey` and `prefsizex` / `prefsizey`. These are a **request, honoured where
it fits, and overridden by concealment where it does not.**

When `region_rect_recursive` cannot give a region its minimum — the area is too
narrow, or a sidebar would collide with one on the other side — it sets
`RGN_FLAG_TOO_SMALL` on the region and returns. Downstream, a region carrying
that flag is treated exactly as a hidden one: its `winrct` is collapsed to zero
extent, so it occupies no space and draws nothing.

There is no negotiation and no veto. An editor has no callback that can reject a
size or demand a different one; the container decides, and **its failure mode is
to make the content disappear rather than to refuse the layout.** That is a
reasonable answer for a 3D content tool and a directly unsafe one here, which
"What this project does differently" returns to.

### An editor is isolated by convention, not by construction

This is where the expectation the research set out to test was **falsified**, and
it is the most consequential correction in this document.

The expectation was that an editor genuinely cannot read its own position, its
neighbours, or what else is open — the property that would make
interchangeability structural rather than aspirational. It is not true. Editor
callbacks receive a `bContext`, and through it the window, the screen and every
area in it. Counted across the 21 `space_*` directories in the tree:

- **16 of 21 call `CTX_wm_area`**, reading their own area. Universal, and
  `space_view3d` does it 33 times.
- **11 of 21 call `CTX_wm_screen`**, reaching the screen that contains them.
- **10 of 21 iterate the screen's whole area list** (`screen->areabase` or
  `ED_screen_areas_iter`) — reading, and sometimes acting on, other open
  editors. `outliner_sync.cc` walks every area to synchronise selection between
  outliners; `node_select.cc` and several files in `space_view3d` do the same.
- **2 of 21 actively search the screen for another area of a chosen type** via
  `BKE_screen_find_big_area` — `space_text` looks up the largest text editor in
  the screen, and `space_view3d` the largest 3D viewport.

So Blender's editors are interchangeable because the *contract* does not depend
on position, not because the *API* prevents them from asking. The discipline is
real and mostly kept; it is not enforced. A project that wants the stronger
property has to build it deliberately — it is not something adopting this model
supplies for free.

### How a layout is built, and how far the operations reach

The question `PL-3J2P` had to answer was whether the two behaviours a splitter
tree cannot express are load-bearing in how a layout is constructed, or
accessories to it. Read end to end, they are accessories, and the mechanism is
specific enough to state exactly.

**The default border drag moves a maximal connected collinear chain.**
`screen_geom_select_connected_edge`
(`source/blender/editors/screen/screen_geometry.cc`) takes the axis of the
dragged edge, flags its two vertices, then repeatedly flags any edge that has
exactly one flagged endpoint *and* runs along that same axis, until nothing more
is reachable. Connectivity is required, not merely alignment: two borders that
share a coordinate but are separated by an area spanning across them are
different chains and move independently. Blender treats that as a permitted
resting state.

**Extend-drag is the Shift key.** In
`source/blender/editors/screen/screen_ops.cc`, the area-move operator's
interactive entry point passes `event->modifier & KM_SHIFT` as its `extend`
argument; the non-interactive `exec` path passes `false` outright. The extended
selection — `screen_geom_select_extended_edge`, which takes every vertex within
tolerance of the dragged coordinate regardless of connectivity — runs only when
that flag is set *and* `screen_geom_edge_can_extend` allows it. A helper,
`area_move_reinit`, exists so the user can toggle extension mid-drag, which is
itself the clearest evidence it is a mode the user enters rather than the
default.

**Snap-merge is a separate operator on a right-click menu.**
`screen_geom_edge_aligned_merge` has exactly one caller: `area_edge_merge_exec`,
the body of `SCREEN_OT_edge_merge` ("Merge Area Edge" / "Merge aligned area
edges"). It is not part of any drag. It appears in one place in the interface —
the area-border context menu built by `SCREEN_OT_area_options` ("Area Edge
Options") — and then only when `screen_geom_edge_can_extend` says the edge
qualifies. That menu is also the complete inventory of what a border offers:
horizontal split, vertical split, join in either direction, swap the two areas,
and conditionally merge the edge.

So the answer is unambiguous. **A layout is built by splitting, joining,
swapping and dragging borders; the two graph-only behaviours are a held modifier
and a conditional context-menu item.** The measurement in the previous section is
the other half of the same answer: not only are those behaviours opt-in, the
layouts Blender ships with do not depend on them.

### Persistence, and what happens when an editor is missing

A layout and its editors are saved by different owners. `bScreen` is an ID
block, written with the rest of the file; `SpaceType`
(`source/blender/blenkernel/BKE_screen.hh`) carries its own `blend_write` and
`blend_read_data` alongside its lifecycle hooks, so the layout layer delegates
each editor's serialization to that editor rather than knowing what is inside
it. This is the answer to "how does a workspace save without the layout code
knowing what an F_A/F_I chart is", and this project should copy it.

**What happens on read when the editor type is unknown is the finding that
matters, and it is not one to copy.**

`ED_area_and_region_types_init` in `source/blender/editors/screen/area.cc` looks
up `BKE_spacetype_from_id(area->spacetype)`. When that returns null — a file
naming an editor type this build does not have, because it was removed, renamed,
or comes from a newer Blender — it calls `area_init_type_fallback(area,
SPACE_VIEW3D)`. That helper's own comment describes it as setting up a known
space type in the event a file with an unknown space type is loaded. It
substitutes the **3D viewport**, silently. There is no error, no warning, and
nothing surfaced to the user; the only guard is a `BLI_assert` that the
substitution itself worked, and asserts compile out of release builds.

So: **Blender fails quietly here.** The area keeps its rectangle, fills with a
different editor than the file asked for, and the interface looks entirely
normal.

That is precisely the shape of failure this project already rejected on the Qt
side. `PL-C842` disqualified `QSplitter.saveState()` as a source of truth partly
because restoring a three-child state into a two-child splitter returns `True`
and produces a plausible-looking wrong layout rather than failing. Blender's
recovery path has the same property. `CLAUDE.md`'s safety-critical standard
prefers an obvious failure state to a plausible-looking number and treats stale
or mis-contexted presentation as a safety failure in its own right, so this is a
point where the precedent runs out and the project has to do something else.

### What survives a resize, a split, a join, and a swap

The swap case is the one item 34 depends on, and it holds, with a mechanism
worth knowing.

`ED_area_newspace` (`source/blender/editors/screen/area.cc`) changes an area's
editor. It searches `area->spacedata` for a stored `SpaceLink` of the requested
type. If it finds one, it **swaps the region lists** — the area's live
`regionbase` goes back onto the outgoing `SpaceLink`, and the stored one's
regions become live — and moves the found link to the head of the list. If it
finds none, `SpaceType.create` makes a fresh one. The outgoing editor's state is
**kept**, not freed, unless it is flagged temporary.

The mechanism is the interesting part: an editor's per-view state — pan, zoom,
scroll, panel open/closed — lives in its **regions**, and the regions travel with
the `SpaceLink`. The area holds one live region list at a time and the stack
holds the others. That is why switching an area to another editor and back
restores the view exactly, which is what `ROADMAP.md` item 34's "induction
workspace with the graph zoomed in" case needs.

Two caveats worth recording: the stack is **unbounded** — nothing evicts old
entries, so an area accumulates one stored editor per type it has ever held; and
`SpaceType.duplicate` is what decides how much of an editor's state a *split*
carries into the new area, so split fidelity is per-editor rather than a property
of the layout system.

### What an editor must implement

`SpaceType` is a vtable-as-data: metadata plus function pointers, registered once
at startup. The required core is small, and the best evidence for where the line
falls is not a null check but the simplest editor in the tree.

`space_script` (`source/blender/editors/space_script/space_script.cc`, 220
lines) registers: `spaceid` and `name` for identity; `create`, `free`, `init` and
`duplicate` for lifecycle; and two region types — a main window region and a
header — each with its own `init` and `draw`. That is a working editor.

Everything else `SpaceType` offers is optional and absent from at least one real
editor: `operatortypes`, `keymap`, `dropboxes`, `listener`, the context callback,
`blend_write` / `blend_read_data`, `foreach_id`.

One detail matters for this project's own contract: **the editor declares its own
header region.** The container does not supply a title bar and then hand the
editor a space beneath it; the editor registers a header region type alongside its
main one, with its own draw callback. A view's chrome is the view's business, and
the area only allocates the rectangle it is computed into.
