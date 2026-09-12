---
id: PL-7H0X
title: The chart is interactive with automatic tooltips left on, so hovering a trace shows an unlabelled number read off an M4-decimated point rather than a sample
status: dropped
added: 2026-09-08
closed: 2026-09-12
reason: Overtaken by the Qt port. What remained was to read fl_chart's default tooltip and write down what it prints, as the known starting point for PL-YLKR. v0.5.1 replaces fl_chart with pyqtgraph (PL-G59B), so that reading describes a component being deleted and is no longer the input PL-YLKR needs. The substance transfers intact and is already stated in PL-YLKR: that a drawn point is an M4 representative rather than a sample, that a bare number carries no unit, compartment or agent, and that nothing derives the tooltip's resolution the way docs/MODEL.md derives the readouts'. PL-KP7H already settled the half that was about the flag being undeclared.
---

**Problem.** `flet_charts.LineChart.interactive` defaults to `True` —
"enables automatic tooltips and points highlighting when hovering over the
chart" — and `app/simulation_view.py` never sets it. Each
`LineChartDataPoint` also carries the library's default
`LineChartDataPointTooltip(text=None, ...)`, and `app/chart_series.py` never
gives one any text. So the interface has a hover readout nobody designed, on
both charts, whose contents are whatever `fl_chart` produces from a null text.

Three separate problems with that, if it renders as expected:

1. **The point is not a sample.** `redraw_series` draws
   `CHART_COLUMN_BUDGET_PER_SERIES` columns of M4-decimated data — at 300x and
   an 18 000-sample run, one drawn point stands for roughly 120 recorded ones
   and is the bucket's minimum, maximum, first or last. A tooltip reading a
   drawn point reports one selected sample as though it were the value at that
   instant.
2. **No unit, no compartment, no model identity.** `CLAUDE.md` counts the
   correct number with the wrong units or label as a safety failure, and
   requires a clinically meaningful displayed value to be traceable to the
   model, inputs, units and transformations that produced it. A bare `y` in a
   grey box is none of that.
3. **Undeclared.** `docs/MODEL.md` § "Displayed precision" derives what the
   readouts may show. Whatever the tooltip prints was derived by nobody.

**Not confirmed against a live client.** This is read off the `flet_charts`
source and the app's own construction, not off a screenshot: no client was
available in the session that found it (2026-09-08). Confirm what actually
renders before deciding — it may show nothing at all, in which case the item
collapses into `PL-KP7H`, which wants the tooltip objects gone for an
unrelated reason (they are half the per-frame diff cost, `PL-YSZN`).

**First step.** Run the app, hover a trace on both charts, and record what
appears. Then set `interactive` explicitly to whatever is decided, rather than
leaving it at a default nobody chose.

**Half of this is answered.** `PL-KP7H` set `LineChart.interactive` explicitly
rather than leaving it at a default nobody chose: it is now false while the run
plays and true while it is stopped, written in one place with the per-point
tooltips. So "undeclared" no longer describes the flag.

What remains is the part that needed a client and still does: **what the
default tooltip actually renders**, and therefore whether points 1 to 3 above
describe a real defect or a feature that shows nothing at all. `PL-YLKR` is
where the answer goes either way — it designs the content — so if the hover
turns out to render nothing, close this as answered and let `PL-YLKR` carry the
design from scratch.

**Confirmed on a live client, 2026-09-08** (project owner): the paused hover
works. That settles two things and deliberately not a third.

Settled: the tooltip **renders and behaves** on a paused run, which is the
first live-client confirmation of `PL-KP7H` end to end — Flet's diff reports
the `tooltip` mutation, the client acts on it, and `interactive` toggling
reaches the chart. `tests/integration/test_chart_patching.py` asserted the
patch; this is the other end of it.

Settled: this item's premise holds. There *is* an automatic hover on the
traces, so it is not a feature that shows nothing, and the case for designing
what it says does not collapse.

**Not settled: what it says.** "Works" is a report that the affordance
functions, not that its contents are right, and the owner had already asked
for the tooltip to be made more readable — which is `PL-YLKR`. So the three
concerns above stand unexamined: whether the number carries a unit, a
compartment and an agent, and whether it presents an M4 representative of a
bucket as though it were the sample at that instant. That last one is the
safety-relevant half and no report of "it works" can answer it.

**What is left here**, now that `PL-KP7H` set `interactive` explicitly and the
affordance is confirmed: read the rendered tooltip against the three concerns
and write down what it actually prints. Then this item closes and `PL-YLKR`
designs the replacement from a known starting point rather than a guess.
