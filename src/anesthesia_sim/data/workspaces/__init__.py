"""This package holds the Workspaces shipped with the application, one JSON file each.

It contains no executable code. Each file is a Workspace set document that holds one
Workspace. It has the same form as a reader's own `workspaces.json`, so `layout/shipped.py`
reads it with the same function that `layout/store.py` uses (`PL-KXTL`). A file's stem
is the shipped Workspace's id, and the Workspace in it names that id as its
origin.

Every Workspace puts the concentration chart on the left at the window's full
height, and a column on its right whose first Area holds the parameter
controls. The row is split at the same shares in all three, so the controls
stay where they were when the reader switches tabs (project owner,
2026-11-26, `PL-YS8M`). On a wide screen the controls' Area is then the same
in every Workspace. On a 1366 by 768 laptop screen the column is as wide as
the widest View in it needs, so the Area keeps its top and right edges and is
wider in Induction and Maintenance. Each gives the Parameters View a small
share, so its Area stays at the View's least height at every window size and
the Views around it take the rest (`PL-4JCC`). The shares are placeholders.

With one run, Maintenance shows its lesson whole in a 1366 by 768 window, the
size its pixel budget was set for (`ROADMAP.md` v0.6.0 Required scope entry
20, `PL-84QX`, `PL-D5J4`). Induction's wash-in plot needs a 1440 by 900
window, and scrolls inside its Area on a smaller one. With a branch open, the
controls' Area holds a second row of controls, and neither lesson fits whole.

- `default.json` - the concentration chart, and a column that holds the
  parameter controls over the bookmarks and the branch control. At 1366 by
  768 the chart keeps every row above its plot on screen.
- `induction.json` - the concentration chart, and a column that holds the
  parameter controls over the wash-in chart and, under that, the bookmarks
  beside the branch control. The wash-in curve shows the alveolar
  concentration as a fraction of the circuit concentration. It changes fastest
  in the first minutes.
- `maintenance.json` - the concentration chart, and a column that holds the
  parameter controls over the compartment schematic. During maintenance, the
  agent moves into muscle and fat while the tensions in those tissues stay
  low. Each container's label gives its share of all the agent, with a bar
  under it, and that is where a learner sees it (`PL-PR1W`, `PL-8PL4`). The
  containers, their labels and their bars are the schematic's first row under
  its name line, and the line that says what the shares are of comes next.
  Both stay on screen at 1366 by 768, and the scale caption under them
  scrolls. While a container is above the scale, the line that names it comes
  first, and the share line can then scroll too. The schematic needs nearly all of the column's height
  on a laptop screen, so this Workspace leaves out the bookmarks and the
  branch control. A reader brings either back with the View chooser. The
  wash-in chart, whose lesson is the first minutes, stays in Induction. The
  choice of which Workspace holds the schematic is a placeholder.

None of the three contains the agent accounting View (project owner,
2026-09-16). `docs/INTERFACE.md` § "Values that must stay reachable" puts the
accounting in the tier of displays that a layout may leave out. A reader brings
it back with the View chooser (`PL-50PZ`).

**Provenance.** Shipping a set of named, task-oriented Workspaces beside the
reader's own is Blender's practice: Blender ships eleven default Workspaces,
each named for a task. `docs/interface-provenance.md` records the study of
them and what this project adopted. The idea is all that was taken. The three
arrangements are this project's own, composed for anesthesia teaching, and no
Blender layout or file is reproduced.
"""
