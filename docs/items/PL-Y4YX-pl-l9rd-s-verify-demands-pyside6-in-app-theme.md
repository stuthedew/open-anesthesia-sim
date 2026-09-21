---
id: PL-Y4YX
title: PL-L9RD's verify: demands PySide6 in app/theme.py, which that file's own documented invariant forbids, and the invariant's stated reason does not hold either - both tools ast.parse it and neither imports it
priority: P3
effort: S
status: needs-decision
classes: defect
feature: qt-port
touches: src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/qt_chart.py
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

## Promoted to `needs-decision` 2026-09-16, and narrowed to the half that is left

`PL-L9RD` closed and did **not** resolve this, which its own ground in
`ROADMAP.md` had assumed it would. What that item fixed was the *symptom*: its
`verify:` no longer requires PySide6 in `app/theme.py`, and the file's comment
no longer defends itself with the claim that the two tools need it to import
nothing - they call `ast.parse`, which executes nothing, so that reason was
checkably false and is replaced with one that holds.

**Decision needed.** Whether `app/theme.py` keeps its no-toolkit rule, or
becomes the place the Qt styling layer is composed.

The case for moving it: 27 `setStyleSheet` sites across `app/qt_chart.py`,
`app/qt_widgets.py`, `app/run_view.py` and `app/simulation_view.py` each build a
CSS string from this file's constants, and the partial helpers that already
exist (`_panel_stylesheet`, `_slider_stylesheet`, `selector_stylesheet`,
`_surface_stylesheet`, `_text_stylesheet`) live in the view modules rather than
beside the values they use. "Make the visual decisions once" wants one place.

The case for keeping it: this file is where a value a clinician could be misled
by is written down, and it is worth being importable and testable without a
display, an event loop or a plugin. A stylesheet composer needs none of Qt's
types either - it returns strings - so the two may not actually be in tension,
which is the thing to establish before choosing.

**Recommendation: keep the no-toolkit rule, and move the composers rather than
the toolkit.** A function returning `f"QPushButton {{ color: {INK}; }}"` imports
nothing, so the 27 sites can be centralised here without a PySide6 import at
all. That gets the single place without giving up the property worth having.
What needs checking before committing to it is whether any of the five existing
helpers genuinely needs a Qt type - if one does, it stays in its view module
and the rule holds for the rest.

**Done when.** The question is answered in `app/theme.py`'s own comment, and
either the composers have moved with the tests to match, or the item records why
they stay where they are. `PL-NGF7`'s
`check_disabled_states_are_the_style_s` is unaffected either way: it refuses a
`:disabled` rule wherever the string is composed.

**Re-pointed by `PL-6TP8`, 2026-09-19.** The half of this item that belonged
to the `verify:` cluster - a command satisfiable by a comment containing a
string, demanding what the file forbids - closed with `PL-L9RD`, whose command
was re-pointed at close. What remains, whether `app/theme.py` keeps its
no-toolkit rule, is the project owner's decision and outside `PL-6TP8`; the
recommendation above stands.

## Narrowed by PL-C4W8's Gate 2 staleness sweep, 2026-09-21

**The contradiction this item is named for is gone.** `PL-L9RD` closed with
`verify: python3 tools/doc_check.py check && grep -qF 'that absorption was
reversed on 2026-09-16' ROADMAP.md`, which demands nothing of `app/theme.py`;
and `app/theme.py` itself now states the corrected reason for its no-toolkit
rule, recording in place that the old `ast.parse` justification was false.
Commit `d56f857f` (#621) made both changes together. So "two current
statements in conflict" is no longer the finding.

**What is still open, and why the item stays open.** The narrower question the
contradiction pointed at is unresolved in the tree: whether `app/theme.py`
keeps its no-toolkit rule, or the stylesheet-composing helpers centralise into
it. They are still spread across `qt_widgets.py`, `run_view.py`, `qt_chart.py`
and `simulation_view.py`. The item stays `needs-decision` on that question
alone.
