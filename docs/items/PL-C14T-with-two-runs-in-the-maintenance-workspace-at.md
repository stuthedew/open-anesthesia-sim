---
id: PL-C14T
title: With two runs in the Maintenance Workspace at 1366 by 768, the schematic's Area is held at 110 px, so under its pinned names and units it shows about one line of a label at a time and never a whole container
status: untriaged
feature: interface-design-review
touches: src/anesthesia_sim/app/view_registry.py, src/anesthesia_sim/data/workspaces/maintenance.json
added: 2026-11-27
filed-pr: 2331
---

**Problem.** With a branch open in the Maintenance Workspace at 1366 by 768, the compartment schematic's Area is held at its least height, 110 px under its header (`_LEAST_HEIGHT_PX` in `app/view_registry.py`). `PL-3NGZ` keeps the model-output statement and both units above the scroll box (44 px) and each run's name and compartment names over its rows (42 px), so about 24 px is left for rows. A user sees one line of a label at a time and never a whole container, so no fill can be read against its marks without scrolling it in pieces. Nothing shown is misleading: every value keeps its run, compartment and unit in view.

**What was measured** (`PL-3NGZ`, 2026-11-27, offscreen platform, the container's font). Holding the Area tall enough for the pinned row, a heading and one whole container (209 px with its header) made the page 119 px taller than the window, up from 47 px, and opened a page scroll of 23 px at 1536 by 864. After a branch the dashboard scrolls the page until the chart's plot is whole (`SimulationView._keep_chart_in_view`), which then put the top 51 px of the Concentrations View, its title and key, above the window's top. On `main` the same View's top sits 21 px below it. The patch that made the Area taller is the least-height change recorded in `PL-3NGZ`'s brief.

**Direction.** The Maintenance Workspace already overflows a 1366 by 768 window by 47 px once a branch is open, because the Parameters View holds a row of dials for each run whole and shares the right-hand column with the schematic. A fix gives the schematic room without growing the page: another arrangement of that Workspace for two runs, a schematic that draws its containers shorter when its Area is short, or a chart kept in view by its title rather than its plot's foot. Each changes what a user sees in a shipped Workspace, so it is a design round for the interface pass (`PL-9WDN`) and the project owner.

**Decided 2026-11-27.** The schematic keeps its 110 px least height for v0.7.0. Growing it put the concentration chart's title and key above the window after a branch, and NUREG-0700 Rev. 3 guideline 2.5.1.3-6 (p. 2-67) asks that displays not require excessive scrolling. The coordinator took this on the recommendation without putting it to the owner, under his rule that threads apply a sourced recommendation themselves.

**Done when** a test opens a branch in the Maintenance Workspace at 1366 by 768 and finds, for each run, a scroll position at which all six containers are whole under the run's heading, with the chart's title and key in view.

**Generator check.** A consequence of `PL-3NGZ`'s pinned heading meeting the Workspace's overflow at this size; a one-off.
