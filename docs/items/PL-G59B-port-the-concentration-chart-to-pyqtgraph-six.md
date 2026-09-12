---
id: PL-G59B
title: Port the concentration chart to pyqtgraph: six traces, both clinical references, both axes, the control marks and the wash-in plot
priority: P2
effort: L
status: ready
classes: feature, ux
feature: qt-port
touches: src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/wash_in.py, src/anesthesia_sim/app/simulation_view.py, tests/integration
added: 2026-09-10
verify: uv run python tools/import_boundary_check.py && grep -rq 'pyqtgraph' src/anesthesia_sim/app/
---

**Problem.** Port the concentration chart to pyqtgraph: six traces, both clinical references, both axes, the control marks and the wash-in plot

**`v0.5.1`'s Required scope, item 1.** The spike (`spikes/qt/`, `PL-55DH`)
is the working reference for the traces, both axes and both clinical
references - it draws them from `controller.drawn_window` with the real
`SimulationController` and no adaptation. What it deliberately does **not**
have and this item owes: the control marks (`PL-DR1Z`'s vertical
input-timeline series) and the wash-in plot.

**`PL-GS3R` lands here rather than separately.** Its chord-width column rule -
columns as a function of the selected span, with
`CHART_COLUMN_BUDGET_PER_SERIES` becoming a floor - is what this milestone
makes affordable, and it is why that item is `blocked-by: v0.5.1`. Measured:
49.4 ms of a 200 ms budget at 3 204 points on Qt, against about 78 ms for
Flet's diff alone.

**Presentation correctness is not optional for being a port.** The MAC axis,
the MAC-awake band and the 1 MAC line are clinically meaningful marks and must
stay traceable to the snapshot's own divisor, exactly as `_refresh_view` does
today - the spike's `_apply_agent_scale` is the worked example.

**Why it matters.** The chart is where this simulator does its teaching, and it
is the part of the port with the most clinically meaningful marks on it: the MAC
axis, the MAC-awake band and the 1 MAC line are all values a reader interprets
against. Presentation correctness is not relaxed for being a port - each must
stay traceable to the snapshot's own divisor exactly as `_refresh_view` does
today, and the spike's `_apply_agent_scale` is the worked example.

The six compartment colours carry a second constraint the port must not lose:
the four simulated colour-vision models put pairs of them as close as 1.08, far
under the 3:1 that would make colour sufficient, so the dash pattern is the
separating channel rather than decoration.

**Done when.** Six traces, both clinical references, both axes, the control
marks (`PL-DR1Z`'s vertical input-timeline series) and the wash-in plot all
render under pyqtgraph from `controller.drawn_window`; the MAC marks resolve
against the snapshot's own divisor; the dash patterns survive; and
`tools/contrast_check.py` passes against the new theme.
