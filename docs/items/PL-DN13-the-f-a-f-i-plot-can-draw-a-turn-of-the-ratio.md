---
id: PL-DN13
title: The F_A/F_I plot can draw a turn of the ratio low or high where it falls between two chart columns
priority: P1
effort: M
status: ready
classes: defect, safety
feature: run-computed-one-way
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/run_series.py, src/anesthesia_sim/app/chart_time_base.py
added: 2026-11-21
payoff: a learner reading how far F_A/F_I fell after a dial change reads the true trough, not a column value above it
---

**Problem.** The F_A/F_I plot draws the alveolar fraction divided by the inspired fraction at each second that the chart draws (`DrawnWindow.wash_in_quotients` in `app/run_series.py`). Since `PL-BLZJ` (draw each peak between two columns), `SimulationController.drawn_window` also draws the second at which each compartment's fraction is highest or lowest between two columns. The ratio of two fractions can turn at a second where neither fraction does. After the dial is raised, the inspired fraction rises faster than the alveolar one, so the ratio falls for some seconds and then recovers. The raising is drawn, and the lowest ratio is drawn only if it falls on a column or on a second that one of the six fractions turns at.

**Why it matters.** A learner reading the F_A/F_I plot for how far the ratio fell after a dial change can read a value above the true trough. One case was measured on 2026-11-21, with the default sevoflurane patient and the dial raised to 6% at 600 s: the ratio falls from 0.775 at 600 s to 0.5878 at 635 s, and is 0.5899 eight seconds later and 0.622 at 688 s. So a column near the trough draws it within 0.002, and columns 43 s apart can straddle it. The largest gap over where the change falls has not been measured. The six concentration traces are not affected.

**What it changes.** `chart_time_base.extreme_seconds` already finds the seconds of a series' highest and lowest values between two drawn seconds. Giving it the ratio at each second of the window as a seventh series would draw the ratio's turns. The ratio has no value where the inspired fraction is below `WASH_IN_DENOMINATOR_FLOOR_FRACTION` (`app/wash_in.py`), so the search needs a rule for a stretch that holds such a second. Forming the ratio at every second of a twelve-hour window took about 3 ms in a first measurement on 2026-11-21. Measure the size of the gap first, on a dial raised between two columns at the twelve-hour time base.

**Found in.** `PL-BLZJ`, 2026-11-21.

**Done when.** Either a measurement shows that the drawn ratio misses a turn by less than the plot can show, or the plot draws the ratio's highest and lowest value between two columns and a test draws a trough that falls between two columns.

**Checked 2026-11-22.** In `app/controller.py`, the helper that chooses the drawn seconds still applies `extreme_seconds` only to the compartments' fraction series. `DrawnWindow.wash_in_quotients` forms the ratio only at the seconds chosen from them. At the freeze no turn between two columns was drawn for any series, so the ratio's case was present then. `PL-BLZJ` (#2180) drew the fractions' turns and not the ratio's.

**Generator check.** The fact misread is which series the chart draws a turn for between two columns. `PL-BLZJ` is the same mechanism for the six fractions. This item was filed by the pull request that closed `PL-BLZJ`, so it was found while that fix was built rather than after a shipped fix failed, and it is not recorded as a re-entry (`PL-C47M` has that rule).
