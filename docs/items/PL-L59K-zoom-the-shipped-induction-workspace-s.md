---
id: PL-L59K
title: Zoom the shipped Induction Workspace's concentration chart to the first 15 minutes, once the chart saves its own state
priority: P2
effort: S
status: blocked
classes: feature
feature: interface-areas
touches: src/anesthesia_sim/data/workspaces/induction.json, tests/unit/test_layout_shipped.py
blocked-by: PL-TH35
added: 2026-10-18
payoff: the shipped Induction Workspace opens with its concentration chart on the first minutes of the case, where induction happens, rather than on the same window as every other Workspace
verify: grep -q '"concentration_chart": {' src/anesthesia_sim/data/workspaces/induction.json
---

**Problem.** `ROADMAP.md` v0.6.0 Required scope entry 13 asks for an
induction Workspace "with the concentration graph zoomed in". `PL-KXTL`
shipped `src/anesthesia_sim/data/workspaces/induction.json` with the
arrangement but without the zoom, because a zoom is the chart's own saved
state and the chart does not save any yet. What that state holds, and its
`state_version`, are the View contract's (`PL-TH35` Q4), so writing a zoom
into the shipped file now would decide the chart's state format ahead of the
item that owns it.

**Why it matters.** Without the zoom, the Induction Workspace opens on the
same time window as the others, and the first minutes, where the inspired,
alveolar and vessel-rich curves separate fastest, take a small part of the
chart's width. The project owner's own example of per-View state is a chart
"zoomed to the first fifteen minutes to read the wash-in" (`ROADMAP.md`
entry 11), which is the default proposed here.

**Done when.** `induction.json` keeps a saved state for its concentration
chart Area that shows the first 15 minutes of the case, in the form the chart
writes once `PL-TH35` has defined it, and a test in
`tests/unit/test_layout_shipped.py` reads that state back from the shipped
file. Whether 15 minutes is the right window is put to the project owner at
that point, since a learner sees it.
