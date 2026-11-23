---
id: PL-03YG
title: Searching the F_A/F_I ratio for peaks and troughs (PL-DN13) adds about 5 ms per run per frame on a 12-hour window (14.7 against 9.4 ms); measure a 24-hour window and decide whether the search needs arrays instead of Python lists
priority: P3
effort: S
status: ready
classes: perf
feature: run-computed-one-way
touches: src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/chart_time_base.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no learner sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-22
payoff: a 24-hour run does not make the chart lag behind the clock
---

**Problem.** Searching the F_A/F_I ratio for peaks and troughs (PL-DN13) adds about 5 ms per run per frame on a 12-hour window (14.7 against 9.4 ms); measure a 24-hour window and decide whether the search needs arrays instead of Python lists

**Why it matters.** The chart redraws while a run plays, and a run may last 24 hours. If the search grows with the window, a 24-hour window could make the chart lag behind the clock, which is a stale display.

**Done when.** The search's cost on a 24-hour window is measured and recorded here with the machine and date. If it adds more than the frame budget that `docs/INTERFACE.md` states for a redraw, the search runs on arrays and a test pins its result against the list version.

**Generator check.** A one-off: a cost measurement of one new search, not a misread fact.

**Reproduced 2026-11-23.** The 12-hour figures in the title are the measurement from `PL-DN13`'s branch; no 24-hour figure exists yet, which is the work.
