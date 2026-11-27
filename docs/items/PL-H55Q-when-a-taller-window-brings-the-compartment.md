---
id: PL-H55Q
title: When a taller window brings the compartment schematic's rows into view without a scroll, each run's name stays where it was, so that run's values can show with no name over them
priority: P1
effort: S
status: untriaged
classes: defect, safety
feature: presentation-safety
touches: ROADMAP.md, docs/ARCHITECTURE.md, docs/INTERFACE.md, docs/VERIFICATION.md, docs/items/PL-C14T-with-two-runs-in-the-maintenance-workspace-at.md, docs/items/PL-DKQ5-when-the-dashboard-s-page-scrolls-an-area-s.md, src/anesthesia_sim/app/pinned_heading.py, tests/integration/test_compartment_schematic_view.py
added: 2026-11-27
---

**Problem.** When a taller window brings the compartment schematic's rows into view without a scroll, each run's name stays where it was, so that run's values can show with no name over them

**What was seen** (the review of `PL-3NGZ` after it merged, 2026-11-27,
offscreen platform). In the Maintenance Workspace at 1366 by 600 with a branch
open, the page was scrolled to its end, the schematic's box was scrolled until
run 1's tension line stood under its heading, and the page was scrolled back
to its top. The schematic's Area was then below the window, so each heading
stood at its section's top. Making the window 810 px tall shrank the page's
scroll range and brought the box back into view, with no scroll of the page or
of the box. Each heading stayed where it was, above the box's top edge, while
run 1's six tensions were in view below it. The next drawn frame moved the
heading, so a paused run showed the values with no name over them until
something else moved it.

**Why.** `pin_on_scroll` moved the headings only when a scroll bar's value
changed. A change of a scroll bar's range, which a resize makes, moved the
page's widget into view without any such signal.

**Fix.** `pin_on_scroll` in `app/pinned_heading.py` also moves the headings
after each change of either scroll bar's range.
`test_a_run_heading_follows_a_taller_window_that_brings_its_run_into_view`
fails without the change and passes with it, with the container's font and
with DejaVu Sans, which CI draws text in.

**Gate.** Placed on v0.7.0's frozen list beside `PL-3NGZ`, which it completes:
`PL-3NGZ` is done when no run's values are in view without its name, and this
case broke that. `ROADMAP.md` § "The gate is a snapshot, not a moving target"
puts a finding that completes a frozen item on that item's gate.

**Done when.** A change of what the page or an Area can scroll moves each run's
heading over the part of its section in view, as a scroll does.
