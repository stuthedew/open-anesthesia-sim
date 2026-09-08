---
id: PL-KP7H
title: Every LineChartDataPoint carries a default tooltip holding a full TextStyle, which is half the per-point diff cost: dropping it cut a saturated frame from 52 to 27 ms
priority: P2
effort: S
status: done
classes: perf, ux
feature: chart-readout
milestone: v0.4.11
touches: src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py, tests/integration/test_chart_patching.py
added: 2026-09-08
closed: 2026-09-08
pr: 475
verify: uv run pytest tests/integration/test_chart_patching.py tests/unit/test_simulation_view.py && grep -q 'def test_pausing_puts_the_hover_back_and_the_client_is_told' tests/integration/test_chart_patching.py
---

**Problem.** `flet_charts.LineChartDataPoint.tooltip` defaults to
`LineChartDataPointTooltip()`, which itself carries a full `ft.TextStyle()` of
seventeen fields. Flet's `object_patch` descends into both on every point on
every frame, so each of the ~2 080 point controls costs roughly three nested
dataclass comparisons rather than one. `app/chart_series.py` never sets a
tooltip on anything it builds; the cost is entirely the library default.

Measured 2026-09-08, saturated chart at 300x, on the harness `PL-YSZN`
describes. Absolute figures move between runs on that container; the columns
were taken in one run each so the ordering is what to read:

| Variant | Points | Frame | Slider `on_change` |
| --- | ---: | ---: | ---: |
| As shipped | 2 078 | 42.8 ms | 28.5 ms |
| Point tooltip `text_style = None` | 2 078 | 31.4 ms | 25.3 ms |
| Chart tooltips off, point `tooltip = None` | 2 078 | 22.5 ms | 18.0 ms |
| Both, plus column budget 150 -> 75 | 1 098 | 16.2 ms | 11.1 ms |
| Column budget 150 -> 75 alone | 1 098 | 28.3 ms | 17.6 ms |

Sharing one tooltip instance across every point does *not* help: Flet's diff
descends by structure rather than short-circuiting on identity (41.4 ms against
a 52.1 ms baseline in that run, versus 26.8 ms for `tooltip = None`).

**What each option costs.**

- `text_style = None` is in contract — the field is `Optional[ft.TextStyle]` —
  keeps the hover tooltip, and buys about a quarter of the frame.
- `tooltip = None` buys about half, and is *out* of contract: the field is
  declared `Union[LineChartDataPointTooltip, str]` with no `None`. It survives
  `before_update`, which passes a non-`str` through unchanged, but nothing in
  `flet_charts` promises the Dart side accepts it. `flet_charts` ships no
  stubs, so the type checker will not catch a later change of that contract.
  `LineChart.tooltip = None` *is* documented as "no tooltips will be shown
  throughout this chart" — but it is chart-level, and setting it leaves every
  point's tooltip object in the tree, so it disables the feature without
  buying any of the saving.
- Removing the tooltip removes a live feature: `LineChart.interactive`
  defaults to `True` ("enables automatic tooltips and points highlighting when
  hovering over the chart") and the app never sets it. `PL-7H0X` argues that
  feature should go on its own merits.

**Done when** one of the three is chosen with its reason recorded, the
`interactive` flag is set to match rather than left at its default, and
`tests/integration/test_chart_patching.py` holds whatever the choice is
against the real session.

**Resolved: the hover is offered while the run is paused and withdrawn while
it plays** (project owner, 2026-09-08, choosing the third option above with
that condition). It is a better answer than any of the three as written,
because the cost and the feature turn out not to compete: `_run_render_timer`
takes no frame while the run is stopped, so a paused chart carrying tooltips
costs nothing per second, and a value read under a cursor on a trace advancing
a simulated minute per frame was never readable anyway. Every drawn point is
also an M4 representative of a bucket rather than a sample, which is a thing to
study rather than to glance at.

`chart_series.build_point` is now the single constructor of a plotted point and
builds without a tooltip; `chart_series.apply_point_tooltips` writes them back;
`SimulationView._apply_chart_tooltips` is the one writer of the mode and sets
`LineChart.interactive` in the same pass, so a chart cannot be left interactive
over tooltipless points or the reverse. Built without and given one back, never
the other way round: a point appended mid-run would otherwise arrive carrying
the cost this removes.

Measured after, same harness and machine as above:

| Rate | `page.update` before | after | Delivered rate before | after | Input delay p90 before | after |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1x | 15.8 ms | 9.3 ms | 91% | 94% | 14.5 ms | 10.7 ms |
| 5x | 41.1 ms | 19.8 ms | 82% | 89% | 43.4 ms | 23.4 ms |
| 20x | 40.9 ms | 21.1 ms | 77% | 85% | 56.5 ms | 29.4 ms |
| 60x | 42.0 ms | 20.4 ms | 74% | 85% | 59.6 ms | 29.4 ms |
| 300x | 43.8 ms | 20.3 ms | 73% | 84% | 49.4 ms | 20.6 ms |

One slider `on_change` fell from 59.1 ms to 23.3 ms on a saturated chart. That
is still too expensive to service a drag — 0.7 s of event-loop time per second
at 30 events a second, against 1.8 s before — which is `PL-R2YM`, and it is now
the largest remaining term in the interaction path.

**What it costs, stated rather than buried.** The transition frame carries
about 1 870 tooltip operations and 90 KiB: 71.9 ms on the frame that pauses and
33.4 ms on the frame that resumes, against a steady frame's handful of
operations. That is a single frame on a button press rather than a sustained
rate — `PL-Q197`'s saturation was ~17 900 operations a *second* — and the
render loop stops immediately after it.

**Two things this hands on.** `PL-YLKR` (design what a chart tooltip says)
matters more now than it did: the tooltip has become a readout a reader
deliberately stops to consult rather than one they brush past, and what it
currently says is `flet_charts`' default. `PL-7H0X` keeps its open half — what
that default actually renders, which no session here has had a client to see.
