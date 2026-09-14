---
id: PL-9KDK
title: tools/import_boundary_check.py confines no UI toolkit and no numpy, so nothing stops PySide6, pyqtgraph or numpy landing in core/ during the port, and ROADMAP.md credits it with a Flet count it does not check
priority: P2
effort: S
status: done
classes: defect, infra
feature: qt-port
touches: tools/import_boundary_check.py, tests/unit/test_import_boundary_check.py, docs/ARCHITECTURE.md, ROADMAP.md
added: 2026-09-14
closed: 2026-09-14
verify: uv run python tools/import_boundary_check.py && grep -q 'package="flet"' tools/import_boundary_check.py
---

**Problem.** tools/import_boundary_check.py confines no UI toolkit and no numpy, so nothing stops PySide6, pyqtgraph or numpy landing in core/ during the port, and ROADMAP.md credits it with a Flet count it does not check

**Found 2026-09-14** by the pre-port survey. `BOUNDARIES` in
`tools/import_boundary_check.py` declares seven entries - `pydantic`,
`subprocess`, `time`, `datetime`, `random`, `secrets`, `uuid` - and the word
`flet` appears nowhere in its output ("import boundaries: 7 declared, 34
modules read, 0 errors"). Yet `ROADMAP.md` § "the interface moves to Qt"
says "`tools/import_boundary_check.py` is why: exactly three modules import
Flet", and all six qt-port items lead their `verify:` with that command.

The count is *true* - `grep -rl "import flet" src/` gives `app/main.py`,
`app/simulation_view.py`, `app/chart_series.py` - but nothing enforces it,
and the one change about to introduce PySide6, pyqtgraph and numpy has no
boundary keeping any of the three out of `core/`. `CLAUDE.md`'s first
architecture rule is "keep scientific/simulation code independent of Flet";
the tool that should carry it does not.

**Done when** `BOUNDARIES` confines `PySide6`, `pyqtgraph` and `numpy` to
`src/anesthesia_sim/app` (and out of `core/`), confines `flet` to the three
modules above while it lasts, and the roadmap sentence cites a check that
exists. Lands with `PL-BXB2` and `PL-V53R`, the other two `tools/` re-pointings
the port needs first, so `tools/` is opened once.

**Why it matters.** `CLAUDE.md`'s first architecture rule is that simulation
code stays independent of the UI toolkit, and the port is the one change that
introduces three packages the rule has never been tested against. A boundary
declared before they arrive fails the first commit that lets one into `core/`;
one declared afterwards is written against whatever the port already did. The
roadmap sentence is the other half: a claim that reads as verified while
nothing verifies it is the exact shape this tool's own docstring names as the
reason it exists, and the count it credits the tool with is one the tool does
not make. Confining `flet` to its three modules also turns the tool's own
unused-allowance error into the port's checklist - each module the port frees
of Flet must drop its allowance in the same commit, and the last one takes the
boundary with it.

**Found by declaring it, 2026-09-14.** Flet is two distributions with two root
packages. `app/chart_series.py` imports `flet_charts` and not `flet`, so a
single `flet` boundary naming all three modules failed on its own
unused-allowance rule the first time it ran. The declaration is two
boundaries - `flet` in `main.py` and `simulation_view.py`, `flet_charts` in
`chart_series.py` and `simulation_view.py` - which between them name exactly
the three modules the roadmap counts, and a test pins that union. The other
three entries (`PySide6`, `pyqtgraph`, `numpy`) permit no module under
`core/`, the shape the clock boundaries already use, and are declared before
any of the three exists in the tree.
