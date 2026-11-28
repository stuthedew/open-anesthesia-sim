---
id: PL-2Y1L
title: No test runs on macOS, so a layout that fits the Linux test fonts but not macOS's system font passes every check: five layout tests fail on a GitHub macOS runner that pass on Linux
status: untriaged
feature: interface-matches-its-spec
touches: .github/workflows/quality.yml, tests/conftest.py, tests/integration/simulation_view/test_simulation_view_page.py
added: 2026-11-28
---

**Problem.** No test runs on macOS, so a layout that fits the Linux test fonts but not macOS's system font passes every check: five layout tests fail on a GitHub macOS runner that pass on Linux

**Measured 2026-11-28**, on the runs `PL-H100` records. Every workflow in `.github/workflows/` runs on Ubuntu, and the tests set Qt's `offscreen` platform (`tests/conftest.py`), so each layout test sees the Fusion style and a Linux font. The project owner uses the app on a Mac, where it draws with the `macos` style and macOS's system font, because the app sets no style.

Run under `cocoa` on a GitHub macOS runner, with each test window kept at its asked size (a throwaway pytest plugin set `WA_DontShowOnScreen` before each window's `show`), five of 162 tests in `test_compartment_schematic_view.py`, `test_agent_cost_view.py`, `test_qt_rendering.py` and `simulation_view/test_simulation_view_page.py` fail:

1. `test_each_shipped_workspace_shows_its_lesson_whole_with_one_run[Maintenance-1366-768]`: the schematic's values are 20 px below the part in view (`PL-H100`).
2. `test_the_parameter_controls_stand_where_they_did_after_a_tab_switch[1920-1080]`: the Parameters Area is at x 1152, 752 px wide, in Default and Induction, and at x 1145, 759 px wide, in Maintenance, so the controls move 7 px on a tab switch.
3. `test_a_whole_view_is_held_at_the_height_it_needs_at_the_width_it_is_drawn[Induction]` and `[Maintenance]`: the Area is 1 px taller than its View needs (391 for 390, 329 for 328).
4. `test_the_parameters_area_is_not_far_taller_than_its_controls[Default-1366-768]`: the Area's scroll box is 153 px for a bound of 152.

Without `WA_DontShowOnScreen` 32 tests fail, because macOS shrinks every window to the runner's 1024 by 768 screen. GitHub's standard runners are free in public repositories, and this one is public.

**Where to start.** Decide whether a macOS job runs the layout tests on every pull request or on a schedule, and whether the probe's `WA_DontShowOnScreen` belongs in `tests/conftest.py` under `cocoa`. Then fix or re-derive the four smaller failures above. The job is new CI, so check the workflow-machinery pause in `CLAUDE.md` before building it.

