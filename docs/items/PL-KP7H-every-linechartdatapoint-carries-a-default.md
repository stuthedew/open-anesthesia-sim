---
id: PL-KP7H
title: Every LineChartDataPoint carries a default tooltip holding a full TextStyle, which is half the per-point diff cost: dropping it cut a saturated frame from 52 to 27 ms
status: untriaged
added: 2026-09-08
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
