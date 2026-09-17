---
id: PL-4D1M
title: ROADMAP item 34 records Blender's window management but not the widget catalogue it implies, the named task workspaces the owner described, or the ordering that puts the layout mechanism before any widget
priority: P3
effort: S
status: done
classes: planning, docs
milestone: v0.4.26
touches: ROADMAP.md
added: 2026-09-15
closed: 2026-09-15
pr: 597
verify: python3 tools/doc_check.py check && grep -qF 'The widget catalogue is separate work, and the layout comes first' ROADMAP.md
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

**Closed 2026-09-15.** Item 34 now carries four paragraphs it did not have, and
a fifth decision the owner gave in the same exchange:

1. *Tiling by default, and break-out into a separate window rather than
   floating panels* - an area may be broken out into its own top-level window,
   itself tiled, which is what "floating" was taken to mean. Floating panels
   overlapping the tiled areas within a window are recorded as refused, with
   the covered-value reason, so the decision is not re-litigated from the word
   alone.
2. *The widget catalogue is separate work, and the layout comes first*, with
   the owner's own wording quoted and the refinement that the container
   abstraction is validated against two existing views rather than one.
3. *What a preset differs in, by example* - the induction and big-picture
   workspaces, and the central-graph default shape.
4. Planned-milestone **item 36** is the catalogue, filed as its own line so
   that scoping item 34 does not drag it along.

`PL-JFXG` closed alongside as item 37. `PL-WLWY` stays open and is named from
item 34: break-out sharpens its question rather than answering it, because a
broken-out window can be dragged over the window carrying the minimum display.
