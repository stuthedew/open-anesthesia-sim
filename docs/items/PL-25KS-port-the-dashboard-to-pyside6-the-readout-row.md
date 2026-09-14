---
id: PL-25KS
title: Port the dashboard to PySide6: the readout row, the four parameter controls, the agent selector, the transport, the new-case dialog and the notice banner
priority: P1
effort: L
status: ready
classes: feature, ux
feature: qt-port
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/main.py, tests/unit, tests/integration, docs/ARCHITECTURE.md
added: 2026-09-10
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
