---
id: PL-L59K
title: Zoom the shipped Induction Workspace's concentration chart to the first 15 minutes, once the chart saves its own state
priority: P2
effort: S
status: ready
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

## What `PL-TH35` left for this item, 2026-10-19

The concentration chart's saved state holds only its `state_version` today
(`ConcentrationView.save_state` in `src/anesthesia_sim/app/views.py`). The
window the chart shows is not the chart's own. It is the dashboard's time
base, which every View is shown in each tick, and one frame per tick serves
every plot (`PL-9LNF`). A width chosen in one chart's control therefore moves
every chart. "The first 15 minutes" is also a fixed window from the start of
the case, not one of the following widths the time base offers.

So this item has to decide where a zoom lives before it can write one.
**Recommendation:** make the zoom the chart View's own state, as
`{"state_version": 2, "window_s": [0, 900]}`, and have the dashboard
assemble one frame per distinct window rather than one per tick. Charts
without a zoom keep sharing one frame, so the two plots still draw the same
instants. *Alternative:* save the time base with the Workspace. That is
cheaper, but it cannot express a fixed window and it would zoom every chart
in the Workspace, not one.

