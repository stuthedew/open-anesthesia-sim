---
id: PL-Q4M4
title: The simulated-time clock reads in seconds while the chart's own time axis reads in hours and minutes
status: untriaged
added: 2026-09-05
---

**Problem.** The simulated-time clock reads in seconds while the chart's own time axis reads in hours and minutes

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `PL-SSBP` gave the chart a time base that spans a case, and its
axis reads in units that carry themselves - `3m`, `1h30m`, `12h`. The
"Simulated time" panel above it still reads `format_elapsed`'s `5400.0 s`, and
so does every recorded control change in the run record beside the chart. One
quantity, two formats, on one screen.

**Why it matters.** `format_elapsed`'s own docstring names this hazard - "a
timeline reading in one time format beside a clock reading in another would
leave the reader converting between two displayed times of the same quantity"
- and the same docstring anticipated the case-length time base as the moment
the project would have to decide. A reader locating a control mark on a
twelve-hour axis has to convert `5400.0 s` into `1h30m` by hand to find it,
which is a conversion the display should be doing.

**The two are not one function, which is why this is a decision and not a
rename.** `format_elapsed` stamps a recorded time at the tenth of a second
the simulation steps at, and the control timeline needs that resolution;
`format_chart_time_label` is legible across half a day and rounds a tenth
away. The question is which of three the interface should do:

1. Leave both, and accept the conversion. Cheapest, and the status quo.
2. Move the clock to the compound form, keeping a tenth where one exists
   (`1h30m0.5s`). One format, at the cost of a longer and busier readout.
3. Move the clock to the compound form and drop the tenth, keeping seconds
   only in the control timeline where the stamp is read against a step.

**Where.** `app/formatting.py` (`format_elapsed`, `format_chart_time_label`),
`app/simulation_view.py` ("Simulated time" panel), `app/control_timeline.py`.

**Not urgent, and not a wrong number.** Both readings are correct and
unambiguous; this is a conversion the reader is doing that the display could
do for them.
