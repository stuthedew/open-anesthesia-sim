"""This package holds the Workspaces shipped with the application, one JSON file each.

It contains no executable code. Each file is a Workspace set document that holds one
Workspace. It has the same form as a reader's own `workspaces.json`, so `layout/shipped.py`
reads it with the same function that `layout/store.py` uses (`PL-KXTL`). A file's stem
is the shipped Workspace's id, and the Workspace in it names that id as its
origin.

Each Workspace shows its own lesson whole in a 1366 by 768 window, the size its
pixel budget was set for (`ROADMAP.md` v0.6.0 Required scope entry 20,
`PL-84QX`, `PL-D5J4`). Each gives the Parameters View a small share, so its
Area stays at the View's least height at every window size and the Views around
it take the rest (`PL-4JCC`). The shares are placeholders.

- `default.json` - the concentration chart at the window's full height, with
  a column on the right that holds the parameter controls over the bookmarks
  and the branch control. At 1366 by 768 the chart keeps every row above its
  plot on screen.
- `induction.json` - the concentration chart over the parameter controls on
  the left half, and the wash-in chart over the bookmarks and the branch
  control on the right half. The wash-in curve shows the alveolar
  concentration as a fraction of the circuit concentration. It changes fastest
  in the first minutes.
- `maintenance.json` - the concentration chart over the parameter controls on
  the left half, and the compartment schematic over the branch control on the
  right half. During maintenance, the agent moves into muscle and fat while the
  tensions in those tissues stay low. The schematic's share bar is where a
  learner sees that (`PL-PR1W`). The schematic needs most of a 768 px window's
  height to show its share bar, so this Workspace leaves out the bookmarks. A
  reader brings them back with the View chooser. The wash-in chart, whose
  lesson is the first minutes, stays in Induction. The choice of which
  Workspace holds the schematic is a placeholder.

None of the three contains the agent accounting View (project owner,
2026-09-16). `docs/MODEL.md` puts the accounting in the tier of displays that a
layout may leave out. A reader brings it back with the View chooser (`PL-50PZ`).

**Provenance.** Shipping a set of named, task-oriented Workspaces beside the
reader's own is Blender's practice: Blender ships eleven default Workspaces,
each named for a task. `docs/interface-provenance.md` records the study of
them and what this project adopted. The idea is all that was taken. The three
arrangements are this project's own, composed for anesthesia teaching, and no
Blender layout or file is reproduced.
"""
