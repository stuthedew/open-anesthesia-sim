---
id: PL-25KS
title: Port the dashboard to PySide6: the readout row, the four parameter controls, the agent selector, the transport, the new-case dialog and the notice banner
priority: P1
effort: L
status: done
classes: feature, ux
feature: qt-port
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/main.py, src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/theme.py, tests/unit, tests/integration, tests/reference/test_coupled_dynamics.py, tools/agent_identity_check.py, tools/contrast_check.py, tools/import_boundary_check.py, tools/glyph_check.py, pyproject.toml, docs/ARCHITECTURE.md, docs/MODEL.md, README.md, .claude/rules/ui-color.md
added: 2026-09-10
closed: 2026-09-15
verify: uv run python tools/import_boundary_check.py && grep -q 'PySide6' src/anesthesia_sim/app/main.py
---

**Problem.** Port the dashboard to PySide6: the readout row, the four parameter controls, the agent selector, the transport, the new-case dialog and the notice banner

**The Qt port's Required scope, item 2** - the bulk of it.
`app/simulation_view.py` is 4 321 lines and this is most of what replaces it.

**The hedges are requirements, not labels.** "end-tidal-equivalent" and
"inspired" are `PL-NV9W` and `PL-8M05`; "common gas outlet" is `PL-71CF`.
Each has a test holding the exact pair of strings, and each exists because the
unhedged form is a wrong clinical inference from a correct number. The spike
carries all three and `spikes/qt/chart_sources.py` records why.

**One thing the spike does better than the shipped build, worth keeping.** Qt
sliders are integer-valued, and the spike turns that into a property: the steps
are the display resolution, so the value applied to the model is exactly the
value printed beside it. The Flet slider is continuous and rounds only its drag
label, which is what `PL-3TLK`'s comment had to reason about.

**`PL-B9PY`'s decomposition is a required input, not a later pass.** That item
ships in v0.5.0 on Flet - Gate 1 places it under "Cleared by v0.5.0 itself",
because rendering two runs at once is what the branched-run milestone is - and
this port rewrites the class it decomposed. Build the Qt view decomposed from
the start: read `PL-B9PY` for the seam it establishes rather than reproducing
one class holding one run's widgets and then splitting it again.

**Why it matters.** It is the bulk of the milestone and the point at which the
interface stops being two toolkits. `app/simulation_view.py` is 4 321 lines and
this replaces most of it; until it lands, `PL-7SVX` cannot run and the port is
not a port.

It is also where presentation-safety either survives the rewrite or is lost. The
three hedges are requirements rather than labels - "end-tidal-equivalent" and
"inspired" (`PL-NV9W`, `PL-8M05`) and "common gas outlet" (`PL-71CF`) - each
exists because the unhedged form is a wrong clinical inference from a correct
number, and each has a test holding the exact pair of strings. A rewrite that
reproduces the layout and drops a hedge ships a safety regression that looks
like a successful port.

**Done when.** The readout row, the four parameter controls, the agent selector,
the transport, the new-case dialog and the notice banner render under PySide6;
every existing test that holds a hedged string still passes against the new
widgets; the view is built decomposed along the seam `PL-B9PY` establishes
rather than as one class to be split later; and the integer-slider property the
spike demonstrates is kept, so the value applied to the model is exactly the
value printed beside it.

**Rider, 2026-09-14 (pre-port survey).** `touches` gains `docs/ARCHITECTURE.md`:
the definition of done says it must "describe the interface that exists", and
its package map is held to disk in both directions by `tools/doc_check.py`, so
every module this item adds or removes edits that map in the same commit or
fails `make check`. The line count above is corrected from 3 619 to 4 321,
`PL-B9PY` having grown the file since the brief was written.

**Raised to `P1`, 2026-09-14.** `PL-2K1R` (the interpretation disclaimer,
`P1` `safety`) now waits on this item, and the store's band rule is that
nothing waits on a blocker below its own band - the same reason `PL-G59B` is
`P1` for `PL-GS3R` and `PL-YVHK`. The port's two build items now sit at the
band the safety work behind them already held.

**What the chart port left for this item, 2026-09-14 (`PL-G59B`).** The
dashboard assembles one `chart_frame.ChartFrame` per render tick -
`assemble_chart_frame` over a `RunInput` per run (controller, the snapshot
the same tick formats the readouts from, and the `AdjustmentGrouping`'s
adjustments), the selected time base or `None` for "Fit run", and
`TraceLegend.shown` - and calls `draw` on `qt_chart.ConcentrationChart` and
`qt_chart.WashInChart` with it; `TraceLegend.visibility_changed` is the
signal to redraw on. The chart panel's captions are this item's, read off the
frame rather than re-derived: the time-axis caption from `ChartFrame.fitted`
and `time_base`, `format_mac_reference` and `format_mac_awake_reference` from
the reference snapshot, the wash-in state sentence from `read_wash_in` and
`RunFrame.undrawn_wash_in_stretches`, the off-scale notice from
`RunFrame.percents` against `axis_top_percent`, and the unmarked-adjustments
count from `RunFrame.undrawn_control_marks`. The `README.md` hover line
(`PL-YVHK` item 5) lands here too, since this is what makes the Qt chart the
shipped one.

**`verify:` rewritten 2026-09-14.** `grep -rq 'PySide6' src/anesthesia_sim/app/`
started passing when `PL-G59B` put `app/qt_chart.py` in the tree, so
`docket check --verify` refused it. It now names `app/main.py`, which this
item alone rewrites to build the Qt application, and which imports Flet
today; run and seen to fail (exit 1).

**Started 2026-09-15, and the shape it takes.** Four decisions the design had
to make, recorded before the first commit so the reasoning outlives the branch:

1. **The Flet dashboard leaves with this item, not with `PL-7SVX`.**
   `tools/agent_identity_check.py` admits exactly one `_apply_agent_color_scheme`
   writer across the whole of `app/`, and its identity set is whatever that
   writer writes - so a Qt dashboard and the Flet one cannot both be measured
   in one tree, and a tool weakened to one writer per class would stop meaning
   what it means. `app/simulation_view.py` (Flet), `app/chart_series.py`,
   `tests/unit/test_simulation_view.py` and
   `tests/integration/test_chart_patching.py` go here; `spikes/`, the Flet
   dependencies and `PL-C92D`'s table stay with `PL-7SVX` and `PL-3SQT`. The
   `flet`/`flet_charts` boundaries become `allowed=()` in the same change,
   which is `PL-7SVX`'s "held rather than merely current" half arriving early.
2. **The split follows the chart port**: `app/dashboard_frame.py` states every
   string and every per-tick claim with no toolkit loaded; `app/qt_widgets.py`,
   `app/run_view.py` and `app/simulation_view.py` move widgets to match it and
   decide nothing. The tests port by claim, not by mechanism, under their own
   names, into `tests/unit/test_dashboard_frame.py` and
   `tests/integration/test_simulation_view.py`.
3. **`PL-TG60` is re-argued on a measurement, not on the residual.** Perturbing
   one stored coefficient by one published SD (the method § "Displayed
   precision" uses for the readouts) moves the exhaust total by 0.016-0.042 L
   at 3600 s and 0.18-0.23 L at the 24 h limit, blood:gas dominant. One count
   of 0.1 L therefore sits between a quarter of an SD and six SDs across the
   whole supported span; 0.01 L falls to a fiftieth of an SD by 24 h. The panel
   prints one decimal through `formatting.format_agent_volume`, with the unit
   stated as the specification states it ("Litres of equivalent pure agent
   gas"), and the residual lines keep `:.3e`.
4. **Riders that close here because the Flet chart leaves or because the text
   is written once**: `PL-2K1R` (the interpretation line, wording open to the
   owner), `PL-3355`, `PL-TG60`, `PL-005`, `PL-YVHK` item 5, `PL-YCWZ` with
   `PL-2QMK`, and `PL-Q4VH` with `PL-THXF`, whose defects the Qt chart already
   fixed by construction and which waited only for the Flet chart to go.

`touches` widened accordingly on the same day; `tools/agent_identity_check.py`
is in it because its own docstring records that rule 1's Qt spelling is "the
half to port first", and no other open item declares the file.

**Closed 2026-09-15.** The dashboard renders under PySide6 from the same
controller, in four modules rather than one: `app/dashboard_frame.py` states
every string and every per-tick claim with no toolkit loaded (72 tests, no
display); `app/qt_widgets.py` holds the leaf widgets that decide nothing -
`MetricPanel` reserving the widest value's width, `ReadoutRow` reflowing
where its measured panels stop fitting, the integer `ParameterSlider` whose
one step is the display resolution, `NoticeLabel`, `NewCaseDialog` with the
keep button as the default, `inert_splitter`, `initial_window_geometry` and
a `FlowLayout` for the legend rows; `app/run_view.py` is `RunView`, one run's
widgets, controller, handlers, refresh and halt, with
`_apply_agent_color_scheme` the single writer of agent colour; and
`app/simulation_view.py` is `SimulationView`, what runs share, inside nested
inert splitters. `tests/integration/test_simulation_view.py` ports the Flet
dashboard's widget-level claims under their own names against real
controllers, headless (123 tests); `tests/integration/test_qt_widgets.py`
holds the leaf widgets; `tests/integration/test_qt_rendering.py` renders the
whole interface at a fixed size and reads pixels and geometry back. The
Flet dashboard, its chart-series module and their two test files are gone,
and `flet` and `flet_charts` are permitted in no module under `src/`.

**Two facts a later session should know.** The readout row seats seven
panels across only where the seven columns' own reserved widths fit - each
column the widest value it can show, so the clock's wide elapsed form costs
no other column - which is 1 068 logical pixels of row on this container's
font, a window of about 1 100, and a screen of about 1 375 at the startup
fraction; four below that. The pixel breakpoints `PL-8M05` measured on Flet
are replaced by that rule, and the reservation (the 22 px value size, the
panel padding, the glosses' italic width) is `PL-L9RD`'s lever if seven
across on a 1 366 px laptop is wanted - it is nine pixels short today. And `PySide6.QtCore.Signal.emit` swallows a slot's exception, so
every presentation path guards `_refresh_view` itself rather than relying
on a raise reaching the caller.

**Docs checked:** `docs/ARCHITECTURE.md` (package map, data flow, the app
prose, the loops, the tools section, the tests section, where new code
belongs), `docs/MODEL.md` (the hazard table and its partly-mitigated row,
the reproducibility list, the interface boundary headings, the drawn-columns
paragraph, the readout row's width condition, the accounting precision, the
displayed-precision terminus, the hover section), `README.md` (the hover
line, the Linux `libegl1` line), `ROADMAP.md` (six citations of the deleted
module), `docs/WORKING_NOTES.md` (the testing thread and the mockups thread),
`docs/worker.md` (how a session writes the screenshot),
`.claude/rules/ui-color.md` (what the checks read), `CONTRIBUTING.md`.
