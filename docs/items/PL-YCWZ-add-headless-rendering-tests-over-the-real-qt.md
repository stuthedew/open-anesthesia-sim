---
id: PL-YCWZ
title: Add headless rendering tests over the real Qt interface, which is what PL-2QMK has been waiting for
priority: P2
effort: M
status: done
classes: test, infra
feature: qt-port
touches: tests/integration, tests/conftest.py, src/anesthesia_sim/app/simulation_view.py, docs/ARCHITECTURE.md, docs/worker.md
added: 2026-09-10
closed: 2026-09-15
pr: 588
verify: uv run python tools/import_boundary_check.py && test -f tests/integration/test_qt_rendering.py
---

**Problem.** Add headless rendering tests over the real Qt interface, which is what PL-2QMK has been waiting for

**The Qt port's Required scope, item 6, and it closes `PL-2QMK`.**

`PL-2QMK` records that no session in the web container can visually confirm a
chart change, because Flet's web renderer fetches Flutter assets the egress
proxy denies. That is what blocks `PL-90Y6`, `PL-3355`, `PL-W8DQ`, `PL-GVXP`
and the rest of `presentation-safety`.

**The capability is already demonstrated rather than assumed.**
`spikes/qt/qt_spike.py --screenshot` writes a PNG of the running interface in
that very container, with a dial change drawn in it, under
`QT_QPA_PLATFORM=offscreen`. This item is what turns that from a flag into
tests: assertions over the real interface at a fixed size, so a presentation
change can be reviewed by a session rather than only by the project owner.

**What such a test may assert is the design question.** A pixel-exact snapshot
is brittle across Qt versions and font stacks; what is worth asserting is
nearer to "the alveolar trace is drawn", "the MAC-awake band sits between these
two axis values", "no trace leaves the plot". Decide that before writing many.

**Why it matters.** It unblocks a whole feature. `PL-2QMK` records that no
session in the web container can visually confirm a chart change, because Flet's
web renderer fetches Flutter assets the egress proxy denies - which is what
blocks `PL-90Y6`, `PL-3355`, `PL-W8DQ`, `PL-GVXP` and the rest of
`presentation-safety`. Under `QT_QPA_PLATFORM=offscreen` the capability is
already demonstrated rather than assumed: `spikes/qt/qt_spike.py --screenshot`
writes a PNG of the running interface in that very container, with a dial change
drawn in it.

Until it exists, every presentation change is reviewable only by the project
owner running the app, which is the single largest serialization point in this
project's workflow.

**Done when.** Tests render the real Qt interface headless at a fixed size and
assert over it, `PL-2QMK` is closed, and the assertions are chosen for
durability rather than pixel-exactness - "the alveolar trace is drawn", "the
MAC-awake band sits between these two axis values", "no trace leaves the plot" -
since a pixel snapshot is brittle across Qt versions and font stacks.

**Rider, 2026-09-14 (pre-port survey).** Two things nothing sets, both measured
in this container. (1) `QT_QPA_PLATFORM`: unset, Qt defaults to `xcb` and
`QApplication([])` aborts with `Could not load the Qt platform plugin "xcb"`,
listing `offscreen` among the available plugins. The carrier is a new
`tests/conftest.py` with `os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")`
before any PySide6 import - not a prefix on the pytest line in `Makefile` or
`.github/workflows/quality.yml`, which `tools/doc_check.py`'s
`check_coverage_gate` holds to string equality. Add `tests/conftest.py` to this
item's `touches:`. (2) `libegl1`: `PL-VHLZ` carries the CI step and the
environment line; this item's first rendering test cannot pass in CI until
that lands, because `import PySide6.QtGui` dies before collection.

**Started by `PL-G59B`, 2026-09-14.** `tests/conftest.py` carries the
`QT_QPA_PLATFORM` line this rider asked for, `quality.yml` installs `libegl1`
(`PL-VHLZ`'s CI half), and `tests/integration/test_qt_chart.py` renders the
chart headless and reads pixels back -
`test_the_references_and_the_ruling_are_painted_and_the_ruling_sits_underneath`
is the first assertion of the durable kind this brief asks for, and it caught
a real defect (pyqtgraph's grid painting over the 1 MAC line). What is left
is the dashboard-level rendering: the real interface at a fixed size, once
`PL-25KS` has one.

**Closed 2026-09-15, with `PL-25KS`.** `tests/integration/test_qt_rendering.py`
renders the real dashboard headless at 1600x1000 over a real run advanced
past a control change, and asserts what is durable rather than pixel-exact:
the grab is the requested size and not blank, a screenshot can be written,
the agent badge is painted in the agent's own fill, the 1 MAC line is
painted along the row the axis places it on, the alveolar trace lies inside
the plot, no readout value is clipped by its panel, the readout row and the
sidebar lie inside the page, and the hover reports the drawn state through
the formatters. `docs/worker.md` says how a session writes the screenshot.
`PL-2QMK` closes on it.
