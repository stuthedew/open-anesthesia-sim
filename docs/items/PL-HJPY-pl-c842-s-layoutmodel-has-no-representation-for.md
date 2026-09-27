---
id: PL-HJPY
title: PL-C842's LayoutModel has no representation for more than one window, which item 34's break-out requires and which PL-C842 itself recorded as the part most likely to change shape
priority: P2
effort: M
status: blocked
classes: planning
feature: interface-areas
blocked-by: PL-1FT6
touches: docs/ARCHITECTURE.md, ROADMAP.md
added: 2026-09-16
---

**Problem.** PL-C842's LayoutModel has no representation for more than one window, which item 34's break-out requires and which PL-C842 itself recorded as the part most likely to change shape

**Problem.** `PL-C842` is closed and the container decision it took describes one tree: `LayoutModel` as "a tree of `Split(orientation, children, sizes)` and `Pane(pane_id, view_kind)`", with one adapter module building the widget tree from it. It then records, in its own list of thin evidence, that break-out windows are unmodelled and are the part most likely to change the model's shape. Nothing since has designed that, and `grep -ril "top-level window" docs/items/` returns only `PL-C842`, the closed `PL-4D1M` and `PL-WLWY` - the first flagging the gap, the other two recording break-out as intent.

The questions the model cannot currently answer: what holds the set of windows; whether a workspace owns several layouts or one layout spans windows; whether break-out moves the pane or copies it, and what the vacated pane becomes; what happens to the broken-out area when its window is closed; how a pane is addressed across windows so that `swap` and `set_view` mean something between them; and whether the border-chain query - "a `borders()` query returning, for any handle, the set of handles collinear and adjacent to it" - stops at a window boundary, which it must, because two windows' handles can be screen-collinear and belong to different trees.

**Why it matters.** `PL-C842` made the multi-window case part of its own argument for owning the model - "`saveState()` is per-splitter; a multi-window layout has no single call to save. A structure spanning windows is required either way — the only question is whether it is designed or accreted" - and then did not design it. The cost of accretion here is not a refactor of code the project owns: the serialized form is a file the learner has saved their own workspaces into, so a root that gains a window set later is a migration with a compatibility rule attached, in a load path that is also supposed to fail loudly rather than guess. The answer to the break-out display question decides part of this one - a privileged main window that cannot close while break-outs exist is a constraint on the model, not on the window manager - so that decision comes first.

**Done when.** The multi-window relation is designed and recorded alongside the rest of the layout model's design: what owns the set of windows, what break-out does to the source pane, what closing a broken-out window does to its contents, how panes are addressed across windows, and where the border-chain query terminates. It is recorded before any code serializes a layout, so that the first version of the saved format already has a place for it.

*Basis (lens `layout-ops`).* docs/items/PL-C842-decide-whether-the-layout-container-sits-behind.md, § "Where the evidence is thin, stated plainly": "**Break-out windows are still unmodelled.** Item 34 wants an area taken into its own top-level window. Blender's answer is a second screen under the same workspace, with the per-window relation held separately. Nothing here designs that, and it is the part most likely to change the model's shape."

## Area-model audit (PL-BNYF)

**Disposition: `missing-prereq`.** Filed 2026-09-16 by the area-model queue audit (`PL-BNYF`), which swept 49 open and untriaged items and seven gap lenses against `ROADMAP.md` item 34, `docs/interface-provenance.md` and `.claude/rules/ui-areas.md`. Each candidate was checked against the store before it was filed, so a gap an existing item already covers is not here.

---

## Narrowed 2026-09-16 to the representation

Scoping item 34 split it across two releases, and this item goes wholly to the
first. What it owes v0.6.0 is the **serialized shape**: what owns the set of
windows, whether a Workspace owns several layouts or one layout spans windows,
how an Area is addressed across windows so `swap` and `set_view` mean
something between them, and where the border-chain query terminates - which it
must at a window boundary, because two windows' handles can be screen-collinear
and belong to different trees. That lands in `PL-1FT6`'s model at version 1 even
though v0.6.0 opens one window, which is this item's own argument: a root that
gains a window set later is a migration against files a learner has already
saved their Workspaces into.

**What break-out *does* - the operation, the window's lifetime, what happens to
the source Area and to a closed window's contents - is break-out's own
build**, which has had no release since 2026-09-26 (`PL-V1Y7`): `ROADMAP.md`
item 34 carries it as its unscheduled second half, and `PL-Y04W`, its build
item, was dropped that day. Two of the questions this item listed are
answered already and are recorded rather than re-derived: what a second
window owes the display is `PL-W54S`'s tier split, and the lifetime
constraint is that the main window refuses to close while any other is open,
which `PL-Y04W`'s brief records with the measured Qt trap behind it. The
window set this item puts in the root is kept all the same: it is what keeps
break-out possible without a migration.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 1.

---

## Design round 2026-09-27: recommendations

Recommendations, not decisions: the thread that records the project owner's
answer marks each `(project owner, DATE, ratified)` or replaces it. Nothing
here is built; the shape lands in `PL-1FT6`'s model at version 1.

**Q1. What owns the set of windows?**
**Recommendation: the Workspace.** A Workspace's layout is an ordered list of
window trees; `windows[0]` is the main window by construction, and the model
refuses to remove it or to empty the list. One Workspace is active for the
whole application at a time, so switching tabs switches every window together.
Blender's structures were read for the shape and then narrowed: `WorkSpace`
holds a list of `WorkSpaceLayout`s, and a per-window `WorkSpaceInstanceHook`
lets each window show a different Workspace
(`source/blender/makesdna/DNA_workspace_types.h`, `blender/blender` `main`,
read at `raw.githubusercontent.com` on 2026-09-27). That per-window freedom is
refused here, because `docs/MODEL.md`'s allocation - the per-substance tier
once, in the main window; the invariant tier and the run's name in every window
- has one answer only while every window shows the same Workspace and therefore
the same run binding. *Alternative refused:* a root-level window list with an
active Workspace per window, Blender's runtime shape, which reopens whose
per-substance tier the main window carries.

**Q2. Several layouts, or one layout spanning windows?** Several: one tree per
window, because a splitter tree is a rectangle and cannot span two. It follows
from Q1.

**Q3. How an Area is addressed across windows.** **Recommendation:** Area ids
are unique across the Workspace, not per window, allocated by the model from a
counter the Workspace stores (`next_area_id`) and **never reused**, because the
per-Area retained View state (`PL-WV9K`) is keyed by Area id and a reused id
would resurrect another Area's settings. `swap(a, b)` and `set_view(a, kind)`
take Area ids, so both mean something across windows in the model; whether the
interface offers a cross-window swap is break-out's own build.

**Q4. Where the border-chain query terminates.** At the window boundary, by
construction: `borders(handle)` is defined over the tree that owns the handle,
and a handle belongs to exactly one window. The test is two windows whose
handles are screen-collinear, with neither chain containing the other's handle.

**Q5. The serialized shape, which is what this item owes v0.6.0.**
**Recommendation:** three layers, each pure Python in the layout package:

- `LayoutModel` (`PL-1FT6`): `windows`, a list of trees, a tree being nested
  `Split(orientation, sizes, children)` and `Area(id, view)`. **Sizes are
  fractions of the split's extent, never pixels**, so a file is
  machine-independent and the too-small case (`PL-K285`) is decided against
  the screen it is opened on. No window geometry is stored (out of scope for
  v0.6.0, `ROADMAP.md`). The unconditional region has **no entry**, because it
  is structural (`PL-NWTM`).
- `Workspace` (`PL-WV9K`): name, origin, pinned run, its `LayoutModel`,
  `next_area_id`, and per-Area View state.
- `WorkspaceSet` (`PL-SSQW` persists it): the ordered Workspaces, the active
  one, and `schema_version` at the top of the one file.

Illustrative, not the schema:

```json
{"schema_version": 1, "active": 1, "workspaces": [
  {"name": "Induction", "origin": "shipped:induction", "pinned_run": null,
   "next_area_id": 3,
   "windows": [{"tree": {"split": "horizontal", "sizes": [0.7, 0.3],
                          "children": [{"area": 1, "view": "concentration_chart"},
                                       {"area": 2, "view": "agent_accounting"}]}}],
   "view_state": {"1": {"concentration_chart": {"state_version": 1}}}}]}
```

**Break-out's reservation, and nothing more.** Taking an Area into its own
window is expressible with what version 1 already has: remove the Area from its
tree, its space going to its sibling exactly as `join` gives it, and append a
window whose tree is that Area. The schema needs no further field for it, so
none is added and no code for it is written now.

**What this settles for the queue.** Once ratified, this item's design half is
done, and its `blocked-by: PL-1FT6` reads backwards (the 2026-09-27 report
flagged the edge): `PL-1FT6`'s build carries this shape rather than preceding
it. The thread recording the answer decides whether this item closes with
`PL-1FT6` or is folded into it.

## Answers 2026-09-27

**Every recommendation above: ratified** (project owner, 2026-09-27,
ratified, over the alternative each names). The one decision the owner
specified otherwise is `PL-WV9K` Q4: layouts are saved by an explicit "Save
as default" action in the layout menu, not automatically; `PL-WV9K`
§ "Answers 2026-09-27" carries that design.
