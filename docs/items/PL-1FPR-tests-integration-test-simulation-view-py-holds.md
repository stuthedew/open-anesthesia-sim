---
id: PL-1FPR
title: tests/integration/test_simulation_view.py holds 12,232 lines and 307 tests for a 2,193-line module, and tests/integration/test_controller.py holds 6,443 lines: split each by the behaviour it tests
priority: P3
effort: M
status: done
classes: refactor
feature: unit-test-review
touches: tests/integration, tests/integration/simulation_view, tests/integration/controller, .claude/rules/ui-color.md, docs/ARCHITECTURE.md, docs/INTERFACE.md, docs/MODEL.md, docs/WORKING_NOTES.md, docs/apparatus.md, docs/items/PL-0889-the-banner-shown-when-a-run-reaches-the-24-hour.md, docs/items/PL-0G2P-the-run-state-tests-read-only-the-text-of.md, docs/items/PL-1D3Z-a-workspace-pinned-to-a-run-that-is-no-longer.md, docs/items/PL-3JTH-the-refusals-for-branching-at-a-control-event.md, docs/items/PL-4G79-the-approved-interface-wording-list-records.md, docs/items/PL-6XPZ-below-about-1366-px-of-window-width-the-control.md, docs/items/PL-B8DL-the-four-test-layouts-named-every-view-hold.md, docs/items/PL-CBYS-the-page-still-scrolls-at-every-common-screen.md, docs/items/PL-FKN7-the-branch-s-presentation-requested-wiring-is.md, docs/items/PL-H2K2-nothing-signals-a-run-approaching-the-supported.md, docs/items/PL-HF1B-the-control-change-record-in-the-unconditional.md, docs/items/PL-LKX7-docs-interface-md-displayed-precision-says-a.md, docs/items/PL-R17Y-no-test-proves-a-dropped-branch-s-widgets-leave.md, docs/items/PL-RF2S-every-widget-painted-canvas-and-chart-keeps-the.md, docs/items/PL-RS3Z-the-order-of-a-branch-s-splitter-sections-is.md, docs/items/PL-VFPB-no-test-reaches-the-branch-of-simulationview.md, docs/items/PL-VHBW-pl-4l49-s-foreground-walk-builds-only-the-main.md, docs/items/PL-VJD2-build-maximize-area-one-area-fills-the-room-the.md, src/anesthesia_sim/app/run_series.py, tests/conftest.py, tests/integration/test_interface_wording.py, tests/integration/test_qt_rendering.py, tests/integration/test_run_surfaces.py, tests/reference/test_control_resolution.py, tests/unit/test_chart_time_base.py, tests/unit/test_circuit.py, tests/unit/test_dashboard_frame.py, tests/unit/test_formatting.py, tests/unit/test_playback.py, tests/unit/test_resume_at.py, tests/unit/test_run_definition.py, tests/unit/test_wash_in.py, tools/contrast_check.py, tools/regex_baseline.py, tools/restated_constants.py
deferred-from: v0.7.0 - it waits on PL-RF2S, which this gate's list does not hold, and splitting the files first would conflict with that item's open branch; it changes no value a learner sees
added: 2026-11-11
closed: 2026-11-14
pr: 2152
payoff: a contributor can find and read the tests of one behaviour of the run screen or the controller without opening a 12,000-line file
verify: grep -q 'Shared constants and helpers for the controller' tests/integration/controller/controller_support.py && grep -q 'Shared constants and helpers for the dashboard' tests/integration/simulation_view/simulation_view_support.py
---

**Problem.** tests/integration/test_simulation_view.py holds 12,232 lines and 307 tests for a 2,193-line module, and tests/integration/test_controller.py holds 6,443 lines: split each by the behaviour it tests

**What happens.** Measured 2026-11-11 at `e084968ac`: `tests/integration/test_simulation_view.py` holds 12,232 lines and 307 test functions, for `src/anesthesia_sim/app/simulation_view.py` at 2,193 lines. `tests/integration/test_controller.py` holds 6,443 lines. `CLAUDE.md` § "What this project is" names "a file nobody wants to open" as one of the slow accumulations that could end the project. Open items already find that tests in the first file check hand-kept lists that miss cases (`PL-B8DL`, `PL-86VL`, `PL-0G2P`), and a file this long makes such a gap harder to see.
<!-- absent: tests/integration/test_simulation_view.py -->
<!-- absent: tests/integration/test_controller.py -->

**Recommendation.** Split each file by the behaviour its tests check, moving tests without changing them, and keep shared fixtures in a `conftest.py` or a helper module. `PL-RF2S` is changing how the display is written and its tests, so split after it lands.

**Why it matters.** A test file of 12,000 lines is one that nobody reads whole, so a gap in what it checks stays hidden, and every change to the run screen's tests lands in the same file and conflicts with every other branch that touches it.

**Done when.** Each of the two files is split into files that each hold the tests of one behaviour, with no test changed and the same tests collected before and after, and shared fixtures in one helper module or `conftest.py`.

[superseded 2026-11-14] **Blocked on `PL-RF2S` (2026-11-11).** That item rewrites how the run screen is drawn, and its open branch (#2125) changes both files. Splitting first would make that branch's rebase a rewrite. Build this once `PL-RF2S` closes.

**Generator check.** A one-off. Each test was added where the screen's other tests already were, and no rule says when a test file is long enough to split; one item is not enough to say that a rule is missing.

**Done (2026-11-14).** `tests/integration/test_simulation_view.py` became 19 files under `tests/integration/simulation_view/`, and `tests/integration/test_controller.py` became 11 under `tests/integration/controller/`. Each new file holds the tests of one behaviour. A support module in each directory holds the module docstring, constants and helpers that more than one file uses, and `simulation_view/conftest.py` holds the two module-scoped fixtures. The controller directory has no `conftest.py`: the two 24-hour module fixtures and the `MODULE_FIXTURE_MINUTES` entry that `tests/conftest.py` deals by stayed together in `test_controller_supported_length.py`, so that each trunk is still built once per module. A scratch script did the split from the syntax tree. The same 661 test ids were collected before and after, every top-level definition is identical by syntax tree (530 of 530 and 251 of 251), and all 661 moved tests pass.

Decisions taken in the work. `PL-H2K2`'s `verify:` lost its `uv run pytest` clause: `bin/docket check` refuses a verify rewritten on a branch unless it holds only the admitted shapes, and CI runs those tests anyway. Two stale test names surfaced while checking the references, and were fixed: the comment on `COMPARTMENT_STATE_INDEX` in `app/run_series.py` (named by both blind review passes), and the docstring of `_refresh_bookmarks` in `app/simulation_view.py` (a fix-now commit). Filed: `PL-58PP` (two tests restate the interface tick and promise a check that does not exist) and `PL-BDVM` (an uncalled dashboard test helper). `PL-CBYS`'s open branch (#2134) adds tests to the old dashboard file, so whichever of the two merges second moves them.

Docs sweep: `docs/ARCHITECTURE.md` § "Tests (`tests/`)", `docs/INTERFACE.md` (the drawn-columns paragraph, the comparison rule and the foreground test), `docs/MODEL.md` § "Closed-form agreement test", `docs/apparatus.md` (`contrast_check.py`), `docs/WORKING_NOTES.md` (the 2026-10-17 test-ordering note, marked as naming the removed file), `.claude/rules/ui-color.md`, `README.md` and `CONTRIBUTING.md` (neither names the two files), and the comments and docstrings that `grep -rn 'test_simulation_view.py\|test_controller.py'` found under `src/`, `tests/` and `tools/`. Each now names the new file or directory, or is marked as naming the removed one.
