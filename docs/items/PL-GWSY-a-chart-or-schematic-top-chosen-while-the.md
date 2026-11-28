---
id: PL-GWSY
title: A chart or schematic top chosen while the preferences cannot be saved is said to be unsaved only in the agent cost View, so a Workspace without that View gives no sign that the top will reset at the next launch
status: untriaged
feature: chart-readout
touches: src/anesthesia_sim/app/views.py, src/anesthesia_sim/app/simulation_view.py
added: 2026-11-28
filed-pr: 2341
---

**Problem.** A chart or schematic top chosen while the preferences cannot be saved is said to be unsaved only in the agent cost View, so a Workspace without that View gives no sign that the top will reset at the next launch

**Found on 2026-11-28** while building `PL-7LZ7` (one axis top for every chart and schematic). The axis top is now a preference, saved in `preferences.json`. When a save fails, or saving is off because the file was written by a newer build or could not be checked, `SimulationView._change_preferences` puts the reason in the preferences notice. Only `AgentCostView` shows that notice. A reader who picks a top in a Workspace with no agent cost View is not told that the top lasts only until the application closes.

**Why it matters.** It is not a wrong value: the axis and the control show the top in force. It is a setting that silently does not persist, which `app/preferences.py`'s rule that no problem with the file passes without a notice is meant to prevent.

**What a fix needs to decide.** Where a reader who is not looking at the agent cost View learns that preferences are not being saved. One candidate is the same line under each "Axis top" control that names a refused saved top (`preferences.chart_ceiling_notice`). The other is one application-wide notice. The wording follows the sources `PL-VT87` recorded.

**Generator check.** A one-off: the first preference set outside the agent cost View.
