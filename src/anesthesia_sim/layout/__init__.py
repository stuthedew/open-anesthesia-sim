"""The area layout is a value that records which View occupies which part of each window.

`ROADMAP.md` item 34 takes Blender's window system as the model for this
interface. `PL-C842` put the layout's source of truth here, in plain Python,
rather than in the widgets that draw it. Nothing in this package imports a
toolkit, and `tools/import_boundary_check.py` rejects any import of `PySide6`
or `pyqtgraph` here. So every operation, and every refusal of one, is tested
without a `QApplication`. One adapter module builds the widget tree from the
layout value (`PL-W9P6`).

- `tree.py` defines the values a layout is built from: `AreaId`, `ViewKind`,
  `Area`, `Split` and `Window`. Each one rejects, as it is built, a value
  that could not be valid. The module also defines the rule that gives each
  tree a single form: no split has a child split of its own orientation.
- `model.py` defines `LayoutModel`, which holds every window's tree. It also
  defines the operations a reader performs on the layout, and the
  `borders()` query that a drag uses.
- `serialization.py` writes and reads the layout as JSON. It handles both the
  layout inside a saved Workspace and a versioned document that contains a
  layout on its own.
- `exceptions.py` defines the exceptions the package raises, and what each
  one means to a caller.
- `run_identity.py` defines `RunId`, which names a run independently of
  where the run is drawn. A Workspace pins a run by this id (`PL-7Z84`).
- `shipped.py` reads the Workspaces shipped under `data/workspaces/`. It uses
  the same function that reads the reader's own saved file (`PL-KXTL`).
"""
