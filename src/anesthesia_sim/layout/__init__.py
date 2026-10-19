"""The area layout: which View occupies which part of each window, held as a value.

`ROADMAP.md` item 34 takes Blender's window system as the model for this
interface, and `PL-C842` put the layout's source of truth here, in plain
Python, rather than in the widgets that draw it. Nothing in this package
imports a toolkit - `tools/import_boundary_check.py` refuses `PySide6` and
`pyqtgraph` under it - so every operation and every refusal is tested without
a `QApplication`, and one adapter module builds the widget tree from the value
(`PL-W9P6`).

- `tree.py` - the values a layout is built from: `AreaId`, `ViewKind`,
  `Area`, `Split` and `Window`, each refusing as it is built what could not
  be one, and the one form a tree takes.
- `model.py` - `LayoutModel`: every window's tree, the operations a reader
  performs on it, and the `borders()` query a drag reads.
- `serialization.py` - the layout as JSON: the body a Workspace holds, and a
  versioned document holding one on its own.
- `exceptions.py` - what the package refuses, and what each refusal means to
  a caller.
- `run_identity.py` - `RunId`, what a run is called by independently of
  where it is drawn, which a Workspace pins (`PL-7Z84`).
- `shipped.py` - the Workspaces shipped under `data/workspaces/`, read by the
  same reader as the reader's own file (`PL-KXTL`).
"""
