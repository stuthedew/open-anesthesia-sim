---
id: PL-P83G
title: With two runs compared in the compartment schematic, the second run's share bar can be on screen while the lines naming its segments are scrolled out of its Area
priority: P2
effort: S
status: done
classes: defect, ux
feature: schematic
touches: src/anesthesia_sim/app/qt_schematic.py
added: 2026-11-26
closed: 2026-11-27
pr: 2326
filed-pr: 2325
tests: tests/integration/test_compartment_schematic_view.py::test_each_share_bar_is_painted_to_its_share_on_one_scale_under_its_own_label
---

**Problem.** With a branch open, the compartment schematic stacks one schematic per run, and the View is taller than its Area at every common screen size, so it scrolls inside the Area. Each schematic draws its share bar and, under it, the lines that name each segment in text. The second run's bar sits in the middle of the View, so the Area's lower edge can fall between that bar and its lines, and the bar is then on screen with nothing to name its segments. Measured on 2026-11-26 in Maintenance, scrolling 2 px at a time: 32 to 49 scroll positions show the bar without its lines, at 1366 by 768, 1440 by 900, 1536 by 864 and 1920 by 1080, in both test fonts. `main` at 971a9cb9 had the same fault at 1920 by 1080 with a branch open, so it predates `PL-YS8M`. `PL-YS8M` moved the bar and its lines above the containers, which removed the fault with one run.

**Why it matters.** `docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts and share bar assert" requires each segment to be named in text, never by colour alone. A reader comparing runs who sees only the bar must tell muscle from fat by colour, and two of the six trace colours are hard to separate (`.claude/rules/ui-color.md`, judgment 3).

**Generator check.** None found: it is one View's row order meeting the scroll box that every View gets (`PL-CBYS`).

**Done when.** Wherever any part of either run's share bar is in view, its lines are wholly in view, at the common screen sizes with a branch open. `test_the_share_bar_is_never_on_screen_without_the_lines_that_name_its_segments` in `tests/integration/simulation_view/test_simulation_view_page.py` covers one run and should gain the branched case. Routes to weigh: draw the segment names inside or beside the bar itself, or keep each run's bar and lines in a row that its Area pins, as the wash-in View pins its "modelled" line (`PL-26BZ`).

**Closed 2026-11-27 by `PL-8PL4`, which removed the bar this item is about.**
The project owner chose to replace the single divided bar with a share line
and a short bar under each container's label. Each bar now holds one
compartment and stands in that compartment's column, under its container and
its name, so no bar has segments for a reader to tell apart by colour, and no
separate lines exist to scroll away from it. With two runs compared, each run's
bars are in its own schematic's canvas, under the line that names the run.
`test_the_share_bar_is_never_on_screen_without_the_lines_that_name_its_segments`
went with the bar. `test_each_share_bar_is_painted_to_its_share_on_one_scale_under_its_own_label`
checks that each bar stands inside its own container's column.
