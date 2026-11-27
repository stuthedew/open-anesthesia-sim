---
id: PL-YSFX
title: While two runs are compared, each run's playback selector reaches a screen reader as "Playback" alone, and in the Induction Workspace both plots' window selectors are "Time base" alone, so a screen-reader user cannot tell which run or plot a selector sets
priority: P3
effort: S
status: untriaged
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/views.py, tests/integration/test_keyboard_focus.py
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it; each selector is named and only the run or plot it sets is missing, so the release waits only on the owner test drive (filed 2026-11-27)
added: 2026-11-27
filed-pr: 2333
payoff: a screen-reader user who reaches a playback or time base selector hears which run or plot it sets
---

**Problem.** `PL-RK9Z` named every control from the label shown beside it, and added which one it is where two controls in one form share a label, such as "Add, time bookmark" and "Add, MAC target". It did not do this for controls that repeat across runs or Views. While two runs are compared, each run's playback selector is named "Playback" (`RunView._lay_out_transport_row`). In the Induction Workspace the concentration chart's and the wash-in plot's window selectors are both named "Time base" (`views.py`, `label_control(time_base_name, self._window.selector)`). A screen-reader user moving through the controls hears the same name twice and cannot tell which run's playback rate, or which plot's window, the next key press changes. The run's list of control changes is already named with its run, by `compared_panel_heading` in `RunView`, so these two are the gap.

**Why it matters.** WCAG 2.2 SC 2.4.6 (Headings and Labels, Level AA) reads "Headings and labels describe topic or purpose", and SC 4.1.2 asks that each control's name can be programmatically determined (read 2026-11-27). A sighted user sees which run's panel or which plot a selector sits under. A screen-reader user gets only the name. I suggest P3, because each selector is named and only the run or plot is missing.

**Approach.** Add the run's name to the playback selector's accessible name while two runs are drawn, as `compared_panel_heading` adds it to the control timeline's heading, and add the plot's heading to each window selector's name. Keep the shown label at the start of each name, which the Understanding document for SC 2.5.3 (Label in Name) calls best practice: "Playback, Run 2", "Time base, wash-in". The names are written by `dashboard_frame` with the other control names, so the interface wording test approves them.

**Done when.** A test with two compared runs reads two different names for the two playback selectors, and a test of the Induction Workspace reads two different names for the two window selectors.

**How it was found.** The first independent review of `PL-RK9Z`'s change, 2026-11-27, as an optional finding.
