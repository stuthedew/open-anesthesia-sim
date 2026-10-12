---
id: PL-VN6M
title: TraceLegend owns the compartment-visibility state inside a widget, which an area system will have to move out
priority: P2
effort: M
status: done
classes: refactor
feature: interface-areas
milestone: v0.5.24
touches: src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/compartment_selection.py, src/anesthesia_sim/app/dashboard_frame.py, docs/ARCHITECTURE.md, .claude/rules/ui-areas.md, tests/integration, tests/unit/test_compartment_selection.py, docs/items/PL-9LNF-three-app-surfaces-own-state-a-layout-could.md, docs/items/PL-7694-the-compared-run-count-and-a-run-s-index-are.md
added: 2026-09-16
closed: 2026-10-12
pr: 1448
verify: grep -q 'def test_the_compartment_selection_outlives_the_legend_that_renders_it' tests/integration/test_simulation_view.py && uv run pytest tests/integration/test_simulation_view.py
---

**Problem.** Which compartments are drawn is held in `TraceLegend`'s own
checkboxes, and `SimulationView` reads it back through `TraceLegend.shown` and a
`visibility_changed` signal. The selection is therefore owned by one widget, and
every other surface that needs it - the chart, the cap notice, a second chart -
reaches into that widget to find out.

**Why it matters.** `.claude/rules/ui-areas.md` test 2: state a layout could
duplicate or relocate does not live inside the widget. Under
`ROADMAP.md` planned-milestone item 34 the legend and the chart become separate
Views in separate Areas, either of which a reader can close. Close the legend
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

## Next steps, 2026-10-12 (handed over for length, claim kept)

Claimed on `claude/layout-model-3hx1dj` with `PL-1FT6` (pull request `#1448`);
the first thread closed `PL-1FT6` and stopped at its spend budget before
starting this. Re-confirmed against the tree that day: the brief holds.

- **The value.** A toolkit-free, immutable selection of shown compartments,
  in a new `app/` module beside `app/chart_frame.py`, built through its check.
  The cap is `chart_frame.compared_compartments(shown, run_count)`
  (`src/anesthesia_sim/app/chart_frame.py:422`, two when more than one run is
  drawn): read it, never restate it.
- **The legend.** `TraceLegend` (`src/anesthesia_sim/app/qt_chart.py:1541`)
  renders a selection it is handed and emits a request on a toggle. Today it
  owns `_check_order` and `_run_count` and drops the oldest box over the cap
  (`_drop_oldest_over_cap`), so that rule moves to the value. `WashInLegend`
  is a different class and is outside this item unless it holds the same
  state.
- **The owner.** `SimulationView` holds the selection and hands it to the
  legend and to `assemble_chart_frame`: the legend is built at
  `simulation_view.py:302`, `_rename_runs` calls `set_run_count`, and
  `_refresh_view` passes `self._legend.shown` to the frame.
- **Tests.** `tests/integration/test_qt_chart.py`,
  `tests/integration/test_simulation_view.py` (its `_set_trace_shown` helper,
  the cap test, and two reads of `_legend._run_count`) and
  `tests/integration/test_dark_appearance.py` (constructs `TraceLegend()`).
  Keep every existing assertion's text true and add new ones beside it:
  `verify --self` refuses an assertion edited in place unless the base copy
  declares `falsifies:`. Add
  `test_the_compartment_selection_outlives_the_legend_that_renders_it` to
  `tests/integration/test_simulation_view.py`, which `verify:` greps.
- **Docs.** `docs/ARCHITECTURE.md` § "Where new code belongs" calls
  `ChartFrame.visible` the subset the legend leaves drawn;
  `.claude/rules/ui-areas.md` names `TraceLegend` as the standing
  counter-example (line 57), so widen `touches` to it; docstrings.
- **Then the pull request** - `/mnt/project-files/v0.6.0/gate-batch.md` has
  the steps left for `#1448` as a whole.
