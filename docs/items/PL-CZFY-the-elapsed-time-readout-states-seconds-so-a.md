---
id: PL-CZFY
title: The elapsed-time readout states seconds, so a run at the newly declared 24-hour limit reads '86400.0 s' - seven characters of tenths on a quantity a reader thinks about in hours
priority: P2
effort: M
status: needs-decision
classes: ux
feature: presentation-safety
touches: src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/control_timeline.py, src/anesthesia_sim/app/simulation_view.py, tests/unit/test_formatting.py, tests/unit/test_simulation_view.py
added: 2026-09-07
---

**Problem.** The elapsed-time readout states seconds, so a run at the newly
declared 24-hour limit reads `86400.0 s` — seven characters of tenths on a
quantity a reader thinks about in hours.

**Why it matters.** `PL-Y5WR` (halt a run at the supported 24-hour run length)
declared the envelope, so the clock's top value is now `86400.0 s` and a reader
has to divide by 3600 to place themselves in the case. The project has already
decided this reads badly, in the one place it had to: `format_supported_run_length`
deliberately does *not* reuse `format_elapsed`, and its docstring names
`86400.0 s` as false precision on a boundary declared in hours. The consequence
is that the interface now states the limit in hours beside a clock counting
toward it in seconds — two displayed forms of one quantity, which is the exact
thing `format_elapsed`'s own one-format invariant exists to prevent.

**Where.** `src/anesthesia_sim/app/formatting.py`: `format_elapsed` (~625) and
its docstring, `format_supported_run_length` (~654), `format_chart_time_label`
(~729) and `_duration_components` (~707). Call sites:
`src/anesthesia_sim/app/simulation_view.py:2253` (the clock) and
`src/anesthesia_sim/app/control_timeline.py:189-192` (control-change stamps).
Tests: `tests/unit/test_formatting.py`, `tests/unit/test_simulation_view.py`.

**Decision needed.** What form does the clock state, given that `format_elapsed`'s
docstring makes one shared format for the clock and the control-change stamps an
invariant, and that a stamp has to resolve the simulation step it was taken at
(`MAXIMUM_SIMULATION_STEP_S = 0.1` s)?

The fork is narrower than that docstring implies, and the reason is a stale
sentence in it. Measured 2026-09-07, `format_chart_time_label` already renders
`12.3s`, `1h23m45.6s` and `24h`: `_duration_components` returns the seconds as a
float and the label formats them with `:g`, so the compound form **keeps** the
tenth. `format_elapsed`'s docstring says "A compound duration form would round
the stamp away", and that is not true of the compound form that shipped. So:

1. **Route the clock and the stamps through `format_chart_time_label`.** One
   format is preserved, the tenth survives, `86400.0 s` becomes `24h`. Costs the
   fixed width the clock has today — the string reflows between `59.9s` and
   `1h0m0.1s` — on a value that updates every step, which
   `_build_trace_legend_item` already records as a defect in a different control.
2. **Keep `format_elapsed` for the stamps and give the clock its own form.**
   Cheapest, and it gives up the invariant rather than satisfying it.
3. **Leave it**, on the grounds that a 24-hour run is not the teaching case and
   seconds are right for the ones that are.

**Done when.** The clock's form at the supported run length is decided and the
reasoning recorded in `format_elapsed`'s docstring, with the "would round the
stamp away" sentence corrected either way; and if the form changes, the
control-timeline stamps and `format_chart_time_label`'s "which is used where"
note agree with it.
