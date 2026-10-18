"""The Workspaces shipped with the application, one JSON file each. No executable code.

Each file is a Workspace set document holding one Workspace, in the form a
reader's own `workspaces.json` takes, so `layout/shipped.py` reads it with the
same reader `layout/store.py` uses (`PL-KXTL`). A file's stem is the shipped
Workspace's id, and the Workspace in it names that id as its origin.

- `default.json` - the concentration chart across the left three quarters of
  the window at full height, with the parameter controls in a column on the
  right. This is the composition the pixel budget was set for: on a 1366 by
  768 display the chart keeps its 360 px minimum with the parameter controls
  visible (`ROADMAP.md` v0.6.0 Required scope entry 20, `PL-84QX`).
- `induction.json` - the concentration chart over the wash-in chart, with
  the parameter controls on the right. The wash-in curve, alveolar as a
  fraction of the circuit, changes fastest in the first minutes.
- `maintenance.json` - the big picture: the concentration chart across the
  whole width, with the wash-in chart and the parameter controls side by
  side below it.

None of the three holds the agent accounting View (project owner,
2026-09-16): `docs/MODEL.md` puts the accounting in the tier a layout may
leave out, and the View chooser (`PL-50PZ`) is how a reader brings it back.

**Provenance.** Shipping a set of named, task-oriented Workspaces beside the
reader's own is Blender's practice: Blender ships eleven default Workspaces,
each named for a task. `docs/interface-provenance.md` records the study of
them and what this project adopted. The idea is all that was taken. The three
arrangements are this project's own, composed for anesthesia teaching, and no
Blender layout or file is reproduced.
"""
