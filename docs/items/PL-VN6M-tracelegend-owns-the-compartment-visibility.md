---
id: PL-VN6M
title: TraceLegend owns the compartment-visibility state inside a widget, which an area system will have to move out
priority: P2
effort: M
status: ready
classes: refactor
feature: interface-areas
touches: src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/simulation_view.py, tests/integration
added: 2026-09-16
verify: uv run pytest tests/integration/test_simulation_view.py && grep -q 'def test_the_compartment_selection_outlives_the_legend_that_renders_it' tests/integration/test_simulation_view.py
---

**Problem.** Which compartments are drawn is held in `TraceLegend`'s own
checkboxes, and `SimulationView` reads it back through `TraceLegend.shown` and a
`visibility_changed` signal. The selection is therefore owned by one widget, and
every other surface that needs it - the chart, the cap notice, a second chart -
reaches into that widget to find out.

**Why it matters.** `.claude/rules/ui-areas.md` test 2: state a layout could
duplicate or relocate does not live inside the widget. Under
`ROADMAP.md` planned-milestone item 34 the legend and the chart become separate
Editors in separate Areas, either of which a reader can close. Close the legend
and the selection goes with it; open a second chart Area and there is no answer
to which legend it follows. Neither is a bug today, because there is exactly one
of each in a fixed layout - which is precisely why it is cheap to move now and
expensive after the area system is built around it.

**It is not a defect and nothing is misdrawn.** The legend and the plot agree
today, by construction: `TraceLegend`'s docstring records that the entry *is*
the state, which is what stops a legend naming a line the chart is not drawing.
That property has to survive the move rather than be traded for it.

**Shape.** The selection becomes a value the dashboard owns and hands down -
the pattern `ChartFrame` already sets for everything else the chart draws
(`draw(frame)` takes one value and holds nothing). `TraceLegend` renders it and
emits a request to change it, rather than being it. `PL-8PSW` added a second
reader of the same state - the two-compartment cap, which is a rule *over* the
selection and is already decided toolkit-free in `app/chart_frame.py` - so the
seam this item cuts along is visible in the source now.

**Where.** `src/anesthesia_sim/app/qt_chart.py` (`TraceLegend`),
`src/anesthesia_sim/app/simulation_view.py` (`_handle_trace_visibility_change`,
`_refresh_view`).

**Done when.** The compartment selection is owned outside `TraceLegend`, the
legend renders it and requests changes to it, and the legend-agrees-with-plot
property is still asserted by test. The named test is what proves it: a
selection that survives the legend being destroyed is exactly what cannot be
written while the checkboxes *are* the state.

**Found 2026-09-16** while building `PL-8PSW`, on the pass that wrote
`.claude/rules/ui-areas.md` (`PL-LH18`). Filed rather than fixed: it needs a new
test and touches files beyond that item's declared `touches`, so `CLAUDE.md`'s
fix-now door is shut on both counts.
