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


## Set aside for the project owner's answer, 2026-10-19

The build thread that picked this item up found two recorded decisions that
disagree about who owns a chart's time window, and this item cannot be built
until one of them gives way.

- `ROADMAP.md` § "v0.6.0 - the layout is the reader's", Required scope
  entry 11, puts the time window in "per-View-instance state". Two charts in
  one Workspace hold it independently. Its example is the project owner's own
  case of 2026-09-17: three charts in one Workspace, one of them "zoomed to the
  first fifteen minutes to read the wash-in". Blender keeps zoom in each
  editor's own regions, so it agrees (`docs/interface-provenance.md`, the
  paragraph on what `ED_area_newspace` keeps).
- `PL-TH35` Q2 and Q7 (project owner, 2026-09-27, ratified, over a View that
  owns its own time base) made the time base shared state. The dashboard owns
  it, every chart shows it, and one frame per tick serves every plot
  (`PL-9LNF`). That is what is built.

**Settled in this round, whichever answer comes.** The zoom is the ladder's 15-minute
rung following the run, not a fixed window of 0 to 900 s. With the 2%
headroom, a 15-minute following window shows exactly the first 15 minutes
until the newest sample reaches 882 s, and then slides so that the newest
sample stays on the plot. A fixed window would carry the current values off
the right edge after 15 minutes with nothing saying so. That is the
stale-display failure `CLAUDE.md`'s display standard names, and panning away
from the live edge with a statement that it has happened is `PL-Z7LY`'s. The
15-minute width is the narrowest the selector offers and the project owner's
own example, so it is taken as the default here. It is a placeholder under the
project owner's rule of 2026-10-18 on look, wording and placement, because the
current values stay on screen at any width.

**One correction to the brief.** Under "Fit run", the default, the first
minutes of a case already fill the chart: a 30-second case is drawn on the
60-second rung. The zoom matters when a reader's wider choice would otherwise
carry into the Induction Workspace, and because a fixed width keeps each
trace's slope proportional to its rate (`PL-012`), where "Fit run" rescales at
1, 2, 5 and 15 minutes.

**Decision needed.** Should a chart's time-window control
change only that chart, or every chart on screen?

- **Only that chart (recommended).** Each chart View saves its own window as
  `{"state_version": 2, "time_base_s": 900}`, or `"fit"` for "Fit run", and
  the F_A/F_I plot gets the same control. The dashboard assembles one frame
  per distinct window, so charts at the same window still draw the same
  instants. This is what entry 11 and Blender describe, and it makes the
  three-chart case possible. The cost is that two stacked charts can show
  different windows, so their time axes stop lining up. Each still states its
  own window on its axis, and the F_A/F_I plot gains the caption of the window
  in force that the concentration chart already has.
- **Every chart.** The time base stays shared, and the Workspace saves it, so
  switching to the Induction Workspace sets every chart to 15 minutes. It is
  cheaper and keeps stacked plots aligned. It cannot show the three-chart case,
  and entry 11's sentence would have to be rewritten to match.
