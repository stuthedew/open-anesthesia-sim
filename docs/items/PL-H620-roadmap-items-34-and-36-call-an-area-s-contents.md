---
id: PL-H620
title: ROADMAP items 34 and 36 call an area's contents a view or a widget, but the project owner named Blender's own vocabulary - Workspace, Area, Editor - as the concept to implement, and the manual's Areas and Workspaces pages are now available at source
priority: P3
effort: S
status: done
classes: planning, docs
touches: ROADMAP.md
added: 2026-09-16
closed: 2026-09-16
verify: python3 tools/doc_check.py check && grep -qF 'The vocabulary is Blender' ROADMAP.md
---

**Problem.** ROADMAP items 34 and 36 call an area's contents a view or a widget, but the project owner named Blender's own vocabulary - Workspace, Area, Editor - as the concept to implement, and the manual's Areas and Workspaces pages are now available at source

**What the owner said, and why it is a vocabulary decision rather than a
preference.** "The workspace/area concept (areas I previously referred to as a
widget) is what I want to implement." Item 34 had been written in the project's
own improvised terms - *views*, *widgets*, *panels* - against a concept that
already has three precise ones. Keeping two vocabularies for one mechanism is
how a later session scopes the wrong thing: a "widget catalogue" sounds like
chrome, and an *editor* catalogue is what item 36 actually is.

**The three terms, read at the source.** The manual's § "Areas" and
§ "Workspaces" pages were supplied directly by the owner on 2026-09-16, this
environment's egress proxy blocking `docs.blender.org`:

| Term | The manual's definition |
| --- | --- |
| Area | A rectangle that reserves screen space for an editor. Areas do not overlap. |
| Editor | What occupies an area - "each editor offers a specific piece of functionality". |
| Workspace | "A set of Areas containing Editors", geared to a task, switched as tabs in the Topbar. |

**What the source added beyond the vocabulary**, now recorded in item 34:

- **Docking** is the manual's own word for the corner-drag family, and it is
  wider than split-and-join: join, split, split-and-join in one drag, and
  *replace* a second area by dragging into its middle. Areas also swap -
  adjacent through the border's Area Options, any two in a window through
  Ctrl-LMB from a corner.
- **Blender refuses to delete the last workspace.** A floor enforced
  structurally rather than by warning, which is the shape `PL-WLWY` settled on
  for the minimum display, arriving from the same source that inspired the
  layout.
- **A workspace carries settings, not only a layout** - Pin Scene makes
  activating a workspace switch back to the scene it remembers. The analogue
  here is a workspace pinning which *run* it shows, which is what `PL-WLWY`'s
  requirement that a broken-out window name its run needs a mechanism for.

**Done when.** Items 34 and 36 use Area, Editor and Workspace as the manual
defines them, *widget* and *view* are retired from both, and the source is
cited as read rather than inferred. Closed 2026-09-16 with the edit.
