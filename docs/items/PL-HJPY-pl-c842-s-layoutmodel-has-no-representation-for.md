---
id: PL-HJPY
title: PL-C842's LayoutModel has no representation for more than one window, which item 34's break-out requires and which PL-C842 itself recorded as the part most likely to change shape
status: untriaged
feature: interface-areas
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
