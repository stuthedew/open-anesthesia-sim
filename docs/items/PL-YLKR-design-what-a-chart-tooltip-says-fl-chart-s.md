---
id: PL-YLKR
title: Design what a chart tooltip says: fl_chart's default is a bare number, and PL-KP7H makes the tooltip a paused-only readout that a reader will actually stop and study
priority: P1
effort: M
status: done
closed: 2026-09-14
classes: safety, ux
feature: presentation-safety
touches: docs/MODEL.md, ROADMAP.md, docs/items
added: 2026-09-08
verify: python3 tools/doc_check.py check && grep -qF 'what the tooltip may show' docs/MODEL.md
---

**Problem.** Design what a chart tooltip says: fl_chart's default is a bare number, and PL-KP7H makes the tooltip a paused-only readout that a reader will actually stop and study

**Where this now stands.** `PL-KP7H` landed the hover as a paused-only
affordance: points carry no tooltip while the run plays, because Flet's diff
descends into one on every point on every frame, and get one back the moment
the run stops, where the render loop takes no frames and the cost is nil. So
the tooltip has changed character. It used to be something a reader might brush
past on a moving trace; it is now the thing they get by deliberately pausing to
look at a value, which is exactly when what it says has to be right.

What it says today is `flet_charts`' default, from a
`LineChartDataPointTooltip(text=None)` this application never writes into.

**Three things it owes a reader**, and the first is the one only this project
can know:

1. **That the value is modelled, not measured.** Every drawn point *is* a
   state of the run at the instant it is drawn at — `app/chart_series.py`
   interpolates, extrapolates and synthesizes nothing, and a control event
   always gets its own column — so reporting the y value as the value at that
   instant is correct. What it is not is an observation: it is a lumped
   compartment model's alveolar fraction, and a reader who takes it for an
   end-tidal measurement has made exactly the mistake `CLAUDE.md` requires a
   display to prevent. A bare number in a grey box prevents nothing.
2. **Units, compartment and agent.** A bare number in a grey box satisfies none
   of the traceability the safety-critical standard requires of a clinically
   meaningful displayed value.
3. **Its own resolution.** `docs/MODEL.md` § "Displayed precision" derives what
   the readouts may show; nothing derives what this may show, and it should be
   the same derivation or an explicitly different one with a reason.

**And that it exists at all.** A hover that answers only while paused is a
hidden mode: a reader who tries it during a run gets nothing and concludes the
chart is not interactive, so they never find it. Whatever the tooltip comes to
say, something on screen has to say the affordance is there — a caption that
changes on pause is the cheap version. This is part of the same design rather
than a separate item, because a tooltip nobody can find and one nobody can read
fail a reader identically.

**Done when** the tooltip's content is designed and implemented, `docs/MODEL.md`
carries the derivation of what it shows the way it does for the readouts, and
`README.md` says the affordance exists and when.

**Why it matters.** `PL-KP7H` changed what this affordance is. While the tooltip
appeared on a moving trace it was something a reader might brush past; it is now
what a reader gets by deliberately pausing to look at a value, which is exactly
the moment its contents have to be right. A number somebody stopped the
simulation to read is one they will act on.

The safety-relevant half is the first of the three above and it is the one no
report of "it works" can answer: the number is a modelled state of a lumped
compartment model, and nothing on or near the tooltip says so. The reader who
stopped the simulation to study one is the reader most likely to take it for an
observation, and they have no way to tell the two apart from what is on screen.

**The port changes the mechanism, not the design.** `PL-G59B` replaces fl_chart
with pyqtgraph, so whatever fl_chart's default prints stops mattering - but the
three obligations transfer whole. Design it once here and implement against
whichever chart is live. `PL-7H0X` was dropped into this item for that reason.

**Corrected 2026-09-14 (`PL-3M3K`).** That paragraph used to add "and so does
the hidden-mode problem, since a paused-only affordance is equally
undiscoverable in either toolkit". The three content obligations do transfer;
the hidden mode does not, because the affordance is only paused-only *on Flet*.
`PL-KP7H` withdrew it during a run because Flet's diff descends into every
point's tooltip object on every frame - a per-frame per-point cost Qt does not
have, by either route a pyqtgraph readout can be built on. So the port
dissolves that half rather than inheriting it, and the "caption that changes on
pause" this item proposed would have been designing around a constraint that
expires. What the port does *not* dissolve is the affordance's existence:
`ScatterPlotItem` ships `hoverable` set to `False` and a plotted line carries
no hover at all, so silence in the port loses it outright (`PL-DNHM`).

**Corrected 2026-09-13 (`PL-DZFJ`).** Both passages above used to say that a
drawn point is an M4 representative of a bucket of roughly 120 recorded samples,
and that presenting it as the value at that instant is false precision. That has
not been true since v0.4.12: `PL-2FM6` deleted the M4 decimation module,
`RunHistory`, `HistoryWindow` and `SimulationHistorySample`, and the chart
evaluates the run's score at the instants it plots. The first obligation is
therefore not "the point is not a sample" but "the point is modelled rather than
measured" - a different design problem reaching the same remedy, which is why
this item survives the correction rather than shrinking to two obligations.
`ROADMAP.md`'s gate admission for this item carried the same sentence and was
corrected in the same pass.

**Split, and resolved as the design half** (project owner, 2026-09-14). Asked
whether a Flet-facing item should simply be dropped now that the interface is
leaving Flet, the answer was that this one is not a Flet item: two of its three
`touches` were documentation, its own `verify:` tests only `docs/MODEL.md`, and
pyqtgraph reproduces the same defect rather than dissolving it - its default
`tip` is `'x: {x:.3g}\ny: {y:.3g}\ndata={data}'.format`, a bare coordinate pair.
So the design and its derivation land here, on `v0.4.x`, and the implementation
becomes `PL-YVHK`, `blocked-by: v0.5.1` and named in that milestone's
`Required scope` item 1.

**What landed.** `docs/MODEL.md` § "The chart's hover readout: what the tooltip
may show" derives the contents as § "Displayed precision" derives the readouts':
the three-line form and why the qualifiers precede the number; every number
through `app/formatting.py` rather than through the chart library; the readouts'
own resolution, with the argument for a finer hover readout answered rather than
inherited; the below-resolution forms kept; which series answer a hover and why
the references and control marks do not; and that the hover answers running or
paused. It carries a measured table of what `.3g` prints against what this
project's formatter prints, at four instants of a 1 MAC sevoflurane hour - the
worst of them `3.52e-05` where the readout says `<0.01%`.

**What did not land, and is stated rather than left to be discovered.** The
shipped Flet build keeps `PL-KP7H`'s paused-only hover with its library-default
contents until the port. Building it twice was refused on cost: roughly 1 870
per-point strings on Flet, onto a pause-transition frame already measured at
71.9 ms and 90 KiB, against one format callable under pyqtgraph. `README.md`
moves to `PL-YVHK` with the implementation, because it cannot say the affordance
exists until it does.
