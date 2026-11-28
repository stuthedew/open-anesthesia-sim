---
id: PL-2Y1L
title: No test runs on macOS, so a layout that fits the Linux test fonts but not macOS's system font passes every check: five layout tests fail on a GitHub macOS runner that pass on Linux
priority: P1
effort: M
status: ready
classes: defect, safety
feature: interface-matches-its-spec
touches: .github/workflows/quality.yml, tests/conftest.py, tests/integration/simulation_view/test_simulation_view_page.py, tests/integration/test_compartment_schematic_view.py, tests/integration/test_agent_cost_view.py, tests/integration/test_qt_rendering.py
deferred-from: v0.7.0 - safety, deferred on the terms of ROADMAP.md § 'Deferring to the next gate' because its hazard is not live: the one macOS failure that hid a value, PL-H100, closed in #2350, and run 46099466060 of the throwaway macOS workflow after #2346 left only the four failures this brief lists, which move a control 7 px or size an Area 1 px off and hide no value; the release waits only on the owner's test drive (triage 2026-11-28)
added: 2026-11-28
payoff: a layout change that cuts a value on a Mac fails its pull request, as it already does on Linux
---

**Problem.** No test runs on macOS, so a layout that fits the Linux test fonts but not macOS's system font passes every check: five layout tests fail on a GitHub macOS runner that pass on Linux

**Measured 2026-11-28**, on the runs `PL-H100` records. Every workflow in `.github/workflows/` runs on Ubuntu, and the tests set Qt's `offscreen` platform (`tests/conftest.py`), so each layout test sees the Fusion style and a Linux font. The project owner uses the app on a Mac, where it draws with the `macos` style and macOS's system font, because the app sets no style.

Run under `cocoa` on a GitHub macOS runner, with each test window kept at its asked size (a throwaway pytest plugin set `WA_DontShowOnScreen` before each window's `show`), five of 162 tests in `test_compartment_schematic_view.py`, `test_agent_cost_view.py`, `test_qt_rendering.py` and `simulation_view/test_simulation_view_page.py` fail:

1. `test_each_shipped_workspace_shows_its_lesson_whole_with_one_run[Maintenance-1366-768]`: the schematic's values are 20 px below the part in view (`PL-H100`).
2. `test_the_parameter_controls_stand_where_they_did_after_a_tab_switch[1920-1080]`: the Parameters Area is at x 1152, 752 px wide, in Default and Induction, and at x 1145, 759 px wide, in Maintenance, so the controls move 7 px on a tab switch.
3. `test_a_whole_view_is_held_at_the_height_it_needs_at_the_width_it_is_drawn[Induction]` and `[Maintenance]`: the Area is 1 px taller than its View needs (391 for 390, 329 for 328).
4. `test_the_parameters_area_is_not_far_taller_than_its_controls[Default-1366-768]`: the Area's scroll box is 153 px for a bound of 152.

Without `WA_DontShowOnScreen` 32 tests fail, because macOS shrinks every window to the runner's 1024 by 768 screen. GitHub's standard runners are free in public repositories, and this one is public.

**Why it matters.** The project owner uses the app on a Mac, and `PL-H100` showed that a layout which passes every Linux test can cut a value there: in the Maintenance Workspace at 1366 by 768, each container's share line was cut through at the schematic's lower edge. So every layout test that holds a required value whole holds it only in the Linux test fonts. `PL-H100` was found only because a session thought to run a throwaway macOS probe.

**Checked 2026-11-28, from the record.** `PL-H100` closed in #2350. Its brief records run 46099466060 of the throwaway `mac-test-drive` workflow, after #2346 merged: `PL-H100`'s test passed under `cocoa`, and the other four failures were the four listed above, failing as before. Those four move the parameter controls 7 px on a tab switch, or size an Area or its scroll box 1 px larger than its bound, and none hides a value.

**What GitHub offers, read 2026-11-28.** GitHub Docs, "GitHub Actions billing" (https://docs.github.com/en/billing/concepts/product-billing/github-actions): "The use of standard GitHub-hosted runners is free:", followed by "In public repositories". "GitHub-hosted runners reference" (https://docs.github.com/en/actions/reference/runners/github-hosted-runners) lists `macos-latest` among the standard runners for public repositories, with 3 M1 cores and 7 GB of memory. "Actions limits" (https://docs.github.com/en/actions/reference/limits) allows 5 concurrent macOS jobs on the Free plan and says that "jobs that run on macOS runners may take longer to start."

**Where to start.** Decide whether a macOS job runs the layout tests on every pull request or on a schedule, and whether the probe's `WA_DontShowOnScreen` belongs in `tests/conftest.py` under `cocoa`. Then fix or re-derive the four smaller failures above. The job is new CI, so check the workflow-machinery pause in `CLAUDE.md` before building it. On 2026-11-28 no open workflow-lane head carries `generator: live`: the two live heads, `PL-GJ1W` and `PL-LHCL`, touch `src/anesthesia_sim/core` (`bin/docket generators`). So the pause did not hold this job then.

**Decided at triage 2026-11-28: every pull request, not a schedule.** A scheduled run reports a Mac-only break after the change has merged, and that is how `PL-H100` reached `main`. Run only the layout test files listed above, not the whole suite, because macOS jobs start more slowly and only five can run at once on the Free plan. Rule 14 of `.claude/rules/instruction-writing.md` makes this a session's choice, because it changes one internal structure and nothing a user sees.

**Done when.** A macOS job in CI runs the layout test files listed above under Qt's `cocoa` platform on every pull request that runs the test suite, and each of the four failures listed above passes there or has been re-derived for macOS's font, with the reason written in this brief.

**Generator check.** This is the cause `PL-H100` names: every layout test runs in a Linux font and style, so a fit that holds there is never checked in macOS's system font. The fact misread is whether a layout that fits in the test fonts fits in the user's platform font. `PL-H100` is its one member, and one member is not a generator.
