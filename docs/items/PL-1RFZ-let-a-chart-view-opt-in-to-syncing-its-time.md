---
id: PL-1RFZ
title: Let a chart View opt in to syncing its time window with every other opted-in chart in the Workspace, as Blender's Sync Visible Range does for its time-based editors
status: untriaged
feature: interface-areas
added: 2026-10-19
---

**Problem.** Once `PL-L59K` lands, each chart View owns its own time window,
so two charts in one Workspace can show different windows. The project owner
wants a later option that keeps chosen charts' windows in step, "similar to
blender's timeline areas" (project owner, 2026-10-19, in the thread that
answered `PL-L59K`'s question). Nothing in the area system offers that yet.

**What Blender does.** Read at source on 2026-10-19, `blender/blender` main,
`source/blender/editors/interface/view2d/view2d.cc` `view2d_sync` and
`source/blender/makesrna/intern/rna_space.cc` (property `show_locked_time`,
labelled "Sync Visible Range"). The option is a flag on each editor's own
view, `V2D_VIEWSYNC_SCREEN_TIME`, so it is opt-in per editor rather than a
global mode. When a view with the flag changes its horizontal range, Blender
copies `cur.xmin` and `cur.xmax` to every other view on the same screen that
also has the flag. Only time-based editors take part
(`view2d_area_supports_sync`: Dope Sheet, NLA, Sequencer, Clip and Graph).
The vertical range is never synced across Areas.

**Why it matters.** A reader comparing two charts stacked in one Workspace,
such as the concentration chart above the F_A/F_I plot, reads them against
one time axis. With independent windows they can drift apart and the
vertical alignment of instants is lost. An opt-in sync gives that alignment
back without taking away the per-chart window that the three-chart case
needs.

**Done when.** A chart View has a "sync visible range" setting, saved in its
own state. Every chart in a Workspace with the setting on shows the same time
window, and changing the window in any of them changes it in all of them. A
chart with the setting off keeps its own window. Synced charts draw one
shared frame, so they draw the same instants.

**Not in v0.6.0.** The project owner asked for it "later", so this item waits
to be placed.
