---
id: PL-G59B
title: Port the concentration chart to pyqtgraph: six traces, both clinical references, both axes, the control marks and the wash-in plot
status: untriaged
feature: qt-port
added: 2026-09-10
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
