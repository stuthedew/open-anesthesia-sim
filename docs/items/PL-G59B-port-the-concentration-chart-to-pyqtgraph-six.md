---
id: PL-G59B
title: Port the concentration chart to pyqtgraph: six traces, both clinical references, both axes, the control marks and the wash-in plot
priority: P1
effort: L
status: done
closed: 2026-09-14
classes: feature, ux
feature: qt-port
touches: src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/simulation_view.py, tests/unit/test_chart_frame.py, tests/integration/test_qt_chart.py, tests/conftest.py, pyproject.toml, uv.lock, .github/workflows/quality.yml, docs/ARCHITECTURE.md, docs/MODEL.md
added: 2026-09-10
verify: uv run python tools/import_boundary_check.py && grep -rq 'pyqtgraph' src/anesthesia_sim/app/
---

**Problem.** Port the concentration chart to pyqtgraph: six traces, both clinical references, both axes, the control marks and the wash-in plot

**The Qt port's Required scope, item 1.** The spike (`spikes/qt/`, `PL-55DH`)
is the working reference for the traces, both axes and both clinical
references - it draws them from `controller.drawn_window` with the real
`SimulationController` and no adaptation. What it deliberately does **not**
have and this item owes: the control marks (`PL-DR1Z`'s vertical
input-timeline series) and the wash-in plot.

**`PL-GS3R` lands here rather than separately.** Its chord-width column rule -
columns as a function of the selected span, with
`CHART_COLUMN_BUDGET_PER_SERIES` becoming a floor - is what this milestone
makes affordable, and it is why that item is blocked on this one. Measured:
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

## Raised to P1 on 2026-09-14

Not on its own merits - it is `feature`/`ux` classed and nothing it draws is
newly wrong. It is raised because the Qt port moved ahead of v0.5.0
(`PL-RKWB`), and re-pointing the items that waited on the port from
`blocked-by: <the port's version>` to the port item that does their work put two `P1`
`safety`-classed items directly behind this one:

- `PL-GS3R` - 0.26 MAC of departure between the drawn trace and the run at the
  12 h base, worst in the steep early wash-in. Its fix is the chord-width
  column rule, which this port is what makes affordable.
- `PL-YVHK` - the chart hover readout, which `ScatterPlotItem` loses by default
  (`hoverable` is `False`), so a port silent about it removes an affordance the
  Flet build has.

`bin/docket check` refuses a `P1` waiting on a `P2` for exactly this reason:
nothing behind this item can start before it does, so the band it ranks in has
to be the band of the most urgent thing it gates. This is the safety debt of
the chart arriving at the item that unblocks it, rather than a re-banding of
the port's own risk.

**Rider, 2026-09-14 (pre-port survey).** Two sequencing facts no field carries.
`src/anesthesia_sim/app/wash_in.py` was in this item's `touches` and is
removed: § "Explicitly out of scope" names it among the modules that survive
untouched, and the wash-in *plot* is drawn by `chart_series.py` and
`simulation_view.py`, which are already listed. And PySide6, pyqtgraph and
numpy are neither installed nor declared (`ModuleNotFoundError: No module
named 'PySide6'` on a bare checkout), so this item cannot import pyqtgraph
until `PL-3SQT`'s *additive* half lands - the dependencies in, Flet left in
place for `PL-7SVX`. Start there, in this item's own first commit if `PL-3SQT`
has not been started.

**Closed 2026-09-14.** Six traces, both clinical references, both axes, the
control marks and the wash-in plot render under pyqtgraph from
`controller.drawn_window`, in two modules rather than one:

- `app/chart_frame.py` - what one frame *claims*, with no toolkit loaded: the
  six-trace table (`COMPARTMENT_TRACES`, from which the Flet dashboard's own
  `_traces` is now built, so there is one copy), the window and its ticks,
  the percent axis labelled at exactly its gridlines (`PL-Q4VH`), the MAC
  ticks, both references from the snapshot's own divisor, the most-recent
  marks that fit and the count that did not, the wash-in stretches formed
  from the very columns the compartment chart draws, and the hover text.
  `tests/unit/test_chart_frame.py` holds it, 28 tests, no display.
- `app/qt_chart.py` - `ConcentrationChart`, `WashInChart` and `TraceLegend`,
  which move pyqtgraph items to match a `ChartFrame` and decide nothing.
  `tests/integration/test_qt_chart.py` draws them headless against a real
  run, 16 tests, reading the items and the painted pixels back.

**Four decisions the port had to make, recorded here.** (1) pyqtgraph's own
grid is not used: it is painted by the axis item *over* the plot, and at full
opacity the 2% gridline erased the 1 MAC line standing on it - measured in
rendered pixels, and `test_the_references_and_the_ruling_are_painted_and_the_ruling_sits_underneath`
holds the fix, which rules the plot from underneath at the ticks the axes
carry. (2) The hover's instant is stated at the step the run advances by
(`HOVER_INSTANT_RESOLUTION_S`): a drawn column sits at 410.7383 s and the
state is exact there, but four decimals would claim a resolution no other
display has. (3) The wash-in hover's parenthesis uses a solidus, not the
division sign `docs/MODEL.md` showed, because `tools/glyph_check.py` refuses
a character nobody has rendered; the document's example is corrected to
match. (4) Qt states a dash pattern in pen widths and the table states it in
pixels, so `dashed_pen` converts once - the spike had copied the numbers
across and drew every dash three times too long.

**What this leaves to the items behind it.** `PL-GS3R`: `chart_columns` is
the one function the chord-width rule replaces, and it answers the floor at
every rung until that item chooses the target width and re-measures the
departure at every rung - the measurement is that item's, not a port's.
`PL-YVHK`: the hover is built to the derivation, with the headless test that
item asks for; the `README.md` line waits until the Qt chart is the shipped
chart, with `PL-25KS`. `PL-Q4VH` and `PL-THXF`: fixed by construction in the
Qt chart and held by `test_both_axes_are_labelled_where_they_are_ruled` and
`test_the_legend_swatch_carries_the_trace_s_own_dash_pattern`; they close
when the Flet chart that still has the defects goes, with `PL-7SVX`.
`PL-YCWZ`: `tests/conftest.py` and the first pixel-reading test landed here;
the dashboard-level rendering tests are still that item's. `PL-25KS`: the
dashboard assembles a `ChartFrame` per render tick from its runs' snapshots
and their `AdjustmentGrouping`, calls `draw` on both charts, and connects
`TraceLegend.visibility_changed` to a redraw; the captions the Flet chart
panel carries (time-axis caption, the two reference lines, the wash-in state
sentence, the off-scale notice) are that item's, and `ChartFrame.fitted`,
`RunFrame.undrawn_control_marks` and `RunFrame.undrawn_wash_in_stretches`
are what they read.

**Docs checked:** `docs/ARCHITECTURE.md` (package map, data flow, the
chart-series routing bullet, the tests section), `docs/MODEL.md` (the hover
section: the example and how it was built), `README.md` (the Linux `libegl1`
requirement), `ROADMAP.md` (the five lines naming `chart_series.py`, all
still true: it still imports Flet, and leaves with `PL-7SVX`).
