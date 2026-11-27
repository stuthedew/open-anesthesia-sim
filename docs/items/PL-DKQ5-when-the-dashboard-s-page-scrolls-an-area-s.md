---
id: PL-DKQ5
title: When the dashboard's page scrolls, an Area's header and the row a View keeps above its scroll box move out of view while the View's values below them stay in view
priority: P1
effort: M
status: untriaged
classes: defect, safety
feature: interface-areas
touches: src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/pinned_heading.py
deferred-from: v0.7.0 - measured 2026-11-27 under PL-3NGZ: in every shipped Workspace at 1366 by 768, 1440 by 900 and 1920 by 1080, with one run or two, the page never scrolls an Area's pinned row or header out of view, so no shipped layout shows a value without them. It takes a layout the user arranged or a smaller window, and there each value still prints its own unit symbol with its run's and compartment's names in view. Deferred on that measurement on 2026-11-27 (ROADMAP.md § "Deferring to the next gate": the hazard is not live in any shipped Workspace); the coordinator did not put it to the owner, whose rule is that threads apply a sourced recommendation themselves
added: 2026-11-27
filed-pr: 2331
---

**Problem.** A window shorter than the dashboard scrolls the whole page, Areas and all (`SimulationView._page_scroll`). The page can then carry the top of an Area past the window's top edge while the lower part of its View stays in view. Two things go with it. The Area's header names the View and, while a Workspace pins a run, that run (`AreaFrame.pin_label`). The row a View keeps above its scroll box (`pinned_row`, `PL-26BZ`) holds the compartment schematic's "Model outputs — not measurements.", the tensions' unit and the amounts' unit with its 20 °C and 1 atm, and the wash-in plot's statement that it is modelled. So a user can see a tension or an amount with no unit, or a wash-in trace with no statement that it is modelled, on screen.

**What was measured** (`PL-3NGZ`, 2026-11-27, offscreen platform, the container's font). With the schematic as the only Area of a window 1400 by 400, two runs open, the page scrolls 182 px, and the schematic's Area starts 27 px from the page's top. Past about 71 px of page scroll the pinned row is above the window's edge while label lines are in view. `PL-3NGZ` made each run's heading follow a page scroll, so the run's name and the compartments' names stay in view; only the header and the pinned row are left. In the shipped Workspaces at 1366 by 768 and larger, the schematic's Area sits low enough that the page never scrolls its top out of view, so this needs a small window or a Workspace the user arranged.

**Direction.** The same rule `PL-3NGZ` applied inside an Area: a label stays at the top edge of the part in view (NUREG-0700 Rev. 3, guideline 1.5-15, p. 1-59: "General labels and row and column labels should remain along the top (or bottom) and left (or right) edges of the display"). One route is to lay the Area's header and pinned row over the top of its scroll box, as `PinnedHeadingSection` lays a run's heading over its rows, so they slide down while the page carries the Area's top away. A heading inside the View would then have to pin below them rather than at the box's top, so `in_view` would need to leave out the part they cover. The other route is to keep the page from scrolling an Area's top out of view at all. Either changes `AreaFrame`, which the corner drags and the too-small notice also use, so it wants its own pull request and a look at the Wash-in View as well as the schematic.

**Done when** a test scrolls the page of a short window through every position, with the schematic and the Wash-in View each at the top of the window, and no value is wholly in view without its Area's pinned row and header in view too.

**Generator check.** Re-entry of `PL-P83G` and `PL-3NGZ`: a qualifier in a different widget from the values it qualifies, inside a box that scrolls. `PL-3NGZ` closed the case inside an Area and for a run's heading on a page scroll; this is the one box left, the page itself. Three items on one mechanism; whether that makes a generator is triage's call.
