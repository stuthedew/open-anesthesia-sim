---
id: PL-FTP5
title: Record the Blender study protocol and the interface model's design provenance in a durable doc, so a session building the layout knows which Blender sources it may read, what it may carry across, and what the project attributes - the rule currently exists only as a paragraph inside ROADMAP item 34
status: untriaged
touches: README.md, docs/
added: 2026-09-16
---

**Problem.** Record the Blender study protocol and the interface model's design provenance in a durable doc, so a session building the layout knows which Blender sources it may read, what it may carry across, and what the project attributes - the rule currently exists only as a paragraph inside ROADMAP item 34

**Why it matters.** The project owner asked on 2026-09-16 whether there is a
good-faith way to study Blender's architecture for inspiration. The answer is
yes, and it has enough moving parts that a session meeting the question cold
will either re-derive it (a full research round) or guess. It currently lives
only as one paragraph inside ROADMAP item 34, which a session reads only if it
happens to be scoping item 34.

Four things the record should carry:

1. **Reading is not one of the GPL's restricted acts.** GPLv2 § 0: "Activities
   other than copying, distribution and modification are not covered by this
   License; they are outside its scope." Studying Blender's source is
   unrestricted; what is restricted is copying, modifying, translating (§ 2
   names translation explicitly) and distributing.
2. **Architecture sits mostly on the unprotectable side, but not entirely.**
   17 U.S.C. § 102(b) excludes "any idea, procedure, process, system, method of
   operation, concept, principle, or discovery", while *Computer Associates
   Int'l v. Altai*, 982 F.2d 693 (2d Cir. 1992) holds that non-literal
   structure can be protected and gives the abstraction-filtration-comparison
   test for deciding which. Practical consequence: the higher the abstraction
   at which a concept is carried across, the safer — "tiled non-overlapping
   panes, each hosting a swappable view kind, saved as named workspaces" is a
   method of operation; a transliterated `bScreen`/`ScrArea`/`ARegion` struct
   graph is structure.
3. **The prose sources are both better and more encumbered.** Developer Docs
   and HIG carry the rationale; both are CC-BY-SA 4.0 (share-alike), so
   paraphrase and cite, never paste. See `PL-P5QX`.
4. **What the project attributes.** A README or docs line saying the
   workspace/area/editor model is modeled on Blender's, studied from its
   published design documentation. Not legally required for ideas; it is this
   project's own provenance standard, and it is the answer to the spirit
   question rather than the letter one. Blender's own Copyright Rules handbook
   draws the same line in the other direction — it bars copyrighted elements
   from other software while encouraging designs that build on Blender's own
   design history.

**Done when.** The protocol and the attribution exist somewhere a session
building the layout will actually read, and ROADMAP item 34 points at it rather
than restating it.

**Scope note.** This is a provenance/docs item, not a licensing opinion, and it
is not a scoping round for item 34.

---

## What the 2026-09-16 read found

Read at `blender/blender` HEAD `931bb2e7` (Blender 5.3), shallow clone, headers
and struct definitions only — no implementation bodies. Described below in this
project's own words; nothing is quoted from Blender's prose or transliterated
from its code. Paths are given so a later session can re-check a claim without
repeating the survey.

**1. The layout is a vertex/edge graph, not a nested-splitter tree.**
`bScreen` (`source/blender/makesdna/DNA_screen_types.h:95`) owns three parallel
lists — vertices, edges, areas. Each `ScrArea` (`:610`) names four corner
vertices, and neighbouring areas *share* those vertex objects. Split, join,
swap and resize are therefore edits to a small graph, and "drag one border and
every aligned border moves with it" is a consequence of the representation
rather than a feature anyone implemented. This is the one genuine architectural
fork for this project; `PL-3J2P` carries the decision.

**2. An area's editor is a tag plus a registry lookup, never a subclass.**
`ScrArea.spacetype` is an enum; `ScrArea.type` points at a registered
`SpaceType`. Nothing in the layout layer knows a concrete editor exists.

**3. An area keeps a stack of the editors it previously held.**
`ScrArea.spacedata` is a list, first entry active. Changing an area's editor
pushes the old state down rather than destroying it, and changing back restores
it. This is why a round trip preserves zoom and scroll — and it is exactly what
the "induction workspace, graph zoomed in" case in ROADMAP item 34 needs.

**4. `SpaceType` is a vtable-as-data, and it makes each editor own its own
persistence.** (`source/blender/blenkernel/BKE_screen.hh`.) Alongside the
lifecycle hooks it carries `blend_write` / `blend_read_data`, plus
`operatortypes`, `keymap`, `dropboxes` and a context callback. The layout system
delegates serialization instead of knowing about it — the answer to "how does a
workspace save without the layout code knowing what an F_A/F_I chart is".

**5. Every user action is a registered operator.** `wmOperatorType`
(`source/blender/windowmanager/WM_types.hh`) carries `poll` / `exec` / `invoke` /
`modal` / `cancel` plus a string id and introspectable properties. The header
states that `exec` may not touch interface code or input-device state — Blender
enforcing at its own API contract the separation `CLAUDE.md` requires here
("no simulation calculations in UI callbacks"). One `poll` rule then drives
every enable/disable in the interface uniformly.

**6. Change propagation is a tagged broadcast, not a direct call.** A
`wmNotifier` packs category/data/subtype/action into 32 bits; emitters name what
changed and know nothing about listeners; each `SpaceType.listener` decides
whether it must redraw. The analogue: the integrator emits "sim time advanced"
and every open pane decides for itself.

**7. Workspace, window and layout are three things joined by a relation table.**
`WorkSpace` holds named layouts; `WorkSpaceDataRelation` remembers, per
(window, workspace) pair, which layout was last active;
`WorkSpaceInstanceHook` exists specifically to keep window state out of
workspace state (`DNA_workspace_types.h:127-265`). `pin_scene` is the feature
item 34 already records as worth copying.

**8. Layout mutation is deferred out of the event loop.** `WorkSpaceInstanceHook`
carries temporary workspace/layout slots because switching inside a running
handler would invalidate the context the handler is using. Queue the switch,
apply between events. A trap worth knowing before writing the first handler.

**9. The same registry shape is how features stay modular.**
`ModifierTypeInfo` (`source/blender/blenkernel/BKE_modifier.hh`) is `SpaceType`'s
shape applied to geometry: metadata plus function pointers, registered once. The
simulation-relevant callbacks are all *declarative* — `depends_on_time`,
`update_depsgraph`, `is_disabled`, `required_data_mask`. A stage declares its
dependencies and its applicability; the dependency graph then computes
evaluation order and schedules it (`source/blender/depsgraph/DEG_depsgraph.hh`).
Nobody hardcodes a pipeline. That is the transferable answer to "modular
simulation features".

**10. The coordination layer is thin.** `source/blender/windowmanager/` is 80
source files; `source/blender/editors/` is 1164. The ratio is the design goal.
