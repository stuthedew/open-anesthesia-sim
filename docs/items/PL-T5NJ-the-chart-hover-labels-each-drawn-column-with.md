---
id: PL-T5NJ
title: The chart hover labels each drawn column with its instant rounded to 0.1 s but prints the state at the column's exact instant, so early in a high-flow induction it pairs a value with an instant at which the model held a different displayed value, such as desflurane's circuit 2.70% shown at "6s" where the state at 6.0 s is 2.68%
priority: P1
effort: S
status: done
classes: ux, defect, safety
feature: replay-findings
touches: src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/chart_time_base.py, src/anesthesia_sim/app/controller.py, tests/unit/test_chart_frame.py, tests/integration/test_controller.py, docs/MODEL.md
added: 2026-10-25
closed: 2026-10-26
pr: 1840
payoff: a paused reader never sees one instant labelled with two different concentrations in the hover and the readout
verify: grep -q 'def test_the_hover_value_belongs_to_the_instant_it_prints' tests/unit/test_chart_frame.py
---

**Problem.** `_hover_instant` (`src/anesthesia_sim/app/chart_frame.py`) rounds the instant to `HOVER_INSTANT_RESOLUTION_S` (0.1 s). The value printed beside it is the state at the unrounded instant. The comment above `HOVER_INSTANT_RESOLUTION_S` says that over 0.05 s "no compartment moves by a hundredth of a percent". That is false early in a fast induction. Reproduced on main: desflurane at 18% and 10 L/min puts the circuit at 2.68% at 6.00 s and 2.70% at 6.04 s, and at 3.15% at 7.20 s and 3.16% at 7.24 s.

**Why it matters.** A paused reader sees the readout row at 6.0 s show 2.68% while the hover at "6s" shows 2.70%. That is a displayed clinical value attributed to the wrong instant, which the safety-critical standard treats as a presentation failure. A fix could snap the columns to the 0.1 s clock grid, or print the instant finely enough that the value belongs to it.

**Done when.** The hover prints a value that belongs to the instant it prints: either the columns sit on the 0.1 s clock grid, or the instant is printed finely enough. The comment above `HOVER_INSTANT_RESOLUTION_S` no longer says no compartment moves by a hundredth of a percent in 0.05 s. `tests/unit/test_chart_frame.py` has `test_the_hover_value_belongs_to_the_instant_it_prints`, using desflurane at 18% and 10 L/min near 6 s.

**Found by.** `PL-TBQS` reviewer replay on #578, findings r03 F4, r04 F2, r05 F4 and r06 F2, and `PL-ZWXD` entry 2. Checked against main on 2026-10-25 with `scripts/c_hover.py`, stepping 0.02 s.

**Route taken 2026-10-26: both of the brief's routes, combined.** Snapping every column to the 0.1 s clock grid would break the chart's one-pixel chord on the one- and two-minute axes, where a pixel is less than 0.1 s on a plot wider than 600 or 1200 px, and could double the column count. Printing the column's own instant would print digits such as 6m50.7383s. So `chart_time_base.grid_spacing_s` rounds the column spacing down onto whole hundredths of a second, and onto tenths wherever that adds at most a tenth more columns. The hover prints to the hundredth (`HOVER_INSTANT_RESOLUTION_S`). Every other drawn instant (a bound, a control event, a fork) is a step instant, so every printed instant is the drawn one. Rounding down keeps each chord within a pixel, except below 0.01 s spacing, which needs a one-minute axis wider than 6000 px. `test_a_bookmark_branch_and_its_parent_agree_at_every_column_they_share` counted shared columns at the old spacing, so its counts were re-measured (240 to 251).
