---
id: PL-THXF
title: The trace legend swatch is a solid bar for a trace that is dashed, so the legend's own redundant channel is words only
priority: P2
effort: S
status: ready
classes: defect, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py
verify: uv run pytest -q tests/unit/test_simulation_view.py && grep -q 'def test_each_legend_swatch_is_drawn_in_its_traces_dash_pattern' tests/unit/test_simulation_view.py
added: 2026-09-07
---

> **This fix rides the Qt port (`v0.5.1`), not Flet.** `ROADMAP.md` § "v0.5.1 -
> the interface moves to Qt" names this item under "Fixes this port carries":
> the defect lives in code that milestone rewrites from scratch, so fixing it
> on Flet means writing the same lines twice. Project owner, 2026-09-10.

**Problem.** `_build_trace_legend_item` draws each compartment's legend mark as
an `ft.Container` filled with the trace's colour — a solid 24x4 bar, whatever
the trace's dash pattern is. The pattern reaches the reader only as a word in
the checkbox label: "Vessel-rich (even dash)". So the legend *mark* identifies
six traces by colour alone, and the reader has to translate a phrase into a
visual pattern to match a curve to its name.

**Why it matters.** `PL-GVXP` made the dash pattern the channel that actually
separates these six curves, because no palette can separate them: holding each
trace to 3:1 against the panel caps its luminance, and six traces under that
cap cannot be more than about 1.48 apart pairwise. That makes the words
load-bearing rather than supplementary, and the set they now have to carry is
"solid / long dash / short dash / even dash / dotted / dash-dot" — six phrases
whose differences are finer than the differences between the lines they name. A
swatch drawn in the trace's own pattern removes the translation: the reader
compares a mark to a curve rather than a phrase to a curve.

The three other legend rows already do this. `_build_band_legend_item` draws
the MAC-awake band ruled on both edges because that geometry is what
distinguishes it on the chart, and `_build_control_mark_legend_item` draws an
upright bar because the control mark's own channel is that it is vertical. The
compartment row is the one that shows a mark it is not drawing.

**Approach.** `ft.Container` has no dash. Two candidates: compose the swatch
from a `ft.Row` of small containers sized from the same `dash_pattern` list the
series is built with, or draw it on an `ft.canvas`. The first keeps the swatch
a plain control that `_apply_trace_visibility` can still fill and empty by
setting `bgcolor`, and takes its geometry from the one list rather than a second
copy — which is the property `_CompartmentTrace` exists to protect. Prefer it
unless the row's spacing cannot be made exact.

Whatever is built, the swatch's outer size must not change with the trace's
visibility or its pattern: this is a control a reader clicks repeatedly, and
`_build_trace_legend_item` records why a row that reflows under the cursor is a
defect.

**Where.** `src/anesthesia_sim/app/simulation_view.py`:
`_build_compartment_trace` (builds the swatch), `_build_trace_legend_item`,
`_apply_trace_visibility` (fills and empties it), `LEGEND_SWATCH_WIDTH` /
`LEGEND_SWATCH_HEIGHT`; `tests/unit/test_simulation_view.py`
`test_the_legend_says_exactly_which_traces_are_drawn` asserts
`trace.swatch.bgcolor` and would need to move to whatever carries the fill.

**Done when.** Each compartment's legend mark is drawn in that trace's own dash
pattern, taken from the same list the series is built from rather than a second
copy; the mark still shows and hides with the trace without changing size; and
a test fails if a swatch's geometry stops matching its series' `dash_pattern`.

**Note.** The words stay. They are what a screen reader and a monochrome
printout get, and `docs/MODEL.md` § "The six compartment traces" records the
style table. This adds the visual channel beside them rather than replacing
them.
