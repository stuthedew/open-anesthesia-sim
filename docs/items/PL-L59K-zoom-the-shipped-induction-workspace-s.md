---
id: PL-L59K
title: Zoom the shipped Induction Workspace's concentration chart to the first 15 minutes, once the chart saves its own state
priority: P2
effort: M
status: done
classes: feature
feature: interface-areas
milestone: v0.5.42
touches: src/anesthesia_sim/app/, src/anesthesia_sim/data/workspaces/induction.json, tests/integration/test_view_contract.py, tests/integration/test_layout_adapter.py, tests/integration/test_run_surfaces.py, tests/integration/test_simulation_view.py, tests/integration/test_dark_appearance.py, tests/unit/test_dashboard_frame.py, tests/unit/test_layout_shipped.py, tools/contrast_check.py, docs/MODEL.md, docs/ARCHITECTURE.md, README.md, tests/unit/test_supported_range_edges.py, tests/integration/test_qt_rendering.py, tests/integration/test_workspace_tabs.py
blocked-by: PL-TH35
added: 2026-10-18
closed: 2026-10-19
pr: 1650
payoff: the shipped Induction Workspace opens with its concentration chart on the first minutes of the case, where induction happens, rather than on the same window as every other Workspace
verify: grep -q '"time_base_s": 900.0' src/anesthesia_sim/data/workspaces/induction.json
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

**The question put to the project owner.** Should a chart's time-window control
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

**Answered** (project owner, 2026-10-19, ratified, over one shared window
saved per Workspace): only that chart. In his words, "Only the chart but want
to allow later to allow chart time windows to sync similar to blender's
timeline areas". So each chart View owns its time window and saves it, and
the F_A/F_I plot gets the same control. This reopens `PL-TH35` Q2 and Q7 for
the time base only, on the evidence recorded above: roadmap entry 11 and this
item. The compartment selection stays shared. The later sync is `PL-1RFZ`,
filed from his answer, and this build leaves room for it: charts at the same
window share one frame, which is the same grouping a synced set of charts
would use.

**Build order.** `PL-7Z84` (`#1614`, run identity) changes
`app/views.py`, `app/simulation_view.py` and `induction.json` and waits on the
project owner's read. This build starts on top of it and opens its pull
request after it merges.

## Built 2026-10-19

**How it works.** Each chart View now holds its own time window.
`app/views.py`'s `_TimeWindow` reads the window from the View's saved state,
sets it from the View's own time-base control, and saves it as
`{"state_version": 2, "time_base_s": 900.0}`, or `"fit"` for "Fit run". Each
View tells the adapter which frame it draws through a new contract member,
`View.frame_request`, which returns the window and the plot width. It
replaces `frame_width_px`. The dashboard assembles one frame for each distinct
window, sampled at the widest plot that asks for it, so charts at one window
still share a frame. The adapter hands each View the frame for its own window.
`ViewRequests.frame` replaces `ViewRequests.time_base`: a View that changes
its window asks for a frame at once. The dashboard no longer holds a time
base, and its `time_base_changed` signal is gone, since no shared control is
left to follow it.

**What moved with it.** Three lines depend on the window, so each chart now
writes them from its own frame, one line per run, instead of showing a copy
from the run. The concentration chart writes the off-scale notice. The F_A/F_I
plot writes the wash-in state line, whose suffix counts the stretches its own
window left undrawn. Both charts write the count of control changes in their
window that they could not mark. That count used to sit in the run's
control-change panel as "N not marked on the chart", which no longer has a
single answer once two charts show different windows. `RunView.refresh` now
takes only the snapshot, and `RunView` no longer builds the off-scale or
wash-in lines. The F_A/F_I plot gains the time-base control and the caption of
the window in force, as the recommended option said.

**Placeholders decided here** (project owner's rule of 2026-10-18 on look,
wording and placement). The unmarked-changes line reads "N control change(s)
in this window not marked" and sits under the off-scale lines on the
concentration chart and under the state lines on the F_A/F_I plot. The F_A/F_I
plot's control sits in its heading row, as the concentration chart's does.

**Saved state.** A version 1 chart state held no setting, so a chart reads it
as "Fit run" without a notice: nothing saved is lost. A version 2 state whose
window is not one the selector offers, such as 60 s or `true`, starts the chart
on "Fit run" and shows the unreadable-state notice.

**What a learner sees, and when.** `PL-2KXB` (`#1653`, the Workspace tab
strip) merged while this pull request waited, and its tab switch loads each
Workspace's saved View state. So the Induction tab opens its chart on 15
minutes. `tests/integration/test_workspace_tabs.py`'s
`test_the_induction_tab_opens_its_chart_on_the_15_minute_window` clicks the
tab and checks the frame the chart draws. `tests/integration/test_view_contract.py`
builds the chart from the shipped state and checks that it asks for the
15-minute window. `#1653` also lets a Workspace pin one run. So when a
Workspace is pinned, this branch assembles each window's frame from the
pinned run alone, as `#1653` did for its single frame.

**Whether a zoomed chart mentions an excursion outside its window**
(project owner, 2026-10-19, ratified, over keeping the note on a chart that
does not draw the clipped trace). He saw three screenshots: the whole-run
chart with its off-scale note, the 15-minute chart without it, and a mock of
the 15-minute chart keeping it. He answered "agree with recs and merge". So
each chart's advisories describe only what that chart draws.

**Tests.** `test_each_chart_names_only_the_clipped_traces_its_own_window_shows`
is the regression test for the moved advisory. A case at 8% sevoflurane for
10 minutes and then 0% for 25 leaves the circuit trace clipped early in the
run. The chart that fits the run names it, and a 15-minute chart, whose window
starts after the excursion, does not.
