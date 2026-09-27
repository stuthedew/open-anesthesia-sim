---
id: PL-WV9K
title: Nothing defines a Workspace as an object above PL-C842's layout tree - the named set, the tab lifecycle with item 34's last-workspace floor, and where a learner's own presets are kept
priority: P2
effort: M
status: blocked
classes: planning
feature: interface-areas
blocked-by: PL-1FT6
touches: ROADMAP.md, docs/ARCHITECTURE.md
added: 2026-09-16
---

**Problem.** Nothing defines a Workspace as an object above PL-C842's layout tree - the named set, the tab lifecycle with item 34's last-workspace floor, and where a learner's own presets are kept

**Problem.** `PL-C842` decided the container and specified the lower of the two adopted levels only: "a tree of `Split(orientation, children, sizes)` and `Pane(pane_id, view_kind)`, with `split`, `join`, `resize`, `swap`, `set_view`, and `to_dict()`/`from_dict()` over versioned JSON". `docs/interface-provenance.md` adopts *two* levels, and the upper one has no design and no item. Grepping `docs/items/` for `workspace` returns `PL-3J2P`, `PL-C842`, `PL-FTP5`, `PL-LH18`, `PL-TH35`, `PL-H620`, `PL-4D1M`, `PL-WLWY`, `PL-P5QX`, `PL-RTG9` and `PL-BNYF` - the representation decision, the provenance, the interim `app/` rule, the view contract, the vocabulary, the minimum display, the licence, the attribution and this audit. None of them says what a workspace *is*.

Four things the upper level owes, all named in the sources and none filed:

- **The set and its order.** Item 34: workspaces are "presented as tabs and each geared to a task, which the user can reorder, duplicate and delete".
- **The floor.** Item 34 records it as a precedent worth copying: "Blender refuses to delete the last workspace - a floor it enforces structurally rather than by warning, which is the same shape `PL-WLWY` settled for the minimum display." Structural enforcement is a property of the model, not of a dialog, so it has to be in the type.
- **Shipped defaults against the learner's own.** Item 34 wants named task presets - an induction workspace with the graph zoomed in, a big-picture maintenance one - "alongside workspaces the learner creates for themselves", so the model has to distinguish what ships from what the learner saved and say what "reset" means.
- **Where the saved set lives.** Nothing under `src/anesthesia_sim/` writes to disk: no `QSettings`, no config path, no `json.dump`, no `write_text`, and the only `Path(` in the package is `app_metadata.py:78` reading git metadata. A saved workspace set would be this application's first user-writable state, and its location, its schema version and migration policy, and its behaviour on a file that is missing, unreadable or a version this build does not know are all undecided. `CLAUDE.md`'s "Keep agent/model parameters in validated, versioned data files" governs what ships and says nothing about what the learner writes.

**Why it matters.** "Presets that are the user's to customize and save rather than a fixed set shipped with the application" is one of the four properties the project owner named when they asked for this, and it is the one that needs an object `PL-C842` did not design. The load path is also a new failure surface in an application that currently has none: `PL-C842` settled loud failure for one case - "Deserializing a layout naming an unknown `view_kind` fails visibly. It does not substitute, and it does not drop the pane" - and a corrupt, truncated or future-versioned workspace file is the same shape of failure with no rule yet, in a project whose standard "prefers an obvious failure/error state to displaying a plausible-looking number".

**Done when.** A decision is recorded - in `ROADMAP.md` item 34 and wherever the layout model's design is written - naming what a workspace carries beyond its layout, how the set behaves (order, duplicate, rename, delete, with the last-workspace floor enforced by construction rather than by a warning), whether shipped defaults are data files or code, where the learner's own set is written on each platform, and what the application does with a workspace file that is missing, unreadable or of an unknown version. The failure answer matches `PL-C842`'s unknown-view-kind rule rather than substituting a default layout silently.

*Basis (lens `layout-ops`).* docs/interface-provenance.md § "Adopted": "**Workspace and layout as two levels, not one.** The 2.8 split — a workspace is a task-level object, a layout is the geometry of areas in one window — is what makes `ROADMAP.md` item 34's wanted behaviour possible at all. Item 34 already wants a workspace to pin which **run** it shows, the analogue of Blender's pin scene. If a workspace were only a layout there would be nowhere to put that."

## Area-model audit (PL-BNYF)

**Disposition: `missing-prereq`.** Filed 2026-09-16 by the area-model queue audit (`PL-BNYF`), which swept 49 open and untriaged items and seven gap lenses against `ROADMAP.md` item 34, `docs/interface-provenance.md` and `.claude/rules/ui-areas.md`. Each candidate was checked against the store before it was filed, so a gap an existing item already covers is not here.

---

## Design round 2026-09-27: recommendations

Recommendations, not decisions: the thread that records the project owner's
answer marks each `(project owner, DATE, ratified)` or replaces it. Three are
learner-visible and the owner's: automatic persistence, shipped Workspaces
editable in place, and what a Workspace switch does to the run.

**Q1. What a Workspace carries beyond its layout.** **Recommendation:**
`name` (non-empty, unique in the set), `origin` (`shipped:<id>` or `mine`),
`pinned_run` (a run identity from `PL-7Z84`, or none), its `LayoutModel`
(the window set, `PL-HJPY`), `next_area_id`, and `view_state` (per Area id,
per kind, opaque Mappings from `PL-TH35`). Nothing else: no reader
preferences (roadmap entry 11's third tier is excluded from Workspaces), no
run data, no window geometry. Blender's `WorkSpace` carries more (object
mode, tool settings, an add-on filter, `DNA_workspace_types.h`), each tied to
a concept this project does not have.

**Q2. How the set behaves.** `WorkspaceSet` is ordered with an active index
and offers `add`, `duplicate` (inserted after its source as "<name> (copy)",
origin `mine`), `rename` (refused when empty or taken), `move`, `remove` and
`activate`. **The last-Workspace floor is enforced by construction:** `remove`
raises `LastWorkspace` when it would empty the set, and the interface also
disables the action for a lone Workspace so the error is never the first
thing a reader meets. Blender's precedent, verified at the source
(`source/blender/editors/screen/workspace_edit.cc`, read 2026-09-27):
`ED_workspace_delete` returns false when the workspace list `is_single()`,
and reordering goes through `BKE_id_reorder`.

**Q3. Shipped defaults: data or code, and editable?** Data:
`src/anesthesia_sim/data/workspaces/*.json`, validated like every shipped
parameter file (`PL-KXTL`). **Recommendation (learner-visible): shipped
Workspaces are editable in place**, with three restore actions - "Reset this
Workspace" (shipped origin only, from its JSON), "Restore shipped Workspaces"
(re-adds deleted ones), and "Reset all layouts" (replaces the set, after
confirmation, the one destructive step). *Alternative:* copy-on-write, where
editing a shipped Workspace silently forks it; refused because the fork is a
hidden mode and the reader ends up with two tabs of one name.

**Q4. Saving.** [superseded 2026-09-27; see "Answers 2026-09-27" below]
The recommendation was automatic persistence of every change through
`PL-SSQW`'s debounced atomic write, with no Save action, over an explicit
save, on the grounds that an explicit save introduces an unsaved-changes mode
and a layout lost at quit is a stale-state hazard. **The project owner
specified the explicit save instead** (2026-09-27); the answer below carries
the design.

**Q5. Where the set is written and what a missing, unreadable or
unknown-version file does.** Decided in `PL-SSQW`; the answers are
consistent with `PL-C842`'s unknown-View-kind rule: nothing is substituted
silently, every fallback is announced in the interface.

**Q6. What switching Workspaces does to the run.** **Recommendation
(learner-visible): nothing.** Runs belong to the session (`BranchedCase`);
a Workspace only decides which of them its Views show. With `pinned_run`
set, each View binds to it; unpinned, Views follow the session's displayed
run(s), and the shipped defaults ship unpinned. "Pin current run" on the tab
sets it. A pinned run that is not present gives every bound Area the named
"run not present" state (`PL-7Z84`), never a silent rebind, and never
touches the simulation. Blender's pin scene does more (it changes the
window's active scene on switch, `workspace_scene_pinning_update` ->
`WM_window_set_active_scene`), which here would mean a layout change moving
the simulation, refused.

**[done 2026-09-27, in the design thread itself, once the owner answered
there] Next, for the thread that records the answers (written 2026-09-27
because the design thread stopped for length, not for the work).** The seven
`interface-areas` design items - `PL-HJPY`, `PL-R1WQ`, `PL-SSQW`, `PL-TH35`,
`PL-K285`, `PL-WV9K`, `PL-50PZ` - each carry a "Design round 2026-09-27"
section. When the project owner answers: mark each recommendation
`(project owner, DATE, ratified)` or replace it with what they specified,
in the item that holds it; run `bin/docket yield` on the branch
`claude/project-thread-dwvw9y` (no claim was taken: `bin/docket claim`
refuses a `blocked` item, and the brief said change no status); then
`bin/docket arm` and act on its answer. The six owner-facing decisions are
listed in `/mnt/project-files/v0.6.0/interface-areas-design-round.md`.

## Answers 2026-09-27

**Q1, Q2, Q3, Q5 and Q6: ratified** (project owner, 2026-09-27, ratified,
over the alternative each names).

**Q4: specified otherwise** (project owner, 2026-09-27): "Want a save button
(in drop down menu). Like Blender. Want to purposefully save a new default."
Two readings of "like Blender" exist and the owner was asked on 2026-09-27
which one they mean; until they answer, the design below records the first:
**A**, Blender's startup file, where reopening loads the saved default and
changes not saved as default are gone at quit; or **B**, reopening restores
the last state automatically *and* "Save as default" remains a deliberate
action with "Reset to my default" beside "Reset to shipped".
**Recommendation: B**, because a layout lost at quit is the stale-state
hazard the display standard names and B still gives the purposeful default
the owner asked for; its cost is one more stored section and one more menu
entry. Under B, `PL-SSQW` Q3, Q4 and Q6 gain an automatic atomic write of
the last-state section beside the explicit save of the default.

Blender's own model, which its source confirms
(`source/blender/windowmanager/intern/wm_files.cc`, blender/blender `main`,
read 2026-09-27): `WM_OT_save_homefile`, "Save Startup File - Make the
current file the default startup file", writes the startup file into the user
configuration directory after an "Overwrite Startup File" confirmation, and
`WM_OT_read_factory_settings`, "Load Factory Settings", restores the shipped
one, also after confirmation.

The design that follows:

- Changes to Workspaces during a session are the session's. Nothing writes
  `workspaces.json` on a change.
- **"Save as default"**, an entry in the layout drop-down menu (`PL-M352`
  owns the menu), writes the whole current `WorkspaceSet` - every Workspace,
  their order and the active one - to `workspaces.json` through `PL-SSQW`'s
  atomic replace, after a confirmation naming what it overwrites, and keeps
  the previous default as `workspaces.json.previous`.
- The next launch loads that file; the shipped set loads only when no file
  exists. Q3's reset actions are the "Load Factory Settings" side and keep
  their confirmation.
- No dirty marker and no prompt at quit, as in Blender, where the startup
  file drifts from the session silently: a layout not saved as default is
  gone at quit, which is the behaviour the analogy chooses. A quiet indicator
  that the current layout differs from the saved default was considered;
  recommendation: none, until a learner asks for one.
- Elsewhere: `PL-SSQW` Q3, Q4 and Q6 are reworded to match (no debounce,
  nothing written before the first save, a failed save reported at the
  action), and a newer-version file's "read-only session" means the Save
  action is disabled with the reason shown beside it.
