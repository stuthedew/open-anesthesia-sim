---
id: PL-H100
title: On a Mac, the Maintenance Workspace at 1366 by 768 leaves each container's share line cut through at the schematic's lower edge and its share bar out of view, because macOS's system font draws taller lines than the Linux fonts the tests use; the values show whole only from a 788 px tall window
priority: P1
effort: M
status: done
classes: defect, safety
feature: interface-matches-its-spec
touches: src/anesthesia_sim/data/workspaces/maintenance.json, src/anesthesia_sim/app/qt_schematic.py, tests/integration/simulation_view/test_simulation_view_page.py, docs/INTERFACE.md
added: 2026-11-28
closed: 2026-11-28
pr: 2350
payoff: A user on a Mac with a 1366 by 768 window sees each container's tension, amount and share whole in the Maintenance Workspace, never a value cut through at the schematic's edge.
tests: tests/integration/simulation_view/test_simulation_view_page.py::test_the_maintenance_schematic_leaves_room_for_macos_text_at_1366_by_768
---

**Problem.** On a Mac, the Maintenance Workspace at 1366 by 768 leaves each container's share line cut through at the schematic's lower edge and its share bar out of view, because macOS's system font draws taller lines than the Linux fonts the tests use; the values show whole only from a 788 px tall window

**Measured 2026-11-28** on a GitHub macOS runner (image `macos-26-arm64`, macOS 26.7.2, PySide6 6.12.0), at `a2dd5548` and `2d10ae96`, which add nothing to `main` at `b893e699` but a throwaway probe. Runs 46091853273 and 46092465778 of the `mac-test-drive` workflow on branch `claude/project-thread-m4oy26` hold the logs. The probe built the dashboard with `open_dashboard`, opened Maintenance, pressed Start and advanced one run to 1 h. It ran under Qt's `cocoa` platform, so the app drew with the platform's own style (`macos`) and font (`.AppleSystemUIFont`, 13 pt).

1. **The runner's screen is 1024 by 768, and macOS shrinks a shown window to fit it.** The first run asked for 1600 by 1000 and got 1169 by 645. Every later measurement marks the window `Qt.WidgetAttribute.WA_DontShowOnScreen` before showing it, which keeps the size asked for and still lays text out with the platform's font and style.
2. **At 1366 by 768 the schematic's canvas is 20 px taller than the part of its Area in view.** The Area's viewport is 742 by 252, and the canvas starts 80 px down it and is 192 px tall. So the third label line under each container ("13% of agent" for Circuit) is cut through at the viewport's lower edge, and the share bars are below it. `test_each_shipped_workspace_shows_its_lesson_whole_with_one_run[Maintenance-1366-768]` fails there with "the containers and shares is not wholly on screen in Maintenance". It passes on Linux CI.
3. **The values show whole from a window 788 px tall** at widths 1366, 1440, 1470 and 1512, and from 824 px at 1280. Every label, unit and name fits its box at 1366 by 768, 1470 by 850, 1512 by 917 and 1728 by 1052, at a scale of 1 and of 2 (`QT_SCALE_FACTOR=2`, standing in for a Retina screen). Only the vertical fit fails.
4. **The style is not the cause.** With `app.setStyle("Fusion")` and the same macOS font, the values show whole from 780 px at widths 1366 to 1512, so 1366 by 768 is still 12 px short. The macOS font's lines are 16 px where the Linux test fonts' are 15, and the schematic stacks several of them above and under the containers.
5. **What a maximized window loses on that Mac.** A shown window's title bar was 32 px, the menu bar 31 px and the Dock 63 px (screen 1024 by 768, available 0, 31, 1024, 674). So a maximized window 788 px tall needs a screen about 914 px tall with the Dock showing. A notched MacBook's menu bar was not measured.

**Why it matters.** `docs/INTERFACE.md` says the Maintenance Workspace shows the containers and the share caption whole at 1366 by 768 with one run. On a Mac it does not, and a value line cut through at the lower edge can look like another value, the hazard `PL-GWTR` records for the upper edge. The pinned run heading keeps every value beside its run and compartment (`PL-3NGZ`), and a scroll of the Area shows the rest.

**Checked 2026-11-28** (`PL-GWTR`, pull request #2346). The schematic now
paints a label line or a share bar only while it is whole in view. So on a Mac
at 1366 by 768 the third label line under each container is hidden rather than
cut through, and no cut value can be misread there. This follows from the
painting rule, which the Linux tests check at every scroll position; it was not
run on a Mac. The share lines and bars are still out of view until the Area is
scrolled, so the Workspace still fails `docs/INTERFACE.md`'s requirement on a
Mac, and this item's fix is still needed.

**Where to start.** The fix needs about 20 px of height at 1366 by 768 in the macOS font, taken from the schematic's own rows or given by the Workspace's shares, without breaking the concentration chart's least height. Prove it on macOS, which needs `PL-2Y1L` (a macOS test job) or the same throwaway probe, because the Linux tests cannot see this.

**Decided 2026-11-28.** Fix it before v0.7.0 is cut (project owner, 2026-11-28, over the session's recommendation to cut now and fix it in a later release). The owner chose on a decision card in the test-drive thread, after seeing both Mac screenshots.

**Generator check.** The cause is that every layout test runs in a Linux font and style, so a fit that holds there is never checked in macOS's system font. `PL-2Y1L` records that cause. This is the first item on it, and one item is not a generator.

**Done when.** In the Maintenance Workspace at 1366 by 768 with one run, the schematic's canvas and its share caption are wholly in view under Qt's `cocoa` platform on a GitHub macOS runner, as well as on Linux CI, and `docs/INTERFACE.md` says the fit was checked in macOS's system font.


**Fixed 2026-11-28.** The schematic's containers are 72 px tall instead of 96 (`_CONTAINER_HEIGHT` in `app/qt_schematic.py`). That gives the canvas back 24 px. On a GitHub macOS runner under Qt's `cocoa` platform, run 46095018194 of the throwaway `mac-test-drive` workflow on this branch, `test_each_shipped_workspace_shows_its_lesson_whole_with_one_run[Maintenance-1366-768]` passes. The canvas's foot stands 4 px above its box's foot there, at a scale of 1 and of 2, and at widths 1366, 1440 and 1512 the values show whole from a window 764 px tall. In the Linux test fonts the room under the canvas at 1366 by 768 went from 0 to 24 px in Inter and from 14 to 38 px in DejaVu Sans. The other four macOS failures in that run are the ones `PL-2Y1L` lists, and they failed the same way before this change (run 46091853273).

**Why the containers, and not another part of the View.**

1. The Workspace's shares cannot give room at 1366 by 768. The right-hand column is as tall as the chart beside it, and the Parameters Area above the schematic is at its least height, which `test_the_parameters_area_is_not_far_taller_than_its_controls` enforces.
2. Inside the schematic's box, 77 px stand above the canvas in Inter: 14 px of the padding every View has, 21 px for the View's heading line, which every View carries, and 42 px for the run's pinned heading, which `PL-3NGZ` keeps over the rows. Taking room there changes what other Views or the pinned heading show.
3. The gaps that hold the arterial and venous lines and the gap above the labels could give about 12 px while keeping each line clear of its containers. That is too little.
4. A container's height carries no value that is not also printed: the label under each container prints its tension, amount and share. NUREG-0700 Rev. 3 (O'Hara, Brookhaven National Laboratory for the U.S. Nuclear Regulatory Commission, 2020) guideline 1.1-50, p. 1-13, asks that "displays should provide a sufficient viewing area to include all important information". Guideline 1.3.6-18, p. 1-45, says that where "accuracy of reading graphic data is required", it "might prove best simply to let a user point at any data item and have the computer label that item with a readout of its exact value(s)". So the printed values come before the graphic's height. Read in full text on 2026-11-28 from https://www.osti.gov/servlets/purl/1644018. At the standard 3 MAC top the marks at the chart's MAC labels stay 12 px apart.

**Regression test.** `test_the_maintenance_schematic_leaves_room_for_macos_text_at_1366_by_768` draws in DejaVu Sans, the font the Linux CI runners use, and keeps at least 34 px of room under the canvas. That is how much higher the canvas's foot stands there than on a Mac: 14 px above the box's foot in DejaVu Sans with the containers 96 px tall, and 20 px below it on the Mac. On the code before the fix it fails with `AssertionError: the canvas's foot has 14 px of room` (`uv run pytest tests/integration/simulation_view/test_simulation_view_page.py -k leaves_room_for_macos`). Under `cocoa` it draws in macOS's system font and asks only that the canvas's foot be inside the box. The first version held 20 px of room in whichever font the tests ran in, which the first blind review pass found too weak under DejaVu Sans.

**Docs checked.** `docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts and share bar assert", its note for developers (updated: the fit was checked in macOS's font and style, and the new test). The scale caption's comment in `app/compartment_schematic.py` (no longer states 96 px). `docs/VERIFICATION.md`, `docs/MODEL.md`, `README.md` and `docs/ARCHITECTURE.md` state no container height. `ROADMAP.md` names "96 px containers" only in the title of the closed `PL-8W1B`, which is a record.
