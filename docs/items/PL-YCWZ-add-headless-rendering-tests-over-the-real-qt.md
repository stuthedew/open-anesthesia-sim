---
id: PL-YCWZ
title: Add headless rendering tests over the real Qt interface, which is what PL-2QMK has been waiting for
priority: P2
effort: M
status: ready
classes: test, infra
feature: qt-port
touches: tests/integration, src/anesthesia_sim/app/simulation_view.py
added: 2026-09-10
verify: uv run python tools/import_boundary_check.py && test -f tests/integration/test_qt_rendering.py
---

**Problem.** Add headless rendering tests over the real Qt interface, which is what PL-2QMK has been waiting for

**`v0.5.1`'s Required scope, item 6, and it closes `PL-2QMK`.**

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
