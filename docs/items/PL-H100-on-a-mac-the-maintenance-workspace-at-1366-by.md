---
id: PL-H100
title: On a Mac, the Maintenance Workspace at 1366 by 768 leaves each container's share line cut through at the schematic's lower edge and its share bar out of view, because macOS's system font draws taller lines than the Linux fonts the tests use; the values show whole only from a 788 px tall window
status: untriaged
feature: interface-matches-its-spec
touches: src/anesthesia_sim/data/workspaces/maintenance.json, src/anesthesia_sim/app/qt_schematic.py, tests/integration/simulation_view/test_simulation_view_page.py, docs/INTERFACE.md
added: 2026-11-28
---

**Problem.** On a Mac, the Maintenance Workspace at 1366 by 768 leaves each container's share line cut through at the schematic's lower edge and its share bar out of view, because macOS's system font draws taller lines than the Linux fonts the tests use; the values show whole only from a 788 px tall window

**Measured 2026-11-28** on a GitHub macOS runner (image `macos-26-arm64`, macOS 26.7.2, PySide6 6.12.0), at `a2dd5548` and `2d10ae96`, which add nothing to `main` at `b893e699` but a throwaway probe. Runs 46091853273 and 46092465778 of the `mac-test-drive` workflow on branch `claude/project-thread-m4oy26` hold the logs. The probe built the dashboard with `open_dashboard`, opened Maintenance, pressed Start and advanced one run to 1 h. It ran under Qt's `cocoa` platform, so the app drew with the platform's own style (`macos`) and font (`.AppleSystemUIFont`, 13 pt).

1. **The runner's screen is 1024 by 768, and macOS shrinks a shown window to fit it.** The first run asked for 1600 by 1000 and got 1169 by 645. Every later measurement marks the window `Qt.WidgetAttribute.WA_DontShowOnScreen` before showing it, which keeps the size asked for and still lays text out with the platform's font and style.
2. **At 1366 by 768 the schematic's canvas is 20 px taller than the part of its Area in view.** The Area's viewport is 742 by 252, and the canvas starts 80 px down it and is 192 px tall. So the third label line under each container ("13% of agent" for Circuit) is cut through at the viewport's lower edge, and the share bars are below it. `test_each_shipped_workspace_shows_its_lesson_whole_with_one_run[Maintenance-1366-768]` fails there with "the containers and shares is not wholly on screen in Maintenance". It passes on Linux CI.
3. **The values show whole from a window 788 px tall** at widths 1366, 1440, 1470 and 1512, and from 824 px at 1280. Every label, unit and name fits its box at 1366 by 768, 1470 by 850, 1512 by 917 and 1728 by 1052, at a scale of 1 and of 2 (`QT_SCALE_FACTOR=2`, standing in for a Retina screen). Only the vertical fit fails.
4. **The style is not the cause.** With `app.setStyle("Fusion")` and the same macOS font, the values show whole from 780 px at widths 1366 to 1512, so 1366 by 768 is still 12 px short. The macOS font's lines are 16 px where the Linux test fonts' are 15, and the schematic stacks several of them above and under the containers.
5. **What a maximized window loses on that Mac.** A shown window's title bar was 32 px, the menu bar 31 px and the Dock 63 px (screen 1024 by 768, available 0, 31, 1024, 674). So a maximized window 788 px tall needs a screen about 914 px tall with the Dock showing. A notched MacBook's menu bar was not measured.

**Why it matters.** `docs/INTERFACE.md` says the Maintenance Workspace shows the containers and the share caption whole at 1366 by 768 with one run. On a Mac it does not, and a value line cut through at the lower edge can look like another value, the hazard `PL-GWTR` records for the upper edge. The pinned run heading keeps every value beside its run and compartment (`PL-3NGZ`), and a scroll of the Area shows the rest.

**Where to start.** The fix needs about 20 px of height at 1366 by 768 in the macOS font, taken from the schematic's own rows or given by the Workspace's shares, without breaking the concentration chart's least height. Prove it on macOS, which needs `PL-2Y1L` (a macOS test job) or the same throwaway probe, because the Linux tests cannot see this.

