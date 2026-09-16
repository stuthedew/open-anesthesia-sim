---
id: PL-Y4YX
title: PL-L9RD's verify: demands PySide6 in app/theme.py, which that file's own documented invariant forbids, and the invariant's stated reason does not hold either - both tools ast.parse it and neither imports it
status: untriaged
added: 2026-09-16
---

**Problem.** PL-L9RD's verify: demands PySide6 in app/theme.py, which that file's own documented invariant forbids, and the invariant's stated reason does not hold either - both tools ast.parse it and neither imports it

**Found 2026-09-16 while starting `PL-L9RD`** (re-express `app/theme.py` for Qt
and make the interface pass's visual decisions once). Not fixed here, because
which way it resolves is the project owner's call rather than a repair.

**The two statements, both current.** `PL-L9RD`'s `verify:` is:

```text
uv run python tools/import_boundary_check.py && grep -q 'PySide6' src/anesthesia_sim/app/theme.py
```

and `src/anesthesia_sim/app/theme.py` says, in a comment written for the
reader of any future display token:

> **This module stays free of any toolkit.** `tools/contrast_check.py` and
> `tools/agent_identity_check.py` read this file with `ast` in a bare checkout
> precisely because it imports nothing they would need installed, so a display
> constant that needs a toolkit type belongs in the module that draws it.

So the command that proves the item done requires the file to name PySide6,
and the file requires itself not to. One of the two has to give.

**The invariant's stated reason does not hold, which is what makes this a
decision rather than an obvious repair.** Both tools parse rather than import:
`tools/contrast_check.py:862`, `:906`, `:945` and
`tools/agent_identity_check.py:261` all call
`ast.parse(path.read_text(...))`. `ast.parse` executes nothing and resolves no
import, so a `from PySide6.QtGui import QColor` at the top of `theme.py` would
leave both tools working in a bare checkout exactly as they do now. The
*conclusion* may still be right - a toolkit-free token module is testable and
importable without Qt, which is worth something on its own - but the reason
written beside it is not the one carrying it, and a later session will read
that reason and act on it.

`tools/import_boundary_check.py` does not settle it either way: its toolkit
boundary confines `PySide6`, `pyqtgraph` and `numpy` out of `core/` only, and
`theme.py` is under `app/`, where the docstring says "a widget legitimately
belongs". So the first half of the `verify:` passes whichever way this goes.

**Why it matters.** Three ways, in order of cost.

1. **`PL-L9RD` cannot be closed honestly as written.** Its `verify:` is
   satisfiable by adding a comment containing the string `PySide6`, which
   proves nothing, or by an import the file forbids. The paired shape the
   `docket` skill asks for - a half that proves the tree healthy and a half
   that names what the work adds - is not what this command is.
2. **The invariant is load-bearing for a reason nobody has written down.**
   Whatever is decided, the comment should say the reason that actually holds.
   A rule defended by a reason a session can check and find false is a rule
   that gets broken by the session that checks it.
3. **It is the seam the visual pass runs through.** There are 27
   `setStyleSheet` call sites across `app/qt_chart.py`, `app/qt_widgets.py`,
   `app/run_view.py` and `app/simulation_view.py`, each composing a CSS string
   from `theme.py`'s hex constants, with partial helpers (`_panel_stylesheet`,
   `_slider_stylesheet`, `selector_stylesheet`, `_surface_stylesheet`,
   `_text_stylesheet`) living in the view modules rather than in the theme.
   "Make the visual decisions once" and "keep the theme toolkit-free" pull in
   opposite directions across exactly that seam.

**Done when.** `app/theme.py`'s invariant comment and `PL-L9RD`'s `verify:`
agree, the comment states a reason that is true of the tree, and - if the
toolkit-free rule is kept - `PL-L9RD`'s `verify:` names something that is
actually a specification of the work rather than the presence of a string.
