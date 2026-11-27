---
id: PL-3NGZ
title: On a laptop screen the compartment schematic's labels can be in view while the lines that qualify them have scrolled away: the run's name while two runs are compared, the line saying what the shares are of while a container is above the scale, and the tension's unit
priority: P1
effort: M
status: done
classes: defect, safety
feature: presentation-safety
touches: docs/ARCHITECTURE.md, docs/INTERFACE.md, docs/VERIFICATION.md, docs/items/PL-49D5-with-ventilation-stopped-and-the-dial-lowered.md, src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/compartment_schematic.py, src/anesthesia_sim/app/pinned_heading.py, src/anesthesia_sim/app/qt_schematic.py, src/anesthesia_sim/app/stylesheets.py, src/anesthesia_sim/app/views.py, tests/integration/approved_interface_strings.json, tests/integration/simulation_view/test_simulation_view_foreground.py, tests/integration/test_compartment_schematic_view.py
added: 2026-11-27
closed: 2026-11-27
pr: 2331
filed-pr: 2326
payoff: a user comparing two runs on a laptop never sees a run's tensions, amounts or shares without its name, the tension's unit or what the shares are of
tests: tests/integration/test_compartment_schematic_view.py::test_no_value_is_in_view_without_its_run_and_compartment_at_any_scroll_position
reenters: PL-P83G
---

**Problem.** On a laptop screen the compartment schematic's labels can be in view while the lines that qualify them have scrolled away: the run's name while two runs are compared, the line saying what the shares are of while a container is above the scale, and the tension's unit

**Why it matters.** A label read without its qualifier can be misread. While
two runs are compared, a learner can see one run's tensions, amounts and
shares with neither run's name on screen, and the two runs can differ a lot:
in one scroll position a reviewer saw "Circuit 44%" and "Fat 4%" for the
first run while the second run read circuit 79% and fat under 1%. While a
container is above the scale, the line that says the shares are of all the
agent at this instant can be below the Area's edge. The tension's unit, % of
1 atm, is printed only in the scale caption, which scrolls on this screen.

**What was measured** (the review of `PL-8PL4`, 2026-11-27, Maintenance
Workspace at 1366 by 768, offscreen platform font):

1. With a branch open, the schematic's Area is about 110 px tall and scrolls.
   For each run there are about 24 scroll positions, of 636, at which its
   labels and bars are wholly in view and no run name is. The bars were in
   view without their compartment names at 142 positions; the single bar on
   `main` before `PL-8PL4` was in view without its key at 97. With one run
   neither happens.
2. With one run and the circuit above the scale (sevoflurane at 8%), two of
   three measurements found the share caption below the Area's edge, and one
   found it in view. `docs/INTERFACE.md` says it can scroll.
3. `PL-8PL4` put the share caption directly under the containers, so with
   one run and nothing above the scale it is in view at every screen size
   the lesson test checks.

[superseded 2026-11-27: the triage pass placed this item on v0.7.0's frozen list, so it is fixed now rather than in `PL-9WDN`; see **Placed 2026-11-27** below] **Direction.** Each qualifier belongs where it cannot scroll away from the
values it qualifies: inside the canvas beside the labels, or in a line that
stays at the top of the Area while the content scrolls. That is a layout
decision for item 33's interface pass (`PL-9WDN`), which writes the design
language first.

**Done when** no scroll position at 1366 by 768 shows a run's labels without
its name while runs are compared, or a share without what it is a share of,
and a test scrolls through every position to check it.

**Placed 2026-11-27 (triage).** Classed `safety`, because `CLAUDE.md`'s safety-critical standard counts a value shown without its run, its unit or what it is a share of as a presentation failure. The hazard is live on `main` at `f653c1eb`, where `PL-8PL4` merged as #2326 with the measurements above taken on its branch. A `safety` entry with a live hazard re-enters the current gate and cannot be deferred (`ROADMAP.md` § "Deferring to the next gate"), so this item joins v0.7.0's frozen list and is fixed before the release rather than in `PL-9WDN`'s interface pass. Where each qualifier sits is a placement choice. The building session picks one of the two the direction names, records it as a placeholder, and `PL-9WDN`'s design language may restyle it later.

**Generator check.** A re-entry of `PL-P83G` at sibling sites. Both are a qualifier drawn in a different widget from the values it qualifies, inside an Area that scrolls, so the two can separate. `PL-P83G` fixed the share bar's segment names. The run's name, the share caption and the tension's unit are the same mechanism, and this item was filed by the same pull request (#2326). Two items are not a generator.

**Done 2026-11-27.** Each run's schematic is now a `PinnedHeadingSection` (new `src/anesthesia_sim/app/pinned_heading.py`). Its heading is laid over the top of its column of rows, and `ViewScroll` moves the heading to the top of the section's part in view after each scroll and resize. That is how a list's section headers stay pinned while the list scrolls (Apple, SwiftUI documentation, "Grouping data with lazy stack views", § "Keep important information visible", read 2026-11-27, https://developer.apple.com/documentation/swiftui/grouping-data-with-lazy-stack-views), and how a table keeps its column headers in view (Stanford University IT, 'Fixed "Sticky" Table Header: Advanced Table Design', read 2026-11-27, https://uit.stanford.edu/accessibility/techniques/websites/website-tables/table-sticky; Adrian Roselli, "Fixed Table Headers", read 2026-11-27, https://adrianroselli.com/2020/01/fixed-table-headers.html). The heading is drawn on the panel's colour over the rows, so a row is either below it and seen, or under it and hidden. Of the two directions the brief named, this is the line that stays at the top of the Area.

The heading holds three things: the line naming the instant and, while runs are compared, the run; the share caption; and the six compartments' names, each over its own container (`ContainerNames`). The names were a fourth qualifier that could scroll away from its values: the measurement above found the bars in view without their names at 142 positions. Moving them into the heading is the table's column-header pattern, so the canvas's labels keep three lines: tension, amount and share. The disclaimer "Model outputs — not measurements." and a new line, "Tensions are in % of 1 atm.", moved into the View's pinned row (`PL-26BZ`), above the scroll box, so both are in view at every position. That also closes the case where the disclaimer itself scrolled away. NUREG-0700 Rev. 3 supports each placement (O'Hara, Brookhaven National Laboratory for the U.S. Nuclear Regulatory Commission, July 2020; full text from https://www.osti.gov/servlets/purl/1644018, read 2026-11-27). Guideline 1.5-15, p. 1-59, says that in a scrollable display "General labels and row and column labels should remain along the top (or bottom) and left (or right) edges of the display", and that "all labeling information should be preserved." The run's name is each section's general label and the compartments' names are its column labels, so both stay at the section's top edge. Guideline 1.2.2-4, p. 1-17, says that "when cells have the same measurements, the units of measurement should be part of row or column labels." Every tension has the same unit, so the full unit is stated once, in a general label at the View's top edge, and each tension keeps its "%". `PL-9WDN`'s interface pass may restyle these within the same guidelines.

What it costs: the heading is two lines tall, 42 px under the offscreen font. With two runs in the Maintenance Workspace at 1366 by 768, the schematic's viewport is 81 px, so at most two of a container's three label lines show at once below the heading. Each line carries its unit, and its compartment's name is over it.

Regression test, run against `origin/main` at `8f404cfa` with a variant of `test_no_value_is_in_view_without_its_run_and_compartment_at_any_scroll_position` that reads the run's name line as its heading and checks the share bars alone, because `container` and `label_line` are public only since this change: all three cases fail. Two runs fails with "AssertionError: (150, 'Run 1, at 10m of simulated time')", and both one-run cases with "AssertionError: (36, 'At 10m of simulated time')".

Documents checked: `docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts and share bar assert" (the disclaimer's row, the share caption's place, the heading paragraph and the note for developers), § "Naming the run in a comparison" (item 6); `docs/ARCHITECTURE.md` (the package map: `pinned_heading.py` added, `qt_schematic.py` updated); `docs/VERIFICATION.md` (the hazard row on reading one run's value as the other's gains the new test); `README.md`, `docs/MODEL.md` and `docs/PARAMETERS.md` (none says where the schematic's heading or labels sit, unchanged).
