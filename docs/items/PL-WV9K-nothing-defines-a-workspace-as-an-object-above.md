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
