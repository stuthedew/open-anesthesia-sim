---
id: PL-Q4M4
title: The simulated-time clock reads in seconds while the chart's own time axis reads in hours and minutes
priority: P2
effort: S
status: done
classes: ux
feature: presentation-safety
touches: src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/control_timeline.py
added: 2026-09-05
closed: 2026-09-13
verify: uv run pytest tests/unit/test_formatting.py tests/unit/test_simulation_view.py && grep -q 'def test_the_clock_panel_reads_in_the_chart_axis_form_past_an_hour' tests/unit/test_simulation_view.py
---

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

**Decision needed.** Which of the three the interface should do. It is the
project owner's call rather than a session's: it changes what is on screen on
every frame, and options 2 and 3 differ over whether a displayed time keeps the
tenth of a second the simulation steps at - a resolution question about what
the reader is being shown, not an implementation detail.

**Done when.** The queue records which option was chosen and why. If it is 2 or
3, the "Simulated time" panel reads in the same format as the chart's axis, and
a test asserts the string the panel renders at a simulated time past an hour.

**Decided 2026-09-13 by the project owner: option 2.** The clock moves to the
compound form and keeps the tenth. Worked together with `PL-CZFY`, which is
the same decision reached from the 24-hour end, and closed with it in one
commit.

Option 1 (leave both, accept the conversion) was the status quo this item
exists to object to. Option 3 (compound form, tenth dropped from the clock)
was refused because it is not needed: the brief's reason for considering it
was that the control timeline needs `0.1 s` resolution and the compound form
would not carry it, and `PL-CZFY` measured that the compound form *does*
carry it - `_duration_components` returns the seconds as a float and the
label formats them with `:g`, giving `1h23m45.6s`. So option 2 satisfies the
stamp's requirement and the axis's at once, and option 3 would have given up
resolution for nothing.

`format_elapsed` and `format_chart_time_label` now share one private
renderer and differ in exactly one respect, the axis origin's bare `0`,
which is a parameter rather than a branch at each site so that the
difference is visible where it is decided.

**The reflow the brief did not raise but `PL-CZFY` did** is paid in layout,
per the owner's direction: `theme.ELAPSED_VALUE_WIDTH` holds the readout's
width open at the widest string the supported run length can reach, so a
component appearing or falling away cannot move the panel under a reader.
`_build_trace_legend_item` already records that rule for the legend rows.
The width is derived rather than measured, and
`test_the_widest_reachable_clock_string_is_what_the_reserved_width_assumes`
is what fails if the form or the envelope changes; nothing renders the
interface in a check yet (`PL-7J96`), so it has not been confirmed by eye.
