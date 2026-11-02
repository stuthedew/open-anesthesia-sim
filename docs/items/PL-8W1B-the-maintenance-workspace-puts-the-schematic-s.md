---
id: PL-8W1B
title: The Maintenance Workspace puts the schematic's 96 px containers beside the full-height concentration chart, so one tension stands at different screen heights in the two Views and a learner may read a fill level across against the chart's gridlines; align the containers to the plot's scale or caption them against that reading
status: untriaged
feature: presentation-safety
added: 2026-11-02
---

**Problem.** The Maintenance Workspace puts the schematic's 96 px containers beside the full-height concentration chart, so one tension stands at different screen heights in the two Views and a learner may read a fill level across against the chart's gridlines; align the containers to the plot's scale or caption them against that reading

**Where this came from.** The second blind review pass on `#1929` (`PL-PR1W`) named it as optional on 2026-11-02. Each container's label still prints its tension in text, and the schematic's caption says a height is a tension on the chart's 0 to 3 MAC scale, so no value is lost. The risk is a reading across the two Views. The containers are `_CONTAINER_HEIGHT` (96 px) tall in `app/qt_schematic.py` and sit at the top of their Area, while the plot beside them is several hundred pixels tall.
