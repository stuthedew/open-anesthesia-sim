---
id: PL-9KDK
title: tools/import_boundary_check.py confines no UI toolkit and no numpy, so nothing stops PySide6, pyqtgraph or numpy landing in core/ during the port, and ROADMAP.md credits it with a Flet count it does not check
status: untriaged
added: 2026-09-14
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
