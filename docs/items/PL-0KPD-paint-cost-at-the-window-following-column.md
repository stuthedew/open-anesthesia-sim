---
id: PL-0KPD
title: Paint cost at the window-following column budget is unmeasured: extrapolating the owner's 6.7 us per drawn point from one 3 204-point reading puts two compared runs on a 3 840 px plot at about 207 ms, past the 200 ms render interval, and only the owner's hardware can measure it (found closing PL-PGZF)
priority: P3
effort: S
status: ready
classes: perf
feature: chart-readout
touches: docs/WORKING_NOTES.md
deferred-from: v0.6.0 - captured after the cut, classed perf rather than safety or science, and no entry on the list waits on it
added: 2026-10-18
payoff: the owner knows whether comparing two runs on a wide display keeps each frame inside the 200 ms render interval, rather than relying on one extrapolated reading
verify: grep -qF 'paint measured at the window-following budget' docs/WORKING_NOTES.md
---

**Problem.** Paint cost at the window-following column budget is unmeasured: extrapolating the owner's 6.7 us per drawn point from one 3 204-point reading puts two compared runs on a 3 840 px plot at about 207 ms, past the 200 ms render interval, and only the owner's hardware can measure it (found closing PL-PGZF)

**Evidence.** `PL-PGZF` measured the chart's read, `assemble_chart_frame`, at
the window-following column budget on 2026-10-18 and recorded it in
`docs/WORKING_NOTES.md` under "The read measured at the window-following
budget". The read fits inside the 200 ms frame in every case measured: 28.4 ms
for one run and 55.9 ms for two compared runs on a 3 840 px plot. Paint was not
measured, because this container has no GPU and draws offscreen. The only paint
reading is the owner's of 2026-09-10: 21.57 ms for 3 204 drawn points, about
6.7 us per point. A drawn point is one drawn instant of one trace of one run.
Two compared runs on a 3 840 px plot draw 2 561 instants on each of six traces,
or 30 732 points. At 6.7 us each that is about 207 ms, which is past
`RENDER_INTERVAL_S` (0.2 s, `app/dashboard_frame.py`). One run on a 1 600 px
plot draws about 6 400 points, or about 43 ms.

**Why it matters.** If paint does grow linearly, a learner comparing two runs
on a wide display gets a frame that takes longer than the render interval.
The run then lags its own clock on screen, and the readouts and chart update
later than the simulation they describe. Nothing measures this today. One
reading cannot say whether paint is linear in points, and the interface has no
frame timing of its own since the Qt spike was deleted (`PL-7SVX`).

**Done when.** Paint is measured on the owner's machine at the
window-following budget, for one run and for two compared runs, at plot widths
up to the widest the owner's display gives. The figures are recorded in
`docs/WORKING_NOTES.md` beside the read's, under a heading that carries the
phrase `paint measured at the window-following budget`, with a conclusion on
whether the whole frame fits the render interval. Building that measurement is
part of the work: a script the owner can run, since this container cannot.
A recorded "it fits" closes this as legitimately as a fix would.

**Generator check.** One-off: a measurement left open when the budget began
following the window, not a misread fact.
