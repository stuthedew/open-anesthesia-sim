---
id: PL-SSBP
title: Add the chart time-base selector with 15, 30 and 60 minute scales plus Fit run
priority: P2
effort: M
status: ready
classes: ux, feature
feature: chart-readout
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-08-25
---

**Problem.** PL-012 decided the chart gains a user-selected time base and
built only its default "Fit run" mode. The selector itself does not exist.

**Why it matters.** The selected duration is the width of the visible window,
which is what makes a long run inspectable at a chosen resolution. It also
subsumes zoom: choosing 15 minutes on a 30 minute run is zooming, so this
removes the need for a separate zoom feature.

**Where.** `app/simulation_view.py`.

**Notes.** The full duration list is deliberately unsettled; 15, 30 and 60
minutes plus "Fit run" is the agreed starting set, and geometric spacing was
suggested so each step is a meaningful change rather than a nudge. "Fit run"
stays the default. The gridline interval must derive from the selected scale,
never be fixed.

**Done when.** The user can choose a time base from a list, the chart window
takes that width, and a run shorter than the selected scale still shows whole.
