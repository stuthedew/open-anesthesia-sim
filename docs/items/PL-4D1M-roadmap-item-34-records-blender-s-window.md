---
id: PL-4D1M
title: ROADMAP item 34 records Blender's window management but not the widget catalogue it implies, the named task workspaces the owner described, or the ordering that puts the layout mechanism before any widget
status: untriaged
added: 2026-09-15
---

**Problem.** ROADMAP item 34 records Blender's window management but not the widget catalogue it implies, the named task workspaces the owner described, or the ordering that puts the layout mechanism before any widget

**Why it matters.** Item 34 already records the layout half well: tiling rather
than floating, areas each hosting one view, workspaces as task-geared tabs the
user reorders and saves, the Apache-2.0/GPL constraint on reading Blender's
source, and the Qt primitives. What the project owner described on 2026-09-15
adds four things it does not carry, and each is intent that would otherwise be
rediscovered at scoping time.

1. **The widget catalogue is separate work from the layout mechanism**, and the
   owner wants the mechanism first: "So I think the layout part with the
   adding, resizing, removing windows etc. and then telling the program what
   should be in that window ... is the functionality I want to end up with.
   Then separately want to work on widgets." Item 34 says an area "holds one
   view" and never says what the views are or that they are their own track.
2. **Named task workspaces, by example**: an induction workspace with the graph
   zoomed in, a big-picture maintenance workspace, and user-created ones beside
   the shipped defaults. Item 34 has "task-oriented layout presets" in the
   abstract and no example of what a task preset differs in.
3. **A default layout shape**: a central graph of the compartments with widgets
   arranged around it, itself customizable.
4. **Candidate widgets the owner named**, which are what the catalogue would be
   scoped from: a Gas Man-style schematic compartment view (already
   planned-milestone item 27), an F_A/F_I chart (already drawn today, as a
   section rather than a movable view), an opioid/hypnotic isobologram
   (`PL-JFXG`, on the roadmap nowhere), and overlays.

**Not a scoping round.** Item 34 stays unspecified per this section's own rule;
this adds intent to it and files the widget track beside it, so that scoping
later starts from what the owner actually asked for rather than from the
2026-09-12 note alone.

**Done when.** `ROADMAP.md` item 34 carries the four points above, and the
widget catalogue is a planned-milestone line of its own naming the mechanism
dependency rather than being folded into item 34's scope.
