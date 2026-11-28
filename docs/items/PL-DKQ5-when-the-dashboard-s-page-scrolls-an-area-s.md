---
id: PL-DKQ5
title: When the dashboard's page scrolls, an Area's header and the row a View keeps above its scroll box move out of view while the View's values below them stay in view
priority: P1
effort: M
status: ready
classes: defect, safety
feature: interface-areas
touches: src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/pinned_heading.py
deferred-from: v0.7.0 - measured 2026-11-27 under PL-3NGZ: in every shipped Workspace at 1366 by 768, 1440 by 900 and 1920 by 1080, with one run or two, the page never scrolls an Area's pinned row or header out of view, so no shipped layout shows a value without them. It takes a layout the user arranged or a smaller window, and there each value still prints its own unit symbol with its run's and compartment's names in view. Deferred on that measurement on 2026-11-27 (ROADMAP.md § "Deferring to the next gate": the hazard is not live in any shipped Workspace); the coordinator did not put it to the owner, whose rule is that threads apply a sourced recommendation themselves
added: 2026-11-27
filed-pr: 2331
payoff: a user never sees a value in any View without its Area's header and the lines that state its unit and that it is modelled, whatever the window's size or arrangement
root-cause-of: PL-26BZ, PL-P83G, PL-3NGZ
generator: live - each fix kept a value's lines in view inside one box (PL-26BZ, PL-P83G, PL-3NGZ), and the page's own scroll was found the day PL-3NGZ closed; no test scrolls every box of every View
misread: Which lines a shown value needs in view with it, kept together by every box that scrolls
---

**Problem.** A window shorter than the dashboard scrolls the whole page, Areas and all (`SimulationView._page_scroll`). The page can then carry the top of an Area past the window's top edge while the lower part of its View stays in view. Two things go with it. The Area's header names the View and, while a Workspace pins a run, that run (`AreaFrame.pin_label`). The row a View keeps above its scroll box (`pinned_row`, `PL-26BZ`) holds the compartment schematic's "Model outputs — not measurements.", the tensions' unit and the amounts' unit with its 20 °C and 1 atm, and the wash-in plot's statement that it is modelled. So a user can see a tension or an amount with no unit, or a wash-in trace with no statement that it is modelled, on screen.

**Why it matters.** A tension or an amount read without the line that states its unit, or an amount without the 20 °C and 1 atm it is stated at, can be read in the wrong unit or taken as stated at body conditions. A trace read without the line saying that it is modelled can be taken for a measurement. `PL-3NGZ` made each Area keep these lines at the top of the part in view, following NUREG-0700 Rev. 3 guideline 1.5-15 as the Direction paragraph below quotes it. The page's own scroll is the one box where that rule does not yet hold.

**What was measured** (`PL-3NGZ`, 2026-11-27, offscreen platform, the container's font). With the schematic as the only Area of a window 1400 by 400, two runs open, the page scrolls 182 px, and the schematic's Area starts 27 px from the page's top. Past about 71 px of page scroll the pinned row is above the window's edge while label lines are in view. `PL-3NGZ` made each run's heading follow a page scroll, so the run's name and the compartments' names stay in view; only the header and the pinned row are left. In the shipped Workspaces at 1366 by 768 and larger, the schematic's Area sits low enough that the page never scrolls its top out of view, so this needs a small window or a Workspace the user arranged.

**A second instance: a sideways scroll of the page** (the review of `PL-3NGZ`
after it merged, 2026-11-27, offscreen platform). `pin_heading` moves a run's
heading up and down only. With two runs and a branch, a window 1280 px wide,
and the schematic swapped into the Maintenance Workspace's left Area, the page
scrolls 36 px sideways. At its end the first 22 px of "Run 2, at 10m of
simulated time" are left of the view while five of that run's six tensions
stay wholly in view. At 1000 px wide the page scrolls 126 px and hides the
first 112 px of the name, which takes "Run 2" off screen. At 1366 px the page
does not scroll sideways. So it takes, as above, a layout the user arranged and
a window smaller than the shipped sizes. The fix pins the heading's text at the
left edge of the part in view as well as at its top.

**Direction.** The same rule `PL-3NGZ` applied inside an Area: a label stays at the top edge of the part in view (NUREG-0700 Rev. 3, guideline 1.5-15, p. 1-59: "General labels and row and column labels should remain along the top (or bottom) and left (or right) edges of the display"). One route is to lay the Area's header and pinned row over the top of its scroll box, as `PinnedHeadingSection` lays a run's heading over its rows, so they slide down while the page carries the Area's top away. A heading inside the View would then have to pin below them rather than at the box's top, so `in_view` would need to leave out the part they cover. The other route is to keep the page from scrolling an Area's top out of view at all. Either changes `AreaFrame`, which the corner drags and the too-small notice also use, so it wants its own pull request and a look at the Wash-in View as well as the schematic.

**Done when** a test scrolls the page of a short window through every position, with each registered View in turn at the top of the window, and finds no value wholly in view without its Area's header and the View's pinned row in view too. The test covers every View rather than the schematic and the Wash-in View alone, so that a View given a pinned row later is checked too (triage, 2026-11-28, from the Generator check below).

**Generator check.** Re-entry of `PL-P83G` and `PL-3NGZ`: a qualifier in a different widget from the values it qualifies, inside a box that scrolls. `PL-3NGZ` closed the case inside an Area and for a run's heading on a page scroll; this is the one box left, the page itself. Three items on one mechanism; whether that makes a generator is triage's call.

**Generator check, answered at triage 2026-11-28.** This item is recorded as the head of one fact: which lines a displayed value must have in view with it, and whether every box that scrolls keeps them in view together. `PL-26BZ` (the wash-in View's "Modelled" line and its plot never on screen together inside their Area, closed 2026-11-14), `PL-P83G` (a share bar on screen while the lines naming its segments had scrolled out, closed 2026-11-27) and `PL-3NGZ` (the run's name and the units scrolled away inside the schematic's Area, closed 2026-11-27) each fixed one box. No head's `misread:` states the fact (`bin/docket generators --misread`, read 2026-11-28). The page's own scroll was found the day `PL-3NGZ` closed, so the mechanism is still producing, and the Done-when above covers every View.
