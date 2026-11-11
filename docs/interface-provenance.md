# Interface provenance: what this project studied of Blender, and what it took

This project has decided to model its interface on Blender's window system
(`ROADMAP.md` planned-milestone item 34). That system divides a window into
resizable **areas** that do not overlap. An area is a rectangle that reserves
screen space and holds one **editor**. Areas are grouped into named
**workspaces**, each arranged for one task, and the user switches to a workspace
by its tab. This project calls what occupies an area a **View**, where Blender
says editor, for the reason given in § "Diverged, and each divergence has a
specific cause". Where this document describes Blender, it keeps Blender's words,
such as `Editor`, because renaming them would misreport the source.

This file records the research behind the decision: what the project read of
Blender, under what rules, what it established, and where it deliberately
departs from Blender's design (§ "What this project adopts, diverges from, and
refuses"). Without it, a session new to the question either redoes the whole
research or guesses, and both have happened. The file also answers a
question the project owner asked directly on 2026-09-16: whether there is a
good-faith way to study Blender's architecture for inspiration. There is, and
its rules are narrow enough to be worth writing down once
(§ "The study protocol").

To find where this project's own code goes, see the map of its layering in
`docs/ARCHITECTURE.md`.

## What a later design thread owes this study

Every thread that designs or builds Workspaces, Areas or Views must follow the
list below, whether or not it is in a Project. The list was written on
2026-10-03 from the rules set for the threads of the v0.6.0 Projects trial.
Until then, those rules were written down only in the trial's instructions
(`PL-PDVF`; the rules are the owner's, read there on 2026-10-03, their kind
unrecorded).

- **Start from this file's record of what was adopted, diverged from and
  refused.** § "What this project adopts, diverges from, and refuses" lists each
  entry and the reason for it. A design that would contradict an entry says so.
- **Read Blender freely, and copy nothing.** The table under § "The prose is the
  encumbered half, not the source" gives the whole rule. Read Blender's source,
  and never copy, adapt, translate or port it. Paraphrase and cite the Manual
  and the Developer Documentation, and never paste from them.
- **Where this study leaves a behaviour open, read Blender's own pages:** the
  Manual at https://docs.blender.org/manual/en/latest/interface/window_system/
  and the source at https://raw.githubusercontent.com/blender/blender/main/
  followed by the file's path. Cite the page, or the file and the function, in
  the item that records the design.
- **Cite a claim at the strength its page gives it.** Base no design on a claim
  marked as unconfirmed in § "What the code cannot answer: Blender's stated
  reasoning", until a page is found for it. Where a design rests on a page this
  file does not list, read that page and record what it said.
- **A recorded divergence or refusal still applies unless the owner reopens
  it.** A thread that thinks Blender's behaviour is better puts the case to the
  owner with a recommendation, and builds nothing on it until the owner decides.
  The milestone's "Explicitly out of scope" list still applies either way.
  Wherever Blender disagrees with the safety-critical standard for clinical
  output in `CLAUDE.md`, or with the milestone's Definition of done, those two
  take precedence.
- **When a Blender host is refused at CONNECT, report the refusal and name the
  host.** Base the report on a probe of the host, not on this file's record of
  the day it was refused (`.claude/rules/instruction-writing.md` rule 14;
  `PL-M701`).

## The study protocol

### Reading is not a restricted act; copying, translating and porting are

Every Blender file that this study read carries the license header
`SPDX-License-Identifier: GPL-2.0-or-later`. This project is Apache-2.0
(`LICENSE`, `pyproject.toml`), and adding GPL code to it would make its stated
license wrong.

The study rests on what the GPL does and does not restrict:

- **Reading Blender's source to understand it is unrestricted.** GPLv2 § 0 puts
  activities other than copying, distribution and modification outside the
  license's scope.
- **Copying, adapting, transliterating or porting Blender's source is
  restricted.** Nobody has done any of these in this project, and nobody may.
  GPLv2 § 2 covers modification and names translation into another language.
  Rewriting a C++ function in Python is such a translation.
- **Describing what was read, in this project's own words, is the
  deliverable.** § "What Blender's window system is" was written that way.

This document gives file paths and the names of functions, structs and fields
throughout, so that you can check a claim against Blender's source. Naming the
function that implements a behaviour does not reproduce how that function is
written.

**Check the license header of each file you read.** The tree is mixed, which the
usual shorthand "Blender is GPL" hides. Blender's README says that the work as a
whole is GPL-3.0 but that individual files may carry a different, compatible
license. The binary ships under GPL-3.0-or-later. In the checkout used for this
study, 2,092 files declare `GPL-2.0-or-later`, 10 unit-test files declare
`Apache-2.0`, and 2 files declare `GPL-3.0-or-later`
(`source/blender/editors/uvedit/uvedit_clipboard_graph_iso.cc` and its header
file).

### The prose is the encumbered half, not the source

Blender's documentation licence sounds weaker than its source code licence, but
it is the one that applies to this repository. This is the constraint most
likely to be got backwards. Reading the GPL source code is not copying, while
pasting documentation prose into `ROADMAP.md` or `docs/` is.

The Blender Manual and the Blender Developer Documentation are both licensed
**CC-BY-SA 4.0**, a share-alike licence. The Developer Documentation includes
the Human Interface Guidelines (HIG). Each kind of source has its own rule:

| Source | Licence | What this project may do |
|---|---|---|
| Blender source code | GPL-2.0-or-later (per file) | Read freely. Never copy, translate or port. |
| Manual, Developer Docs, HIG | CC-BY-SA 4.0 | **Paraphrase and cite. Never paste.** |

Credit the two documentation teams as § "Attribution" names them, with a link.

As read on 2026-10-25, both documentation licence pages grant CC-BY-SA 4.0 "or
any later version", and exclude logos, trademarks, icons, source code and Python
scripts from that licence. The pages are listed under
§ "Pages read on 2026-10-25". The licence statements were first confirmed on
2026-09-16 through a search engine.

Blender's own Copyright Rules handbook draws the same line between studying and
copying for material entering Blender. It asks that a design be studied and
re-expressed, and refuses lifted assets or prose. It bars copyrighted elements
of other software, and encourages designs that build on Blender's own design
history.

### What this project attributes

This project's interface layout is modelled on Blender's. In this layout, panes
are tiled without overlapping, each shows a view whose kind can be swapped, and
a set of panes is saved as a named workspace. § "Attribution" gives the credit,
and says where else it appears.

This project's own provenance standard asks for the attribution to Blender. The
law does not require anyone to attribute an idea, because copyright does not
cover procedures, processes, methods of operation or concepts
(17 U.S.C. § 102(b)). The attribution answers the spirit, rather than the
letter, of the project owner's question in the introduction: whether there is a
good-faith way to study Blender's architecture for inspiration.

The more abstract the part taken from Blender, the safer it is in law. The layout
above is a method of operation. A one-for-one translation of Blender's structs
would copy its structure instead: the structs for the screen, the area and the
region (`bScreen`, `ScrArea` and `ARegion`), and the links between them. In
**Computer Associates Int'l v. Altai**, 982 F.2d 693 (2d Cir. 1992), the court
held that copyright can protect a program's structure as well as its literal
code. That case sets out the abstraction-filtration-comparison test for telling
such structure from a method of operation. A more abstract part is also more
useful, because this project needs from Blender the shape of the boundary
between a pane and what it shows, not the fields of its structs.

### How this study was conducted, and where it could not reach

This section records the route to each source and how deeply it was read,
because the project's rule for citing sources makes the same demand of a stored
constant (`.claude/rules/citing-sources.md`). That rule covers only the data
files, but its reasoning applies here unchanged. Without the record, a citation
read at the source could not later be told apart from one taken from a search
summary. The study's two halves, Blender's source code and its documentation,
have very different evidence grades.

**Blender's source: read directly, in full.** This is first-hand evidence and the
strongest thing in this document. § "What Blender's window system is" records
the commit and the files read.

**Blender's shipped layouts: measured, not eyeballed.** § "How it was measured"
gives the method.

**Blender's documentation: first reached only through a search engine, then read
on the pages themselves.** The documentation half rests on pages read on
2026-10-25, and two of its claims are still unconfirmed. § "What the code cannot
answer: Blender's stated reasoning" records how the pages were reached and read.

## What Blender's window system is

This section describes Blender's window system as its source shows it. § "What
this project adopts, diverges from, and refuses" says what this project takes
from it.

The claims below come from Blender's source, cloned at `blender/blender` commit
`931bb2e7` (Blender 5.3) and read as implementation, not only as headers:
`area.cc`, `screen_edit.cc`, `screen_ops.cc`, `screen_geometry.cc`, the
`space_*` directories, and the blend read/write paths. They are in this
project's own words, and each names the Blender file and function it rests on.

### An area owns its rectangle; an editor owns no geometry at all

In Blender, an area owns a rectangle and shows one editor in it at a time.
**Geometry flows downward from the area, and never upward from the editor.**
Blender's code calls an editor a space.

The area keeps its geometry and identity in its struct, `ScrArea`
(`source/blender/makesdna/DNA_screen_types.h`). It has four corner vertices
`v1`–`v4`, a rectangle `totrct`, and `winx`/`winy`. The file's comments describe
the rectangle as bounded by those vertices. The struct names the active editor in
its `spacetype` tag, and keeps a run-time `type` pointer to the registered editor
type, `SpaceType`. It also holds the stack of editors that the area has shown
before (`spacedata`), and the live list of the area's regions (`regionbase`). A
region is a part of an editor, such as its header.

An editor's saved state cannot record where the editor is, because its struct
has no rectangle, size or position. That struct is `SpaceLink`
(`source/blender/makesdna/DNA_space_types.h`). It is the implicit base of every
editor type's own struct (`Space*`). It holds list links, the `spacetype` tag, a
flag, padding, and a list (`regionbase`) that its comment describes as storage of
regions for inactive editors.

Each region does have a rectangle (`winrct` on `ARegion`), but the editor never
assigns it. The editor declares what kind of region it wants and how big it
would like the region to be. The area that contains the region computes the
rectangle from the area's own rectangle and the region's declared alignment and
size (`region_rect_recursive` in `source/blender/editors/screen/area.cc`).

### An editor cannot refuse a size, and there is no minimum-size contract at all

**In Blender, the container alone computes the rectangle of every region, and it
never refuses a layout.** When a region does not fit, the container makes it
disappear. § "Diverged, and each divergence has a specific cause" says why this
project does not do the same.

The container cannot fit a region when the area is too narrow, or when a sidebar
would collide with one aligned to the opposite side. It then marks the region as
too small (`RGN_FLAG_TOO_SMALL`) and returns. Later code treats such a region
exactly as a hidden one. It collapses the region's rectangle (`winrct`) to zero
size, so the region takes no space and draws nothing.

**Nothing in Blender reads a region type's minimum size.** The region type
`ARegionType` declares a minimum size, `minsizex` and `minsizey`, and a
preferred size, `prefsizex` and `prefsizey`, in the header file
`source/blender/blenkernel/BKE_screen.hh`. A reader of that file alone would
conclude that the container honours a minimum size that an editor states. Yet
the two minimum-size fields occur exactly once in the whole checkout, in their
declaration. They are vestigial. This case is the study's clearest illustration
of why the reading was widened from headers to implementation, after an earlier
pass read headers only.

Blender reads only the preferred size, and mainly when a region first opens.
Even then, the preferred size is a starting value, not a constraint. For a header,
a footer or an asset shelf, the container's layout function uses its own defaults,
whatever the region type asked for (`region_rect_recursive`, in
`source/blender/editors/screen/area.cc`).

### An editor is isolated by convention, not by construction

Blender's source **falsified** the expectation that an editor cannot read its own
position, its neighbours, or what else is open. That property would make
interchangeability structural rather than aspirational. The research set out to
test this expectation. Its falsification is the most consequential correction in
this document.

Blender's editors can read their own position, their neighbours and what else is
open. They are interchangeable only because their contract does not depend on
position. Editors mostly keep to that contract, but nothing enforces it.

Each editor callback receives a context (`bContext`) that gives it the window, the
screen and every area on the screen. The code in Blender's 21 editor directories
(`space_*`) uses the context as follows:

- **16 of 21 read their own area** (`CTX_wm_area`). The call is universal. The 3D
  viewport's code (`space_view3d`) contains it 33 times.
- **11 of 21 get the screen that contains them** (`CTX_wm_screen`).
- **10 of 21 iterate over every area on the screen** (`screen->areabase` or
  `ED_screen_areas_iter`), to read and sometimes act on other open editors. For
  example, Blender does this to synchronise selection between outliner editors
  (`outliner_sync.cc`). The code for node selection (`node_select.cc`) and several
  files of the 3D viewport also iterate over every area.
- **2 of 21 search the screen for another area of a chosen type**
  (`BKE_screen_find_big_area`). The text editor (`space_text`) and the 3D viewport
  each look up the largest editor of their own type on the screen.

### How a layout is built, and how far the operations reach

This project stores its layout as a tree of nested Qt splitters, and such a tree
cannot express two of Blender's layout behaviours. The first is a drag that
moves every border aligned with the dragged one, connected or not. The second is
a merge of aligned edges. Whether a Blender user needs either is `PL-3J2P`'s
question, and § "The measurement: what Blender's own shipped layouts actually
contain" answers it. Reading Blender's source end to end (`PL-3J2P`) showed that
each runs only when the user asks for it.

**By default, a border drag in Blender moves the dragged edge and every edge that
continues it in a straight line.** Blender treats that straight run of connected
edges as one piece, a *maximal connected collinear chain*. Blender selects them in
one function (`screen_geom_select_connected_edge`, in
`source/blender/editors/screen/screen_geometry.cc`). It first flags the dragged
edge's two vertices. It then flags each edge that runs along the same axis and
has exactly one flagged vertex, and repeats until nothing more is reachable. Two
borders at the same coordinate do not move together when an area spans the gap
between them. Blender allows a layout to keep two such borders.

**Moving unconnected aligned borders in Blender needs the Shift key held.** In
`source/blender/editors/screen/screen_ops.cc`, the area-move command passes the
Shift state (`event->modifier & KM_SHIFT`) as its `extend` argument when the
user drags. Its non-interactive path (`exec`) passes `false`. The extended
selection (`screen_geom_select_extended_edge`) takes every vertex within
tolerance of the dragged coordinate, connected or not. It runs only when
`extend` is set and a check on the edge (`screen_geom_edge_can_extend`) allows
it. A helper lets the user turn the extended selection on or off during a drag
(`area_move_reinit`). That helper is the clearest evidence that the extended
selection is a mode the user enters, not the default.

**Merging aligned edges in Blender is a separate command on a right-click menu.**
The merge function (`screen_geom_edge_aligned_merge`) has only one caller,
`area_edge_merge_exec`. That caller is the body of the merge command
`SCREEN_OT_edge_merge` ("Merge Area Edge" / "Merge aligned area edges"). No drag
runs the merge. The command appears in one place in the interface, the right-click
menu of an area border (built by `SCREEN_OT_area_options`, "Area Edge Options").
That menu lists everything a border offers: a horizontal or vertical split, a join
in either direction, a swap of the two areas and the merge. It shows the merge only
when the edge passes the same check as the extended selection
(`screen_geom_edge_can_extend`).

**A split in Blender runs across exactly one area and never past it.** The split
inserts its two new vertices on that area's own left and right edges
(`area_split` in `source/blender/editors/screen/screen_edit.cc`).

**A join in Blender does not need a full shared edge.** The join check
(`area_getorientation`) asks that the facing edges lie at exactly the same
coordinate and overlap by at least `min(tolerance, extent of A, extent of B)`.
The required overlap is therefore never more than the *smaller* area's own
extent, so a short area beside a tall one qualifies. Blender then trims the
overhang into new areas so that the two line up, joins them, and optionally
closes the remainders (`screen_area_join_ex`, using `screen_area_trim`).

**Every aligned join in Blender fuses coincident vertices across the whole screen**
(`BKE_screen_remove_double_scrverts`).

### Persistence, and what happens when an editor is missing

Blender saves a layout and the editors in it with separate code. Blender writes
the layout (`bScreen`, an ID block) with the rest of the file. Each editor type
supplies functions that write and read its data (`SpaceType`'s `blend_write` and
`blend_read_data`, in `source/blender/blenkernel/BKE_screen.hh`). The layout
code calls those functions and never looks inside an editor.

**When a file names an editor type that the running build does not have, Blender
substitutes a 3D viewport for the missing editor.** This substitution is the
finding in this section that matters. The area keeps its rectangle, and no error
or warning names the editor that was lost. An editor type can be missing because
it was removed or renamed, because it belongs to an add-on that is no longer
installed, or because a newer Blender wrote the file.

On reading a file, Blender looks up each area's editor type
(`ED_area_and_region_types_init` in `source/blender/editors/screen/area.cc`
calls `BKE_spacetype_from_id(area->spacetype)`). When the lookup returns null,
Blender calls a fallback function that makes the substitution
(`area_init_type_fallback(area, SPACE_VIEW3D)`). The function's own comment
says that it sets up a known editor type when a file with an unknown one is
loaded. The only guard is an assertion that the substitution itself worked
(`BLI_assert`), and assertions compile out of release builds.

The first reading of this overstated Blender's silence. Blender warns about the
commonest cause of a missing editor type, a file written by a newer Blender.
Blender's file reader (`readfile.cc`) sets a forward-compatibility flag on the
main database when it loads such a file. The status bar then shows a persistent
version indicator in a warning colour, and saving over the file opens a dialog
saying that a newer version of Blender saved it. These warnings say only that
data may have been lost. The file reader sets no flag for the other causes, so
the substitution happens with nothing said at all.

Blender does warn about an unknown *region* type. When a saved area holds a
region of a type that the area's editor type does not declare, Blender's file
reader removes the region and logs a warning that names the region type and the
editor type (`regions_remove_invalid` in `source/blender/blenkernel/intern/screen.cc`,
read at commit `931bb2e7` on 2026-11-07).

This project does not copy the silent substitution, and § "Diverged, and each
divergence has a specific cause" gives the reason.

### What survives a resize, a split, a join, and a swap

In Blender, swapping an area to another editor and back restores the first
editor's view state exactly: pan, zoom, scroll, and which panels are open.

The view state comes back because it lives in the editor's **regions**. Each
area keeps a list of stored editor entries (`area->spacedata`), and an editor's
regions travel with its entry (`SpaceLink`). The area has one live region list at
a time, and the stored entries hold the others.

The function that changes an area's editor is `ED_area_newspace`, in
`source/blender/editors/screen/area.cc`. It searches the area's list for an entry
of the requested editor type. If it finds one, it **swaps the region lists** and
moves the found entry to the head of the list. The area's live region list
(`regionbase`) goes back onto the outgoing editor's entry, and the found entry's
regions become live. If the search finds none, the editor type's create function
(`SpaceType.create`) makes a new entry. The outgoing editor's entry is **kept**, not
freed, unless it is flagged as temporary.

**Blender bounds an area's list of stored editor entries without a cap.** An area
gets a new entry only when it has none of the requested editor type, so its list
holds at most one entry per type, about twenty in all. Blender has no eviction
code, and needs none.

In a *split*, each editor type's duplicate function (`SpaceType.duplicate`)
decides how much of the editor's state the new area carries. The layout system
does not.

### What an editor must implement

Blender registers each kind of editor, such as the script editor, once at
startup as a `SpaceType`: a struct of metadata and function pointers. What an
editor must implement has three different answers: what Blender enforces, what
its editors do, and what the struct declares.

**The enforced contract is tiny.** Only three members are required: `create`,
`free` and the registry key `spaceid`. Blender calls `create` with no null guard
and dereferences its result immediately. Of the two places that call `free`,
only the one in `ED_area_newspace` lacks a null guard. An editor must also
declare a region type (`ARegionType`) with a matching `regionid` for each region
that its `create` builds, such as its header. A region type needs no callbacks,
and one in Blender's source tree sets only its `regionid`.

Blender does not require `name`, and code in the tree uses it only in
diagnostics. One of these is the warning for an unknown region type
(§ "Persistence, and what happens when an editor is missing"). It is the only
warning that names what Blender dropped, and without the editor's `name` it
could not say which editor it was about.

**In practice, editors implement more than Blender enforces.** All twenty
editors in the tree set seven callbacks (`create`, `free`, `init`, `duplicate`,
`operatortypes`, `keymap` and `blend_write`) and declare one region type for
each region they use, even though Blender guards every one of these somewhere.
The simplest real editor is the script editor
(`source/blender/editors/space_script/space_script.cc`, ~220 lines). It sets
the members that identify it and exactly those seven callbacks. It declares two
region types, for its main window region and its header, each with `init` and
`draw`.

**Part of the editor interface that Blender declares is dead.** The window
manager's draw path calls `SpaceType::draw_pre` and `draw_post` with a null
guard, and nothing in the tree implements either. Blender reads
`SpaceType::keymapflag` in `source/blender/editors/screen/area.cc`, and no
editor sets it. Every assignment to `keymapflag` in the tree is to the field of
the same name on `ARegionType`.

**An editor draws its own header.** Beside its main region type, it declares a
header region type with its own draw callback, as the script editor does. The
container supplies no title bar, and the area that holds the editor only
allocates the rectangle that the container computes. This project departs from
Blender here, and § "Diverged, and each divergence has a specific cause" says
how.

## The measurement: what Blender's own shipped layouts actually contain

The project had to decide whether to store its layout as Blender's
**shared-vertex graph** or as a **nested-splitter tree**, and chose the tree
(`PL-3J2P`). In the graph, each area lists its four corner points, and
neighbouring areas share those points. The tree is the structure Qt provides,
and the roadmap already named it (`ROADMAP.md` item 34).

Arguing the choice from the two representations' expressive power is a trap.
The graph can represent every layout that the tree can, and more, so it always
wins on that test. The argument therefore ends before weighing anything. The
question worth answering is narrower: **does Blender, in the layouts it actually
ships, use the power that the graph has and the tree does not?** That is a
count, and it was taken rather than estimated.

### The threshold, stated before the count

The splitter tree is judged against the thresholds below, on the screens of
Blender's eleven default workspaces. The thresholds were written down before
any counting code was run, as a project rule asks (`.claude/rules/expert-review.md`
§ "Name the number that would change your mind, then go and count it").

- **A — non-slicing.** Can each screen be divided into its areas by recursive
  full-span cuts (a *slicing floorplan*)? The minimal non-slicing arrangement
  is the pinwheel: five rectangles with no full-span cut anywhere. A non-slicing
  screen is one that a splitter tree **cannot represent at all**. *If two or
  more of the eleven screens are non-slicing, the tree is wrong outright.*
- **B — cross junction.** Does any interior point have four areas meeting at
  it? A splitter tree can draw a cross junction with two cuts at the same
  coordinate. The junction's two collinear border segments then become
  independent handles, whereas in Blender they share one vertex. *If no screen
  is non-slicing and at most one has a cross junction, the tree is confirmed.
  If four or more do, the tree behaves wrongly at a junction that Blender uses
  routinely.*
- **C — drag fidelity.** Does any decomposition into splitters reproduce
  Blender's border-drag behaviour exactly?

### How it was measured

Blender's default workspaces were read from **version 5.0.1** of the `bpy`
package on PyPI, not from screenshots in the Manual. That package is Blender
built as a Python module, and embeds the same startup data as Blender's source
file `release/datafiles/startup.blend`. That file is stored in Git LFS, so an
anonymous clone gets only a pointer stub. The Blender source studied is **5.3**,
so the layouts are one minor version behind it. The set of default workspaces
has been stable across that range, but the gap remains.

The rectangle of each area was read from every screen in the package's startup
data (`bpy.data.screens`). Each screen was reduced to an exact integer grid and
tested for all three properties. Every possible slicing decomposition of a
screen was enumerated, and the screen was judged on the best one. The rectangles
show how the areas are arranged, but not Blender's own vertex and edge objects,
because the `bpy` package reads RNA, a data layer that does not expose them.

### The result

**A nested splitter tree can express the layouts of all thirty-two workspaces
that Blender ships.** Dragging a border in the tree works as in Blender, except
where two borders cross in the Shading workspace's block of four editors
(a cross junction).

The pre-registered count covers Blender's eleven default workspaces:

| | count |
|---|---|
| **A** non-slicing (a splitter tree cannot express it) | **0 of 11** |
| **B** contains a cross junction | **1 of 11** (Shading) |
| **C** no splitter tree reproduces how Blender drags its borders | **1 of 11** (Shading) |

This count is the outcome pre-registered as "confirmed".

A second check found that a splitter tree can express all twenty-one workspaces
in Blender's five shipped application templates (2D Animation, Sculpting,
Storyboarding, VFX and Video Editing). One of those workspaces has a cross
junction: the same four-editor block, inherited from the Shading workspace. The
templates are built for the tasks least like those of the default workspaces, so
a non-slicing layout was likeliest among them. The second check's result stays
separate from the pre-registered count.

Each of the four possible splitter trees for the Shading workspace keeps exactly
one of the two crossing borders as a single handle. The workspace's 2×2 block
holds the file browser and 3D viewport along the top, and the image editor and
node editor along the bottom. In Blender, each of the two borders is made of two
edges that meet at the centre. Blender drags a straight run of connected edges
as one piece (§ "How a layout is built, and how far the operations reach"), so
dragging either border moves its whole length. A splitter tree's first cut
through the block follows one border across it, and splits the other into two
handles that move independently.

### What would have made this the wrong measurement

The count treated Blender's thirty-two shipped workspaces as a stand-in for
"layouts a professional tiling interface actually needs", and found no
non-slicing layout among them. A layout is slicing when a sequence of cuts can
produce it, each cut running across the whole of one area. The stand-in would be
wrong if Blender's designers chose the defaults to be *teachable* rather than to
exercise Blender's shared-vertex graph. The test of the stand-in was set before
the count: whether a user can reach layouts that the defaults avoid.

**By that test, Blender's defaults are the wrong stand-in, because a user can
make a non-slicing layout in six ordinary operations.** This was found by trying
to falsify the opposite hypothesis: that a user is confined to slicing layouts
because a split runs across one area only and a join needs a full shared edge.
That hypothesis is wrong.

**The count is still correct, but a nested-splitter tree is strictly less
expressive than Blender's graph.** What fails is the stronger claim that
Blender's own operations never reach the layouts that its graph can express and
a tree cannot. The graph's two extra behaviours run only when the user asks:
moving unconnected aligned borders, and merging aligned edges. A Blender user
builds a layout by splitting, joining, swapping and dragging borders, and needs
neither of them. The count found that Blender's shipped layouts depend on
neither. The project still stores its layout as a tree of nested splitters
(§ "Adopted"), and an item records the reasoning that this decision now rests on
(`PL-3J2P`).

**Splits alone always give a slicing layout**, because each split runs across
exactly one area and never past it (§ "How a layout is built, and how far the
operations reach").

**A join can make a layout non-slicing, even when the two areas share a full
edge.** Start from one area and make five splits, which gives six areas: a left
column divided into an upper and a lower part, and five others around them.
That layout is slicing. Now join the two parts of the left column. They share a
full edge, so they pass Blender's join check (`area_getorientation`). Blender
then merges them into one rectangle (`screen_area_join_aligned`). The result is
the five-area pinwheel, a non-slicing layout.

**Joins produce cross junctions as a matter of course, not only by chance**,
because every aligned join fuses coincident vertices across the whole screen
(§ "How a layout is built, and how far the operations reach"). This fusing explains
the cross junction in Blender's Shading workspace.

## What the code cannot answer: Blender's stated reasoning

**Each claim below was checked against the primary page it names**, downloaded
whole and read as text on 2026-10-25 (`PL-PV5Q`). This section was first written
on 2026-09-15, when this environment's egress proxy refused every `blender.org`
host, so the Manual and the Developer Documentation could not be opened. The
section therefore first rested on search-engine summaries, which a project rule
warns are what is likeliest to be mistaken for a reading
(`.claude/rules/citing-sources.md`). The `blender.org` hosts answered a probe on
2026-09-26 (`PL-M701`). The check on 2026-10-25 corrected three claims,
strengthened three, and left two marked as unconfirmed. Each of those two says
that none of the pages read confirms it. The section's main finding held:
Blender's reason for non-overlap is not this project's reason. Where Blender does
not appear to state something, the claim still says so, rather than giving a
confident summary assembled from general knowledge. § "Pages read on 2026-10-25",
at the end of this document, gives the pages and how they were fetched.

### Blender's reason for non-overlapping is not this project's reason

The most important finding about Blender's stated reasoning is a negative one:
Blender is good evidence that a subdivided window is workable and pleasant at
scale, and no evidence at all for this project's safety argument. Blender avoids
overlapping windows by default for visibility and efficiency. The roadmap rules
out silently covering a value on the dashboard (`ROADMAP.md` item 34). A covered
value is a misread value, which the safety-critical standard in `CLAUDE.md`
treats as a safety failure. This project's argument rests on that reasoning and
on the set of values that must always be displayed
(`docs/MODEL.md` § "Minimum displayed outputs"). Citing Blender in support of it
would be citing a different argument that reaches a similar-looking conclusion.

The Design Paradigms page of Blender's Human Interface Guidelines bases
non-overlapping on visibility and window management. A user should see the
relevant options and tools at a glance, without pushing or dragging windows
around, so Blender defaults to a subdivided window.

William Reynish's paper for the 2008 Blender Conference, "The Evolution of
Blender's User Interface", lists freeing artists from *covering up content*
among Blender's original design decisions, and credits that list to
blender.org. The guidelines page does not contain that phrase. The paper gives
efficiency as the reason: time an artist spends managing windows is time not
spent on the work.

The guidelines page states non-overlapping as a **default**, not as an
invariant. The same paragraph says that Blender also supports several windows
and screens, and names their uses: multi-monitor setups, animated windows,
render output, and individual cases where an overlap helps. A project that cites
Blender as precedent for an absolute rule against covering a value claims more
than Blender says. This project's rule is narrower and firmer than Blender's
default, which is the right way round, but the rule is this project's own.

**Non-Overlapping** is often treated as one idea with **Non-Blocking** and
**Non-Modal**, but each of the three has its own reason. The guidelines page
lists them first among its eight paradigms. Non-blocking means that no tool or
option locks the user out of the rest of the application. Blender does not pop
up a request that must be filled in before something runs. Where a task such as
a render does block, the page asks that the blocking be shown clearly and that
the user can leave the task at once. Non-modal is described in
§ "There is no mode-awareness doctrine to borrow", because the first version of
this section described it wrongly.

### "Non-overlapping" is narrower than it sounds, and the source proves it

Blender guarantees only that one area never overlaps another, so this project
has to draw its own line between what may overlap and what may not. It can keep
the shape of Blender's practice: a small, named, enumerable set of things that
may float, with a predicate that identifies them, rather than a judgement for
each widget.

No page that was read states a general principle about what may overlap an
editor. The guidelines name regions as the third level of subdivision, inside an
editor, and say nothing about whether a region may float. Blender's line
therefore has to be inferred from its practice, which the source code shows
clearly. That practice corrects a reading this project was at risk of adopting:
that Blender's non-overlap guarantee covers everything, not only areas.

**Inside one area, regions overlap by default.** What follows was verified in
the source rather than inferred. A toolbar, sidebar or header floats
translucently over the main region of its own area. The redo panel is a floating
region type. A user preference controls the overlap (`USER_REGION_OVERLAP`, in
`DNA_userdef_types.h`). The field that stores the preference (`uiflag2`) is
initialised with the overlap switched on. A Blender function arbitrates between
overlapping regions (`region_overlap_fix`, in
`source/blender/editors/screen/area.cc`). Blender's region definitions include a
region type for a heads-up display (`RGN_TYPE_HUD`) and an alignment that makes
a region float (`RGN_ALIGN_FLOAT`), both in `DNA_screen_types.h`.

Menus, popovers, tooltips and pie menus overlap freely. So do temporary
top-level windows. Blender treats these windows as a named category: a public
predicate identifies them (`WM_window_is_temp_screen`, in
`source/blender/windowmanager/WM_api.hh`). The temporary windows are
Preferences, the file manager and the render window. The Developer
Documentation's Window page names the same three.

### Header, sidebar, toolbar and footer are keyed to scope of effect

Blender's source defines roughly sixteen roles for an editor's regions, such as
the header and the sidebar, but gives no guidance on what goes in each. The
"Anatomy of an Editor" page of Blender's guidelines offers **defaults rather
than a decision procedure**, organised mostly by **scope of effect**:

- A switch between an editor's modes goes at the left of the header, just
  after the editor-type switcher.
- In the centre of the header, you choose the data that the editor works on,
  such as the image in the image editor.
- Display options change what you are looking at, and go on the right of the
  header.
- Options that affect several tools or the editor's own behaviour go on the
  right of the header or in the tool settings region, perhaps behind an options
  popover.

The Regions page of Blender's Manual describes the toolbar and the sidebar. The
toolbar, on the left, holds a set of interactive tools. The first version of
this section called those tools "gizmo-driven". No page read says that, so the
word was withdrawn. The sidebar, on the right, holds panels of settings for the
objects in the editor and for the editor itself. The guidelines' Sidebar Tabs
page calls for as few tabs as possible, and for an existing tab to be reused
rather than a new one added. The Layouts page asks for the most important and
most used widgets to be the easiest to reach, but applies that request only
within a panel, not to the choice of region.

One principle from Blender matters more to this project than the placement rules
above: context ranks above tools, which § "Adopted" applies to the simulator. The
principle comes from Blender task T91536, filed by Francesco Siddi in 2021. Until
Blender 3.0, an editor's tool settings region sat above its header, and the task
proposed swapping them. Its argument is **information hierarchy**, not looks. The
header holds the controls that define the working context, most of all the
editor's mode. Tools often depend on the mode, so the header ranks above the tool
settings. The swap shipped in Blender 3.0 as commit `4cf4bb2664`, which the 3.0
user-interface release notes list. The commit message itself gives a narrower,
practical reason: the header then always sits next to the window edge.

Blender's Manual and guidelines leave two gaps:

1. **The main region has only a thin definition.** The Manual's Regions page
   says that at least one region is always visible. It calls that region the
   main region and the most prominent part of the editor, and says its purpose
   differs by editor. The guidelines' Main Region heading has no text under it.
   The first version of this section said that the main region had no role at
   all, which was too strong.
   The main region matters to this project because a user can hide every other
   region, the header included, each from its own context menu.
2. **There is no list of what may not go in a header.** The guidelines do say
   that every regular editor has a header, because the header is how users tell
   the editors on screen apart. They add that a default layout should hide the
   header only in rare, well-reasoned cases. The problem they name for the
   header is its limited width, which they address with dropdowns and popovers.
   A project that must always show certain values will find no rule in Blender
   that keeps them out of a region that the user can hide.

### Workspace and Screen are two concepts because one was doing two jobs

Blender's split between a workspace and its screen layout applies to this
simulator, as § "Adopted" sets out. Of the rationale findings, the one about
this split is the clearest and best-evidenced.

In Blender versions before 2.8, the screen layout mixed workflow settings with
layout settings. The write-up of the Blender 2.8 user-interface workshop reports
this and says that the two should be separated. It is archived on the 2015
Blender wiki. Workspaces were the answer: a workspace is set up for one task,
such as modelling or animation.

The 2.80 release notes describe what shipped. A workspace provides a screen
layout for a task, workspaces appear as tabs at the top of the window, and a
workspace can be appended from another `.blend` file. The Developer
Documentation's Screen page describes the level below. A screen (`bScreen`)
holds the arrangement of areas and regions in one window and records which
window it belongs to. A workspace reaches its screen through an intermediate
object (`WorkSpaceLayout`). The first version of this section said that
Blender's interface renamed the screen "layout". None of the pages read on
2026-10-25 confirms it.

A Blender workspace carries more than an arrangement. The Manual's Workspaces
page lists a workspace's settings: a mode that it switches to when activated, an
optional pinned scene (Pin Scene), and an optional add-on filter. Current
versions add two settings for the video sequencer. A workspace can also hold
*several* screens. The Screen page gives one reason: a window shows one screen
at a time, and Maximize Area creates a second screen that holds only the
maximized editor. That screen is closed afterwards, and the first shows again.
The first version of this section also said that opening a temporary window adds
a hidden screen. None of the pages read confirms it.

Pin Scene is an opt-in exception to Blender's rule that interface and data stay
separate. The workshop write-up states that rule. It first put the active scene
on the **window**, not on the workspace or the screen layout, because switching
screen layouts was also switching scenes. Pin Scene shipped later, and the
Manual says that it takes effect when the user enables it.

### There is no mode-awareness doctrine to borrow

Blender has no doctrine for keeping the user aware of the current mode, so this
project must design its own. The project's safety standard needs one, because it
requires that a user can never be wrong about what state the application is in,
or about what context a displayed value belongs to. The re-read found more than
the first version of this section did, but the conclusion holds. Only one rule
from Blender's interface guidelines carries over: each editor's header stays
visible except in rare, well-reasoned cases.

**Blender's Non-Modal paradigm asks that input stay consistent and
predictable**, so that common mouse and keyboard methods do not change meaning
on the fly. The guidelines page that describes it admits that Blender's
complexity makes some modes unavoidable, and sorts them into three kinds:

- editing modes, such as mesh editing or posing, which are now a state of the
  object rather than of the editor or of the whole application;
- sticky modes, which stay active without input and are used only by the
  transform tools;
- temporary modes, which end as soon as the user stops acting.

The first version of this section said that Non-Modal was mainly about not
blocking, which was wrong. That description belonged to select-then-operate and
to adjusting an operation after it has run, which are separate paradigms on the
same page.

**Blender does name the hazard of an unnoticed mode.** Reynish's 2008 paper
grounds non-modality in Jef Raskin's argument from *The Humane Interface*: a
person cannot attend to the system's state and to the task at the same time, so
a gesture meant for one mode gets made in another. The write-up of Blender's
2.8 workshop names a related hazard: users become disoriented when they switch
layout or workspace, because the new editors keep views of their own and look
different. The write-up proposed views that pinned editors share. The
guidelines' "Anatomy of an Editor" page says that editors are in effect modes,
so each must be clearly distinguishable from the others. That page names the
header as what helps users tell editors apart.

**Blender's guidelines answer the hazard of an unnoticed mode by removing modes
or narrowing their scope, not by keeping the current mode visible.** The
guidelines have a page titled "Modal Interfaces", but when it was read on
2026-10-25, its only content was the heading "Preventing Mode Errors vs.
Consistency". In practice, Blender has strong mode-awareness devices: the mode
selector in the header, and a keymap and shading that change with the mode. None
of the pages read presents them as a deliberate answer to the hazard.

### Where Blender says the model does not apply

Blender says plainly that its non-overlapping area model is for desktops and
does not apply to a standalone tablet. This project's interface is a desktop
application, so the model applies to it. A contributor who plans a tablet build
should treat item 34's model as out of scope there, rather than shrink it.

Dalai Felinto lists the constraints of a standalone tablet in "Beyond Mouse &
Keyboard", a post on the Blender Developers Blog dated 24 July 2025. They are a
single full-screen window, little screen space, and no keyboard or mouse by
default. The post calls for more task-oriented interfaces with lower information
density. Its mockups run Blender in a single area, with temporary context shown
in floating regions. Felinto says that this design partly contrasts with the
non-overlapping model, and calls it a good compromise. So the area model is a
desktop model by Blender's own account, and not only by implication, as the
first version of this section had it.

Blender documents its other exceptions to the model as behaviour, not as limits
with a stated reason. Its temporary windows, for example, are named and
detectable. The Window page of Blender's Developer Documentation says that
these windows are not restored when a file is loaded. Blender's guidelines call
them "irregular editors", along with the global top bar and the status bar. The
guidelines add that an irregular editor opened in the split layout becomes a
regular editor, under the usual rules.

## What this project adopts, diverges from, and refuses

### Adopted

**This project uses Blender's words for two of its three layout concepts, so
that its code and roadmap do not drift apart, or into a private vocabulary.** It
calls a pane an *Area* and a named set of panes a *Workspace*. What occupies an
area is a *View*, which Blender calls an *editor*, as the introduction defines.
A project rule requires these words (`.claude/rules/ui-areas.md`), and the code
uses them: `Area` in `layout/tree.py`, `Workspace` in `layout/workspace.py` and
the `View` protocol in `app/view_contract.py`.

**A workspace and a layout are separate levels.** A workspace is a task-level
object, and a layout is the geometry of the areas in one window. The roadmap
calls for a workspace to pin which **run** it shows (`ROADMAP.md` item 34), much
as a Blender workspace can pin a scene. Blender split workspace from layout in
version 2.8, and that split is what makes the behaviour that `ROADMAP.md`
item 34 wants possible at all. If a workspace were only a layout, it would have
nowhere to keep that run. Here a `Workspace` holds its `layout` and, beside it,
the `pinned_run` that its Views show. Blender's Pin Scene is an opt-in exception
to its own rule that interface and data stay separate (§ "Workspace and Screen
are two concepts because one was doing two jobs"). A design that cites Pin Scene
as precedent should say that it cites an opt-in exception. The exception changes
no decision for this simulator, because pinning a run to a workspace has a
reason of its own (`PL-7Z84`).

**The area owns the geometry, and the view owns none.** A view is given its
rectangle and never stores, computes or asks for one. `layout/sizing.py` sizes
each Area in pixels, and `app/area_layout.py` places the View in it. This
boundary between area and view is the strongest and cleanest part of Blender's
design, and the most transferable.

**Each view serializes itself**, through `View.save_state`. The layout layer
therefore saves a workspace without knowing what any area holds, such as an
F_A/F_I chart. In Blender, each editor also saves and loads its own data
(`SpaceType.blend_write` and `blend_read_data`). That delegation is the right
way to save a workspace without the layout code knowing what an area holds.

**Each area keeps a stack of the views previously open in it.** Switching the
area to another view and back restores the first view's state. The roadmap's
"induction workspace with the graph zoomed in" case depends on this restore
(`ROADMAP.md` item 34). Blender restores a view by swapping lists of regions,
which hold each editor's state
(§ "What survives a resize, a split, a join, and a swap"). This project copies
the outcome, not the swapping. The part of Blender's design to copy is how it
bounds an area's list without a cap. This project keeps one saved state for each View kind
in each Area (`AreaLayout.view_states`), so the number of registered kinds
bounds an Area's list.

**A view kind is a tag looked up in a registry, never a subclass.** Nothing in
the layout layer knows that any concrete view class exists. Each tag is written
once, as a literal, in the registry (`app/view_registry.py`), so renaming a
class cannot change what a saved file means (`PL-R1WQ`).

**Context sits above tools.** The strip that says *what the numbers are about*
outranks and sits above every tool that acts on them. It shows, for example,
which run, which patient or which model the numbers concern. This placement
serves the project's requirement that a user can never mistake which context a
displayed value belongs to. It also follows Blender's argument for its
information hierarchy (§ "Header, sidebar, toolbar and footer are keyed to
scope of effect"). In this window, the unconditional region with each run's
notices and readouts stays at the top, above the Workspace tabs and the Areas
(`SimulationView._build_page`).

**The layout operations are split, join, swap and border-drag, and the layout is
stored as a tree of nested splitters.** They are `LayoutModel`'s `split`,
`join`, `swap` and `resize`, over the `Split` and `Area` nodes of
`layout/tree.py`. A count of what Blender's shipped layouts contain backs this
decision (`PL-3J2P`, § "The measurement: what Blender's own shipped layouts
actually contain").

**From version 1 of the format, a saved file's root holds one or more windows,
each with a tree of its own.** `layout/serialization.py` writes them as the
`windows` list. This was decided on 2026-09-16, when the area model (roadmap
item 34) was planned across two releases, with break-out into further windows in
the second. The reason is that adding windows to the root later would mean
migrating files in which learners have already saved their workspaces. Break-out
has not been planned for any release since 2026-09-26, but it is still wanted,
only not soon, so the reason still applies.

**This project's one window opens maximized, so every area gets the most room
the screen has** (`PL-Z4K6`; project owner, 2026-09-27, ratified, over raising
`WINDOW_SCREEN_FRACTION` to 0.85). Maximized is not full screen: the title bar
and window controls stay. Starting in full screen was rejected to keep them
(`PL-005`). Un-maximizing the window returns it to a centred size of eight
tenths of the screen (`PL-005`). Blender opens its window maximized. Its window
code sets the default window state (`GHOST_WINDOW_STATE_DEFAULT`) to maximized
(`GHOST_kWindowStateMaximized`), and sizes the default geometry to the main
screen. This code, in `wm_window.cc`, was read through the GitHub mirror on
2026-09-27, because the Manual's page was not reachable from the container.

**Ctrl+PgUp and Ctrl+PgDn step through the workspaces, and wrap round**
(`PL-M352`). They follow the order in which the workspace tabs are drawn.
Blender binds the same keys: Ctrl+PgUp runs Previous Workspace and Ctrl+PgDn
runs Next Workspace (Blender Manual, "Workspaces" page). Blender's function for
cycling workspaces also wraps at both ends (`space_workspace_cycle_invoke` in
`source/blender/editors/screen/screen_ops.cc`, `blender/blender` `main`). Both
sources were read on 2026-10-19.

**Maximize Area is adopted and not yet built** (`PL-5XVQ`; project owner,
2026-11-11, ratified, over leaving a learner to rearrange a Workspace in order
to study one View). In Blender, Maximize Area (Ctrl+Spacebar) expands one area
to fill the window, and keeps the editor's menu bar and the status bar visible.
The same shortcut, or Restore Area, returns the area to its size and restores
the previous layout (Blender Manual, "Areas", sections "Maximize Area" and
"Restore Area"; read 2026-11-11). Here, the maximized Area will fill the room
that the Areas share. The unconditional region stays above it and the use
disclaimer stays below it, because no Workspace may remove either. Blender's
Focus Mode also hides the Topbar and the Status Bar. This project has no
equivalent, for the same reason. This project has no code yet (`PL-VJD2`).

### Diverged, and each divergence has a specific cause

**The occupant of an Area is called a View here, not an Editor** (project owner,
2026-09-17, ratified - chosen over keeping Blender's `Editor`, and over
`Component` and `Widget`). In Blender the word `Editor` fits, because its
editors mostly *edit*, as the 3D viewport, the dope sheet and the text editor
do. This project's Views are the concentration graph, the compartment table, the
MAC readout and the control panel. One takes input, and the rest display
modelled values. Calling the displays editors would tell the user they can
change values that they cannot, and the clinical-output standard in `CLAUDE.md`
treats that as a presentation defect rather than a naming preference. `Widget`
was unavailable because `QWidget` is the base class of every View, and
`Component` was rejected as vaguer, though not wrong. The contract every View
implements is the `View` protocol in `app/view_contract.py`.

Neither Blender's term nor Eclipse's carries over whole, which is the cause of
this divergence (the comparison is in `PL-GPYV`). Eclipse is the closest
precedent. It separates editors, which follow an open-save-close document
lifecycle, from views, which do not. Its Perspective is Blender's Workspace. But
in Eclipse, having several instances is a property of editors, and this project
needs several Views of one kind in a single Workspace: two Areas may hold the
same `ViewKind`.

**A missing or unknown View kind must fail loudly.** When a saved Workspace gives
an Area a View kind that this build does not have, the interface must say so
visibly, and must not quietly show a different View there. The interface code in
`app/area_layout.py` draws a notice in that Area alone, naming the saved kind
(`AreaNotice`). The layout model keeps the kind, so a later save writes it back
(`PL-R1WQ`, `PL-DB5G`). Blender instead silently substitutes a 3D viewport, and
the interface looks normal (§ "Persistence, and what happens when an editor is
missing"). Copying the substitution would break the safety-critical standard in
`CLAUDE.md`. That standard prefers an obvious failure state to a plausible-looking
wrong one, and treats a stale or out-of-context display as a safety failure in
its own right. Blender gives a warning that names an unknown region type, but
none that names a lost editor type. That asymmetry suggests that the substitution
is an oversight to avoid rather than a design to follow.

A saved Qt splitter state (`QSplitter.saveState()`) goes wrong in the same way
as Blender's substitution. Restoring a three-child state into a two-child
splitter returns `True` and produces a plausible-looking wrong layout instead of
failing. This project already ruled out the saved splitter state as a source of
truth, partly for that reason (`PL-C842`). It saves its own layout value
instead (`layout/serialization.py`).

**A required value is never hidden to make room.** When a region will not fit,
Blender makes it disappear (§ "An editor cannot refuse a size, and there is no
minimum-size contract at all"). That is a defensible answer for a 3D content
tool, where a hidden sidebar costs a user one keystroke. In this project it is
directly unsafe. A set of displayed values is unconditional: no Workspace may
remove them, and nothing may cover them (`docs/MODEL.md` § "Minimum displayed
outputs"). Silently collapsing one of those values is exactly the failure that
the unconditional set exists to prevent. Where any other display cannot fit, the
interface must say so rather than quietly shrink it away. `layout/sizing.py`
decides whether a View fits, and `app/area_layout.py` says when one does not.

The unconditional set (`app/unconditional_set.py`) sits outside the area system.
Each top-level window keeps its own unconditional region outside its own area
system, holding the invariant tier and the run that window shows (restated on
2026-09-16, when the project settled what a broken-out window must display). The
per-substance tier appears once, in a main window that cannot be closed while
another window is open. `docs/MODEL.md` gives the rule that nothing may cover the
unconditional values, and its one limit. They are cited here rather than
restated, so that the safety rule is stated in one place. The limit is that an
application can observe its own windows, but not what another application has
drawn over them.

**An Area has a minimum size, and says so when it cannot be given it.** Blender
honours no minimum size that an editor states
(§ "An editor cannot refuse a size, and there is no minimum-size contract at
all"). Here, an Area that cannot be given the size its View needs says so rather
than collapsing it, and a border drag stops where an Area beside the moved line
reaches its minimum size (`PL-K285`; `border_range` in
`src/anesthesia_sim/layout/sizing.py`).

**Each View's isolation has to be built, not inherited from Blender.** Blender
hands each editor a context through which it can reach the window, the screen
and every other Area, and § "An editor is isolated by convention, not by
construction" counts the editors that do. Here, each View should be handed what
it draws, through `ViewContext` and `ViewTick`, and given no route to its
container at all, so that Views stay interchangeable by construction. This
narrows Blender's contract on purpose. Isolation is cheap to build now and
expensive to add later, which is why the project's rule file for interface areas
(`.claude/rules/ui-areas.md`) already asks for it in Views written before the
area system exists.

**A View's container sits behind a layout model of this project's own.** As with
a View, the container's isolation has to be built (`PL-C842` has the
recommendation and the evidence). The container, `AreaLayout` in
`app/area_layout.py`, draws the Areas from `LayoutModel` in `layout/model.py`,
which loads no toolkit.

**Prune the contract of a View instead of letting it grow.** Blender's contract
for an editor (`SpaceType`) is a struct of metadata and function pointers. It
has hooks that nothing implements and a field that nothing assigns, and the
design gives no sign that they are unused (§ "What an editor must implement").
This project's contract for a View is the `View` protocol in
`app/view_contract.py` (`PL-TH35`). A test fails on any member of the contract
that `app/area_layout.py` never calls, so the contract cannot keep a hook that
nothing uses
(`test_every_member_of_the_contract_has_a_call_site_in_the_adapter`).

**The container draws each Area's header, not the View** (`PL-TH35`). In
Blender an editor declares and draws its own header region (§ "What an editor
must implement"). Here `app/area_layout.py` draws the header, so every View gets
the same one. The header holds the View chooser, and a right-click on it opens
the Area menu. `app/view_contract.py` lists the header among what is not the
View's, so a View that drew one would give its Area a second header.

**A drag moves every border on the dragged line, as in Blender.** Blender's
default drag moves the whole chain of borders (§ "How a layout is built, and how
far the operations reach"), while a handle in a tree of splitters moves only
itself. In Blender's shipped Workspaces the two differ only at one four-way
junction, in the Shading Workspace's block of four editors, which one template
Workspace inherits (§ "The result"). The layout model keeps its tree rather than
adopting Blender's graph of shared vertices. To recover the one thing that the
tree loses against that graph, a drag moves together every border that is
collinear with the dragged one and adjacent to it. Because a tree has no vertices
to share, the layout model finds the dragged line from where the borders lie
(`LayoutModel.borders()`, `PL-1FT6`). One difference remains: here, two borders
that a drag brings into line are one line from then on. Blender's border drag
merges no vertices and removes only duplicate edges (`area_move_exit` in
`screen_ops.cc`, `blender/blender` `main`, read 2026-10-12), so its two edges
stay two until the user merges them on purpose.

**Every border off the dragged line keeps its place in the window.** Blender moves
only the vertices flagged as on the dragged line (`area_move_apply_do` in
`screen_ops.cc`, `editflag`; read again 2026-10-18), and the layout model moves
only the borders on it (`LayoutModel.resize()`). Suppose Area 1 fills the left
half of the window, and the right half holds Areas 2 and 4 side by side above
Area 3 (`row[1, column[row[2, 4], 3]]`). Dragging the border between the halves
to a quarter of the way across keeps Area 4 a quarter of the window wide
(`PL-5HSG`; project owner, 2026-10-12, ratified, over keeping the proportions
inside each child of the dragged split). A Qt splitter reports the drag of one
handle only, so the interface code in `app/area_layout.py` turns each drag into
a resize of the layout model, then sets every splitter from the result. The
whole line then moves under the pointer, and no other border does (`PL-W9P6`).

**A join depends on the two Areas' rectangles, as Blender's does.** Blender
decides whether two Areas can join from their corners alone. It compares the two
rectangles' edges (`area_getorientation` in
`source/blender/editors/screen/screen_edit.cc`, `blender/blender` `main`, read
2026-10-18), then moves the vertices (`screen_area_join_aligned`), so no build
order exists for a join to depend on. A tree does have one wherever four Areas
meet at a point: a 2x2 grid is either a column of two rows or a row of two
columns. So the layout model's join does not need the two Areas to share one
split (`LayoutModel.join()`). It merges the two rectangles. Then it finds the
lowest split that holds both and divides that split's region again by straight
cuts. Every join that Blender makes between two Areas sharing a whole edge is
made here, with two exceptions. The first is a join that would leave an
arrangement that no straight cuts divide (`PL-3J2P`). The second is a join that
would nest a split past the tree's maximum depth (`PL-G60V`; project owner,
2026-10-12, ratified, over taking or refusing such a join by which split came
first). A split past that depth is refused too (`split`). Blender's join also
trims two Areas that share only part of an edge, as § "How a layout is built,
and how far the operations reach" describes. The layout model joins only Areas
that share a whole edge.

**A border takes the keyboard focus, and the arrow keys move it.** Blender
gives a border no keyboard route. Its Manual's "Areas" page describes resizing
by drag alone, and a right-click on a border opens an "Area Options" menu that
does not resize (read 2026-10-19). The v0.6.0 scope in `ROADMAP.md` requires
every layout operation to work without a drag, so this project follows the W3C
WAI-ARIA Authoring Practices "Window Splitter" pattern instead (read 2026-10-19
from `w3c/aria-practices` `main`, since `w3.org` refused the connection). Each
border is in the tab order, and an arrow key along its axis moves it one step.
With Shift held, the border moves alone, as it does in a drag with Shift. Escape
puts back the layout as it was when the border took the focus. The pattern's
Enter, which collapses a pane, is not offered, because an Area cannot be
collapsed below its minimum size (`PL-K285`). Each Area's menu also lists the
Area's borders under Resize, and choosing one gives that border the focus
(`PL-M352`).

**The Layout menu opens from the tab strip, not from a menu bar.** The strip is
`WorkspaceTabs` in `app/workspace_tabs.py`. The menu lists every Workspace,
steps to the previous or next one, and holds the current Workspace's rename,
duplicate, reset and delete (`PL-M352`). Blender's top bar puts its menus
and its Workspace tabs in one row. A separate menu bar would cost this window a
row of height on Windows and Linux, where the charts already needed 70 to 80 px
more height on the 1366 by 700 laptop reference (`PL-QLZ5`).

**The menus open on a right-click, as in Blender, and no header carries a menu
button** (project owner, 2026-10-19, ratified, over keeping a button in each
Area header and at the tab strip's end, and over removing the menus
altogether). Neither an Area's header (`AreaFrame`) nor the tab strip
(`WorkspaceTabs`) carries one. On his own screen the owner found the "Area" and
"Layout" buttons "overlapping and intrusive", and Blender's headers carry no
such button. In Blender, a right-click on a header opens its context menu, which
holds the splits, Maximize Area and Close Area. A right-click on a border opens
"Area Options", with the splits, the joins and Swap Areas. A right-click on a
Workspace tab opens that tab's menu (Blender Manual: "Regions", section
"Header"; "Areas", section "Area Options"; "Workspaces", section "Controls";
read 2026-10-19).

Here, a right-click anywhere on an Area's header opens the Area menu
(`AreaFrame._open_menu`), and a right-click on the tab strip outside a tab
opens the Layout menu (`WorkspaceTabs.contextMenuEvent`). Each tab's own
menu also holds Previous and Next Workspace, Save as default, Restore shipped
Workspaces and Reset all layouts. The keyboard still reaches every entry: the
Menu key or Shift+F10 opens the Area menu from the View chooser, and a tab's
menu from the tab (`PL-M352`). A right-click on a border opens nothing yet, and
the Area menu holds what Blender puts in its border menu. The View chooser stays
in the header, as Blender keeps its Editor Type selector first in every header.

**Ctrl and a corner drag swap two Areas, as in Blender.** The user holds Ctrl
while pressing an Area's corner, then releases over any other Area in the
window, and the two need not be side by side (Blender Manual: "Areas", section
"Swapping Contents", read 2026-10-19). A preview outlines both Areas while the
user drags (`PL-R5G4`, which added the gesture). `_CornerZone` in
`app/area_layout.py` starts the swap. The Area menu's "Swap with" makes the
same swap.

### Refused

**The layout is not represented as a shared-vertex graph.** It is the tree of
`Split` and `Area` nodes in `layout/tree.py`. The graph is strictly more
expressive, but a measurement of thirty-two of Blender's shipped workspaces
found none that needs what the graph adds. Adopting it would leave one person
maintaining the code for a planar subdivision forever. An item records the
condition under which the project would adopt the graph (`PL-3J2P`).

**This project's occlusion rule does not rest on Blender's reason for a tiled
interface**, as § "Blender's reason for non-overlapping is not this project's
reason" sets out. The rule here is that the values which must always show sit in
the unconditional region, which `SimulationView._build_page` keeps outside the
Areas. Blender does prove that a tiled interface can be workable and pleasant at
the scale of a professional tool.

## Attribution

This project's workspace, area and editor model is based on Blender's, studied
from its published source and its design documentation. Blender is developed by
the Blender Foundation and its contributors. Its source is licensed
GPL-2.0-or-later per file, and the work as a whole is licensed GPL-3.0-or-later.
The Blender Manual is licensed CC-BY-SA 4.0 by the Blender Documentation Team,
and the Blender Developer Documentation by the Blender Developer Documentation
Team.

**No Blender code is used in this project, and none of Blender's documentation
is reproduced here.** What was taken is a design, described in this project's
own words.

`ROADMAP.md` item 34 records that this design comes from Blender, and `README.md`
§ "Acknowledgements" has credited Blender for it since v0.6.0 (`PL-RTG9`). That
release, "the layout is the reader's", was the first in which the shipped
interface followed the design. Until then only this document credited Blender,
because a README sentence saying that the interface is modelled on Blender's
would have described software that did not exist.

## Pages read on 2026-10-25

Each page was downloaded whole with `curl` through this environment's proxy and
read as text. On 2026-10-25, `projects.blender.org` refused to serve its pages
to a client that does not run JavaScript, so task T91536 and commit `4cf4bb2664`
were read through that forge's public API, at
https://projects.blender.org/api/v1/repos/blender/blender/.

- Human Interface Guidelines, Design Paradigms:
  https://developer.blender.org/docs/features/interface/human_interface_guidelines/paradigms/
- Human Interface Guidelines, Anatomy of an Editor:
  https://developer.blender.org/docs/features/interface/human_interface_guidelines/editors/
- Human Interface Guidelines, Layouts:
  https://developer.blender.org/docs/features/interface/human_interface_guidelines/layouts/
- Human Interface Guidelines, Sidebar Tabs:
  https://developer.blender.org/docs/features/interface/human_interface_guidelines/sidebar_tabs/
- Human Interface Guidelines, Modal Interfaces:
  https://developer.blender.org/docs/features/interface/human_interface_guidelines/modal_interfaces/
- Developer Documentation, Screen:
  https://developer.blender.org/docs/features/interface/screen/
- Developer Documentation, Window:
  https://developer.blender.org/docs/features/interface/window/
- Blender Manual, Workspaces:
  https://docs.blender.org/manual/en/latest/interface/window_system/workspaces.html
- Blender Manual, Regions:
  https://docs.blender.org/manual/en/latest/interface/window_system/regions.html
- Blender 2.80 release notes, User Interface:
  https://developer.blender.org/docs/release_notes/2.80/ui/
- Blender 3.0 release notes, User Interface:
  https://developer.blender.org/docs/release_notes/3.0/user_interface/
- Task T91536, "Swap Tool Settings and Headers in Editors", and commit
  `4cf4bb2664`: https://projects.blender.org/blender/blender/issues/91536 and
  https://projects.blender.org/blender/blender/commit/4cf4bb2664ebe145dac9715bbbfcc2b96f5ff175
- Blender 2.8 user-interface workshop write-up:
  https://archive.blender.org/wiki/2015/index.php/Dev:2.8/UI/Workshop_Writeup/
- Reynish W. "The Evolution of Blender's User Interface." Blender Conference,
  2008: https://download.blender.org/documentation/bc2008/evolution_of_blenders_ui.pdf
- Felinto D. "Beyond Mouse & Keyboard." Blender Developers Blog, 24 July 2025:
  https://code.blender.org/2025/07/beyond-mouse-keyboard/
- The two licence pages: https://developer.blender.org/docs/license/ and
  https://docs.blender.org/manual/en/latest/copyright.html
