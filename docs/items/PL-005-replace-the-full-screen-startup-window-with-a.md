---
id: PL-005
title: Replace the full-screen startup window with a sized, centered one
priority: P2
effort: S
status: done
classes: ux
feature: vaporizer-controls
touches: src/anesthesia_sim/app/main.py, src/anesthesia_sim/app/qt_widgets.py, tests/integration/test_qt_widgets.py, tests/unit/test_bootstrap.py, docs/MODEL.md
added: 2026-08-23
closed: 2026-09-15
verify: uv run pytest tests/integration/test_qt_widgets.py tests/unit/test_bootstrap.py && grep -q 'def test_the_startup_window_is_sized_from_the_screen_and_centred' tests/integration/test_qt_widgets.py
---

> **This fix rides the Qt port, not Flet.** `ROADMAP.md` § "v0.4.26 -
> the interface moves to Qt" names this item under "Fixes this port carries":
> the defect lives in code that milestone rewrites from scratch, so fixing it
> on Flet means writing the same lines twice. Project owner, 2026-09-10.

**Problem.** `app/main.py` sets `page.window.full_screen = True` on
startup.
**Why it matters.** Full-screen-on-launch is a hostile default and hides
the window controls on some platforms. Prior project decision is to replace
it.
**Where.** `app/main.py`.
**First step.** Choose the sizing approach. Constraints from the prior
decision: no magic pixel dimensions, no monitor-specific assumptions, and
no native display-probing dependency.
**Done when.** The app opens in an adequately sized, centered window that
remains fully visible on different displays.

**Closed 2026-09-15, with `PL-25KS`.** `main.py` opens the window at
`qt_widgets.initial_window_geometry(screen.availableGeometry(),
window.minimumSizeHint(), WINDOW_SCREEN_FRACTION)`: eight tenths of the
screen's available area on each axis, never below the window's own minimum,
centred - no pixel literal, no monitor assumption, and no display-probing
dependency beyond the toolkit's own screen object. Held by
`test_the_startup_window_is_sized_from_the_screen_and_centred` (the
geometry cases, including a minimum larger than the fraction) and the
launcher test in `tests/unit/test_bootstrap.py`, which builds the real
window and reads its geometry back.
