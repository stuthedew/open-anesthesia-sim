---
id: PL-3355
title: The 'Simulated time' and compartment readouts wrap their value onto a second line at some window widths
priority: P2
effort: S
status: ready
classes: defect, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py
added: 2026-09-04
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_no_metric_value_wraps_away_from_its_unit' tests/unit/test_simulation_view.py
---

**Problem.** The 'Simulated time' and compartment readouts wrap their value
onto a second line at some window widths

**Observed 2026-09-04, in a rendered frame at 1700 CSS pixels**, while landing
`PL-ZRSP` (the F_A/F_I trace). The clock read `85.3` on one line and `s` on the
next, and the alveolar readout `0.13` over `%`, in the seven-column layout
`METRIC_GRID_COLUMNS` selects at that width. A second frame at the same width
did not reproduce it, so it is width-dependent *and* something else - a
transient during layout, or the value's own width crossing a threshold.

**Why it matters.** A unit separated from its number is the presentation
failure `CLAUDE.md` names directly: a reader glancing at a wrapped `0.13` with
the `%` on the line below has a number with no unit attached to it, beside six
other panels that do. `PL-8M05` set the breakpoints from the widest label a
panel must hold on one line; this is the same measurement made against the
*value* rather than the name.

**Where to start.** `_build_concentration_metrics` and `METRIC_GRID_COLUMNS` in
`app/simulation_view.py` carry the existing measurement and its reasoning.
Reproducing it needs a rendered frame rather than a unit test - the screenshot
was taken by driving the app under Chromium with the CanvasKit assets rerouted
to `flet_web`'s local copies, since this container cannot reach gstatic.com.

**Done when.** No metric panel can separate a value from its unit at any window
width the layout selects, and what holds it there is a measurement against the
widest *value* a panel must show - the same measurement `PL-8M05` made against
the widest label - rather than against a frame somebody happened to render.
