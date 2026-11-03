---
id: PL-8W1B
title: The Maintenance Workspace puts the schematic's 96 px containers beside the full-height concentration chart, so one tension stands at different screen heights in the two Views and a learner may read a fill level across against the chart's gridlines; align the containers to the plot's scale or caption them against that reading
priority: P1
effort: M
status: ready
classes: defect, safety
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_schematic.py, src/anesthesia_sim/app/compartment_schematic.py, tests/integration/test_compartment_schematic_view.py
deferred-from: v0.7.0 - found after the gate cleared; each container's label prints its tension, so no value is lost
added: 2026-11-02
payoff: a learner cannot read a compartment's tension off the concentration chart's gridlines from the height of its container
verify: grep -rq 'def test_a_container_cannot_be_read_against_the_chart' tests/
---

**Problem.** The Maintenance Workspace puts the schematic's 96 px containers beside the full-height concentration chart, so one tension stands at different screen heights in the two Views and a learner may read a fill level across against the chart's gridlines; align the containers to the plot's scale or caption them against that reading

**Where this came from.** The second blind review pass on `#1929` (`PL-PR1W`) named it as optional on 2026-11-02. Each container's label still prints its tension in text, and the schematic's caption says a height is a tension on the chart's 0 to 3 MAC scale, so no value is lost. The risk is a reading across the two Views. The containers are `_CONTAINER_HEIGHT` (96 px) tall in `app/qt_schematic.py` and sit at the top of their Area, while the plot beside them is several hundred pixels tall.

**Why it matters.** The caption says each container fills against the chart's scale. In the Maintenance Workspace the chart stands beside the containers at full height. A learner who reads a fill level across to the chart's gridlines reads the wrong tension. The label under each container still prints the right value, so the risk is a misleading picture rather than a lost number. The safety-critical standard counts a misleading plot as a defect.

**Reproduced 2026-11-03, by reading; no screenshot.** `_CONTAINER_HEIGHT` is 96 in `src/anesthesia_sim/app/qt_schematic.py`. `scale_caption` in `src/anesthesia_sim/app/compartment_schematic.py` takes the top of the scale from the chart's own axis. `src/anesthesia_sim/data/workspaces/maintenance.json` puts the chart at full height with the schematic beside it.

**Done when.** In the Maintenance Workspace a container's fill cannot be read as a tension against the chart's gridlines. Either the containers share the plot's vertical scale, or the caption says their height is not on the gridlines' scale. Which of the two is a placeholder choice for the session that builds it. A test shows the chosen route.

**Generator check.** One-off. The fact is the vertical scale a drawn height stands for, when two Views draw one quantity at different heights. No head states it.

**Release question, put to the owner 2026-11-03.** v0.7.0 releases the schematic, and this item is a defect in how the schematic reads beside the chart. Whether the release waits for it is the owner's call, because the safety-critical standard reaches it. **Recommended:** release v0.7.0 with this item deferred, and take it in the first patch. The tension printed under each container is correct, so no number a learner reads is wrong. The risk is a misreading by eye in one Workspace.
