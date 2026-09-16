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
arrangements the defaults avoid.

**It does, and this escape clause fires. A non-slicing layout is reachable in
six ordinary operations.** This was found by trying to falsify the opposite —
the hypothesis was that split being full-span and join requiring a full shared
edge would confine a user to slicing layouts — and the hypothesis is wrong.

Split is indeed always full-span: `area_split`
(`source/blender/editors/screen/screen_edit.cc`) inserts its two new vertices on
the *area's own* left and right edges, so a cut spans exactly that area and
never reaches past it. Splitting alone therefore cannot leave the slicing class.

**Join is what leaves it.** Start from one area and make five full-span splits,
arriving at six areas — a left column divided into an upper and a lower part,
and five others around them. That arrangement is slicing. Now join the two
parts of the left column: they share a full edge, so `area_getorientation`
admits it and `screen_area_join_aligned` merges them into one rectangle. The
result is the five-area pinwheel, which no sequence of full-span cuts can
produce. One ordinary join took the layout out of the slicing class.

Two further findings in the same direction, both verified in the source:

- **Join does not require a full shared edge.** `area_getorientation` asks for
  an exact facing-coordinate match and a perpendicular overlap of at least
  `min(tolerance, extent of A, extent of B)` — so the required overlap can be
  no more than the *smaller* area's own extent, and a short area beside a tall
  one qualifies. `screen_area_join_ex` then trims the overhang into new areas
  with `screen_area_trim` so the two line up, joins them, and optionally closes
  the remainders.
- **Every aligned join fuses coincident vertices across the whole screen**, via
  `BKE_screen_remove_double_scrverts`. So four-area junctions are produced as a
  matter of course by joining, rather than arising only by coincidence — which
  is the mechanism behind the one in the Shading workspace.

**What this does and does not change.** The count stands: Blender's designers
shipped no non-slicing layout in thirty-two workspaces, and the two
graph-specific drag behaviours remain opt-in. What falls is the stronger claim
that the graph buys expressiveness Blender's own model never reaches. It does
reach it, easily, and a nested-splitter tree is therefore **strictly less
expressive than Blender's representation**, not merely differently organised.
`PL-3J2P` records the decision that follows and the reasoning it now rests on.

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

### An editor cannot refuse a size, and there is no minimum-size contract at all

`ARegionType` (`source/blender/blenkernel/BKE_screen.hh`) declares
`minsizex` / `minsizey` and `prefsizex` / `prefsizey`, and a reader who stopped
at the header would conclude that an editor states a minimum the container
honours. It does not. **`minsizex` and `minsizey` occur exactly once in the
entire checkout — that declaration — and nothing reads them.** They are
vestigial. This is the clearest illustration in the study of why the reading
scope was widened to implementation: the earlier pass read headers only, and the
header alone gives the wrong answer here.

What is live is `prefsizey` / `prefsizex`, a *preferred* size consulted mainly
when a region first opens, and even that is a starting value rather than a
constraint — `region_rect_recursive` in
`source/blender/editors/screen/area.cc` substitutes its own defaults for a
header, a footer or an asset shelf regardless of what the type asked for.

The container computes every rectangle, and where a region cannot be fitted —
the area is too narrow, or a sidebar would collide with one aligned to the
opposite side — it sets `RGN_FLAG_TOO_SMALL` and returns. Downstream a region
carrying that flag is treated exactly as a hidden one: its `winrct` is collapsed
to zero extent, so it occupies no space and draws nothing.

So there is no negotiation, no veto, and no declared minimum that means
anything. **The container decides, and its failure mode is to make content
disappear rather than to refuse the layout.** That is a defensible answer for a
3D content tool, where a hidden sidebar costs a user one keystroke. It is
directly unsafe here, and "What this project does differently" returns to it.

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

So: **Blender is silent about which editor was lost.** The area keeps its
rectangle, fills with a different editor than the file asked for, and nothing
names the substitution.

One qualification, because the first reading of this overstated it. Blender is
*not* silent about the commonest situation that produces the loss. When the file
was written by a newer Blender, `readfile.cc` sets a forward-compatibility flag
on the main database; the status bar then carries a persistent warning-coloured
version indicator, and saving over the file raises a dialog whose message is
that the file was saved by a newer version of Blender. That is a real warning,
and it is a **file-level** one: it says data may have been lost, never that this
pane is now showing something other than what was saved.

The silent path is therefore narrower than "Blender never warns" and is still
the one that matters here: an editor type that is missing for any *other*
reason — removed, renamed, or belonging to an add-on that is no longer
installed — trips no forward-compatibility flag, and the substitution happens
with nothing said at all.

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

`SpaceType` is a vtable-as-data: metadata plus function pointers, registered
once at startup. Three different answers to "what is required" fall out of it,
and keeping them apart is the useful part.

**The enforced contract is tiny.** Only `spaceid`, `name` and `create` are
genuinely unavoidable — `create` is called with no null guard — plus one
structural invariant: every region an editor's `create` builds must have a
matching declared `ARegionType` with the same `regionid`. `ARegionType` itself
has **no required callbacks at all**; the tree ships one with nothing but
`regionid` set. Everything else on `SpaceType` is null-guarded at its call site.

**The practised contract is larger.** All twenty in-tree editors set `create`,
`free`, `init`, `duplicate`, `operatortypes`, `keymap` and `blend_write`, and
declare one `ARegionType` per region they use, even though every one of those
is guarded somewhere. The simplest real editor,
`source/blender/editors/space_script/space_script.cc` (~220 lines), implements
exactly that floor and nothing more: identity, those lifecycle hooks, and two
region types — a main window region and a header — each with `init` and `draw`.

**And part of the declared interface is dead**, which is the most useful warning
in this section for a project about to design a contract of its own.
`SpaceType::draw_pre` and `draw_post` have live, guarded call sites in the
window manager's draw path and **zero implementations anywhere in the tree**.
`SpaceType::keymapflag` is read in `source/blender/editors/screen/area.cc` and
**never assigned by any editor** — every `keymapflag` assignment in the tree is
to the identically-named field on `ARegionType`, which is a different member of a
different struct. A vtable-as-data contract accumulates members nothing
implements and fields nothing sets, and nothing in the design makes that
visible. `PL-TH35` should take the shape and plan for the pruning.

One detail matters for our own contract: **the editor declares its own header
region.** The container does not supply a title bar and hand the editor the space
beneath it; the editor registers a header region type alongside its main one,
with its own draw callback. A view's chrome is the view's business, and the area
only allocates the rectangle the container computes.

## What the code cannot answer: Blender's stated reasoning

**Evidence warning, and it applies to this whole section.** None of the pages
below could be opened; every `blender.org` host and `web.archive.org` are
refused by this environment's egress proxy. What follows rests on search-engine
summaries of those pages. Where a claim could be checked against the source it
was, and that is marked. Everything else should be re-read at the page itself by
any session that can reach one. Where the honest answer was that Blender does
not appear to say something, that is recorded as the finding.

### Blender's reason for non-overlapping is not this project's reason

This is the most important finding in the section, and it is a negative one.

`ROADMAP.md` item 34 refuses silent occlusion on a safety argument: a covered
value on this application's dashboard is a misread value, which `CLAUDE.md`'s
standard treats as a safety failure. It would be convenient if Blender's own
rationale were the same, because then the precedent would carry the argument.
**It is not.**

Blender's Human Interface Guidelines name **Non-Overlapping**, **Non-Blocking**
and **Non-Modal** as three separate paradigms with three separate reasons —
which is itself worth knowing, because the three are often treated as one idea.
Non-overlapping is a *window-management and visibility* argument: the interface
should let you see the relevant options and tools at a glance, without pushing
or dragging editors around. Non-blocking is about not being locked out of the
rest of the application by a requester. Non-modal is select-then-act, with an
operator's settings adjustable after it has run.

An attribution caveat, because the search route cannot settle it: the most
pointed phrasing of the non-overlapping rationale — freeing artists from moving
windows around *and from covering up content* — appears to come from a 2008
Blender Conference paper rather than from the guidelines page itself. The
substance is consistent across both, but a session that can open the pages
should confirm which document says what before quoting either.

One further qualifier, and it cuts the same way. Blender states non-overlap as
a **default with acknowledged exceptions**, not as an invariant: the same
guidelines page names multiple windows and screens as legitimate, and cases —
multi-monitor work, render output — where an overlap is the better answer. A
project citing Blender as precedent for an absolute no-occlusion rule is citing
it for more than it says. What this project refuses is narrower and firmer than
Blender's default, which is the right way round but is *our* rule.

So Blender is good evidence that **tiling is workable and pleasant at scale**,
and no evidence at all for the information-integrity claim. This project's
safety argument stands on its own reasoning and on `docs/MODEL.md`'s minimum
displayed outputs, and citing Blender in support of it would be citing a
different argument that reaches a similar-looking conclusion.

### "Non-overlapping" is narrower than it sounds, and the source proves it

Nothing reachable states a general principle for which elements may overlap an
editor and which may not; the line has to be inferred from practice. But the
practice is clear, and one part of it corrects a mistaken reading this project
was at risk of carrying.

**Blender's non-overlap guarantee is about areas, not about everything.**
Verified in the source rather than inferred: `RGN_TYPE_HUD` and
`RGN_ALIGN_FLOAT` are region types (`DNA_screen_types.h`), `region_overlap_fix`
in `source/blender/editors/screen/area.cc` exists precisely to arbitrate regions
that overlap within one area, and the user preference controlling it,
`USER_REGION_OVERLAP` (`DNA_userdef_types.h`), is **on by default** —
`uiflag2` is initialised to it. So a toolbar, sidebar or header floats
translucently over the main region of its own area out of the box, and the redo
panel is a floating region type.

What does *not* overlap is one **area** over another. Menus, popovers, tooltips
and pie menus overlap freely; so do temporary top-level windows, and those are a
named category rather than an accident — `WM_window_is_temp_screen`
(`source/blender/windowmanager/WM_api.hh`) is a public predicate for them, and
Preferences, the file manager and the render window are its members.

The line this project needs is therefore **not** inherited from Blender and has
to be drawn here. The useful part of the precedent is the shape: a small,
named, enumerable set of things that may float, with a predicate that identifies
them, rather than a case-by-case judgement per widget.

### Header, sidebar, toolbar and footer are keyed to scope of effect

The source defines roughly sixteen region roles and no guidance. What the HIG
offers is closer to a set of **defaults than to a decision procedure**, and the
idea organising them is **scope of effect rather than frequency of use**:
display options — what you are looking at — go in the header; options affecting
several tools or the editor's own behaviour go to the right of the header or
into tool settings, optionally behind an options popover; interactive
gizmo-driven tools go in the toolbar; grouped object- and editor-level settings
go in the sidebar, under a discipline that prefers reusing an existing tab to
adding one.

One piece of Blender's own reasoning here is worth more to this project than the
placement rules, and it emerged from the design discussion that moved the tool
settings strip below the header rather than above it. The argument was
**information hierarchy**, not aesthetics: the header carries the controls that
define the working context — the mode, most of all — and tools are interpreted
*relative to* that context, so the context-defining strip must sit above the
tool strip rather than beneath it. That is a real principle and it transfers
directly. Anything that says *what the numbers on screen are about* — which run,
which patient, which model — outranks and sits above anything that acts on
them.

Two gaps worth recording rather than papering over. Nothing reachable gives the
**main region** a role definition at all — it is simply what is left. And there
is no prohibition list for headers; the only stated pressure is limited
horizontal width, answered with pulldowns and popovers rather than with a rule
about what may not go there. A project whose required values must never be in a
hideable region will not find that rule in Blender.

### Workspace and Screen are two concepts because one was doing two jobs

The clearest and best-evidenced of the rationale findings. Before 2.8, screen
layouts were being used as whole-task presets *and* as arrangements of areas.
The 2.8 interface work separated them: a **WorkSpace** became a task-level ID
data-block, and a **bScreen** was demoted to the geometry of areas in one
window — renamed "layout" in the interface.

A workspace therefore carries more than an arrangement: an object mode it
switches to on activation, an optional pinned scene, and an optional
per-workspace add-on filter. It holds *several* layouts because a screen is
bound to a single window, and because maximizing an area or opening a temporary
window creates an extra hidden screen; per-window and temporary layouts
accumulate under the one workspace.

That is directly applicable here. Item 34 already wants a workspace to pin which
**run** it shows, which is the analogue of pin-scene. The two-level split is
what makes that possible: if a workspace were only a layout, there would be
nowhere to put it.

### There is no mode-awareness doctrine to borrow

Worth stating because the absence is the answer, and because this project's
safety standard needs exactly such a doctrine.

Blender's **Non-Modal** paradigm turns out to be primarily about *not blocking*
— no requester that must be completed before a tool runs, settings shown in
non-blocking regions, operator settings adjustable after the fact — plus a
secondary noun-then-verb claim. It is explicitly not a claim that Blender has no
interaction modes; the guidelines concede that Blender's complexity makes some
editing modes inevitable and mitigate them by scoping them.

What is absent is any doctrine about **mode awareness** — keeping the current
mode visible, or what to do about a mode that is hard to notice. Blender has
strong mode-awareness devices in practice (the mode selector in the header, a
different keymap, different shading), but nothing reachable presents them as a
deliberate answer to the hazard of an unnoticed mode. So this project's
requirement — that a reader can never be wrong about what state the application
is in or what context a displayed value belongs to — has no Blender precedent to
lean on, and is ours to design.

### Where Blender says the model does not apply

Mostly Blender documents its exceptions as behaviour rather than as reasoned
boundaries. The temporary windows are named and detectable but explained by what
they do rather than by why they are exempt.

The one place the model is clearly said not to carry is Blender's own
tablet and touch work, which names a single full-screen window, small screen
area, and the absence of a mouse and keyboard as constraints calling for
task-oriented, lower-density interfaces. That is an admission by implication
that the desktop area model is a desktop model. This project's interface is a
desktop application and so sits inside that boundary — but it is the boundary,
and a later session considering a tablet build should treat item 34's model as
out of scope there rather than as something to shrink.

## What this project adopts, diverges from, and refuses

### Adopted

**The three concepts and the three words.** An *area* is a rectangle that
reserves screen space and holds one thing; an *editor* is what occupies it; a
*workspace* is a set of areas geared to a task, switched as a tab. Blender's
vocabulary, used here for the same three things, so that the code and the
roadmap do not drift apart (`.claude/rules/ui-areas.md` fixes this).

**Workspace and layout as two levels, not one.** The 2.8 split — a workspace is
a task-level object, a layout is the geometry of areas in one window — is what
makes `ROADMAP.md` item 34's wanted behaviour possible at all. Item 34 already
wants a workspace to pin which **run** it shows, the analogue of Blender's pin
scene. If a workspace were only a layout there would be nowhere to put that.

**The area owns the geometry and the view owns none.** The strongest and
cleanest thing in the design. A view is given its rectangle and never stores,
computes or asks for one.

**Each view serializes itself; the layout layer does not know what is in a
pane.** Blender's `SpaceType.blend_write` / `blend_read_data` delegation is the
answer to "how does a workspace save without the layout code knowing what an
F_A/F_I chart is", and it is the right answer.

**A stack of previously-open editors per area**, so that switching a pane to
another view and back restores the first one's state. Blender achieves it by
swapping *region* lists, with per-view state living in the regions; the shape to
copy is that the outgoing view's state is kept rather than destroyed.

**A view kind is a tag plus a registry lookup, never a subclass.** Nothing in
the layout layer knows a concrete view type exists.

**Context above tools.** The strip that says *what the numbers are about*
outranks and sits above anything that acts on them — Blender's own information
hierarchy argument, and directly in service of this project's requirement that a
reader can never be wrong about what context a displayed value belongs to.

**Split, join, swap and border-drag as the operation set**, with the layout
stored as a **nested-splitter tree**. `PL-3J2P` carries that decision and the
measurement behind it.

### Diverged, and each divergence has a specific cause

**A missing or unknown view kind must fail loudly.** Blender silently
substitutes a 3D viewport and the interface looks normal. `CLAUDE.md` requires
an obvious failure state in preference to a plausible-looking wrong one, and
treats mis-contexted presentation as a safety failure. A saved workspace naming
a view this build does not have must say so, visibly, and must not quietly
present a different view in that pane. Blender's own asymmetry — it *does* warn
about an unknown region type ten lines away — suggests this is an oversight to
avoid rather than a design to follow.

**A required value is never hidden to make room.** Blender's answer when a
region will not fit is `RGN_FLAG_TOO_SMALL` and collapse to zero extent. For a
3D tool that costs a keystroke. Here, `docs/MODEL.md` § "Minimum displayed
outputs" divides the display into an unconditional set no workspace may remove
and nothing may cover, and silently collapsing one of those is exactly the
failure the division exists to prevent. The unconditional set sits outside the
area system, and where a conditional surface genuinely cannot fit, the interface
must say that rather than quietly shrink it away.

**Isolation has to be built; it is not inherited.** Blender's editors receive a
context through which they can reach the window, the screen and every other
area, and ten of twenty-one do. This project wants interchangeability with
teeth, so its views should be *handed* what they draw and given no route to the
container at all. That is a deliberate narrowing of Blender's contract, not a
copy of it — and it is cheap now and expensive later, which is why
`.claude/rules/ui-areas.md` already asks for it in views written before the area
system exists.

**The container sits behind a layout model of this project's own.** The
container-level form of the same reasoning. `PL-C842` carries the
recommendation and the evidence.

**Border chains, to recover the one thing the tree loses.** Blender's default
drag moves a maximal connected collinear chain; a splitter tree's handle moves
one handle. Across the thirty-two shipped workspaces this differs exactly once,
at a four-way junction. The fix is not the graph: it is for the layout model to
resolve, on a drag, the set of handles that are collinear and adjacent to the
one being dragged, and move them together. That is a query over the tree rather
than a change of representation.

**Prune the contract; do not let it accumulate.** Blender's `SpaceType` carries
hooks nothing implements and a field nothing assigns, and nothing in the design
surfaces that. A contract of our own should be small, and should be re-checked
against its implementers rather than only added to.

### Refused

**The shared-vertex graph**, as the layout's representation. Not because it is
worse in the abstract — it is strictly more expressive — but because the
measurement found nothing in thirty-two shipped workspaces that needs the extra
expressiveness, and the cost of owning a planar subdivision falls on one person
forever. `PL-3J2P` records the condition under which that reverses.

**Blender's rationale for non-overlapping**, as support for this project's
occlusion rule. Blender's reason is window management and visibility; this
project's is that a covered value is a misread value. The conclusions look
alike and the arguments are not the same, so item 34's safety argument stands on
its own reasoning rather than on Blender's precedent. What Blender does supply
is the existence proof that a tiled interface is workable and pleasant at the
scale of a professional tool.

## Attribution

This project's workspace, area and editor model is modelled on Blender's,
studied from its published source and its design documentation. Blender is
developed by the Blender Foundation and its contributors; its source is licensed
GPL-2.0-or-later per file with the work as a whole under GPL-3.0-or-later, and
its Manual and Developer Documentation are licensed CC-BY-SA 4.0 by the Blender
Documentation Team and the Blender Developer Documentation Team respectively.

**No Blender code is used in this project, and none of its documentation is
reproduced here.** What was taken is a design, described in this project's own
words.
