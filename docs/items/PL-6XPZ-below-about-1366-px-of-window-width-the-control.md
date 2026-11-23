---
id: PL-6XPZ
title: Below about 1366 px of window width the control-change record column shrinks to as little as 68 px and clips its lines behind a horizontal scroll bar, because the left column cannot narrow below the transport row's 1115 px minimum width
priority: P3
effort: M
status: done
classes: ux
feature: replay-findings
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/run_view.py, tests/integration/simulation_view, docs/MODEL.md
added: 2026-10-25
closed: 2026-11-23
pr: 2275
payoff: the unconditional control-change record stays readable on windows narrower than 1366 px
tests: tests/integration/simulation_view/test_simulation_view_page.py::test_the_control_change_record_is_readable_at_the_minimum_window_width, tests/integration/simulation_view/test_simulation_view_page.py::test_the_version_and_model_label_keeps_one_line_where_its_row_has_room, tests/unit/test_control_timeline.py::test_no_recordable_line_has_a_part_longer_than_the_longest_parts
recurrences: 2026-11-14 PL-92XM
---

**Problem.** The region's row gives the run rows and the record column stretch shares. The run rows' minimum width is 1115 px, and that comes from the transport row (`app/run_view.py`). So all of the window's shortfall comes out of the record column (`app/simulation_view.py`). The reviewer blamed the heading row, but that row now needs only 786 px. The behaviour they described is unchanged.

**Why it matters.** At a 1250 px window the record is 91 px wide. At the window's minimum width it is 68 px wide. Each entry needs about 165 px, so every line of an unconditional record is cut off behind a scroll bar. `docs/MODEL.md` records the 1366 px case only. No test checks a narrower window.

**Done when.** At every window width the application allows, each control-change entry is readable without a horizontal scroll bar. `tests/integration/simulation_view/` has `test_the_control_change_record_is_readable_at_the_minimum_window_width`, and `docs/MODEL.md` records the narrow case.

**Found by.** `PL-TBQS` reviewer replay on #1585, finding r01 F2, checked against main on 2026-10-25. Measured with `e_i_record_width.py`. The record column was 207 px at 1366 px, 141 px at 1300 px, 91 px at 1250 px and 68 px at 1093 px. At 1093 px the window held at 1227 px, and the horizontal scroll bar was visible from 1300 px down.

**Checked 2026-11-22** against `d4e8200`: still applies, but its numbers are out of date. The region still gives the left column its share and never narrows it below the transport row's minimum width (`src/anesthesia_sim/app/simulation_view.py`, `_RECORD_COLUMN_STRETCH`). No test named `test_the_control_change_record_is_readable_at_the_minimum_window_width` exists. That minimum now depends on the version label. `PL-92XM` (untriaged, filed 2026-11-14) measured 1028 px with a development version label at a 1280 px window, not the 1115 px given here, and it describes the same fault. The document half has moved: `docs/INTERFACE.md` § "Minimum displayed outputs" now says that below about 1366 px a longer version string narrows the record, but it gives no width for the narrow case.

**Done 2026-11-23.** The right column of the region, which holds the control-change record, now has a least width: the widest unbroken part of any line the record can show, measured with every digit drawn as the font's widest. `longest_unbroken_parts` in `src/anesthesia_sim/app/control_timeline.py` lists those parts at each control's largest recordable value, the end of the longest supported run and the most settings a run can step under; with the tests' font the column needs 228 px. The version-and-model label beside the run controls now wraps between words, so the transport row's least width no longer grows with the version string or the agent's name. Where the window is too narrow for both, the readout row steps down from seven across to four, below about 1260 px, rather than the record losing its line ends. Sizing the window from the dashboard before its first frame then gave a geometry narrower than the window's own minimum, because the readout labels are empty until that frame, so `main` now presents the first frame before it sizes the window.

Regression test: `test_the_control_change_record_is_readable_at_the_minimum_window_width` in `tests/integration/simulation_view/test_simulation_view_page.py`, which checks the record at the narrowest window the dashboard allows with the longest text the label can carry, "Version unavailable (this build is not traceable)". Run against `origin/main` at `e75ec4d3` it fails with `assert 145 >= 184`: the record's label was 145 px against the 184 px that "Alveolar ventilation 12.0 L/min ->" needs. `test_the_longest_parts_include_the_widest_line_a_learner_can_record` and `test_no_recordable_line_has_a_part_longer_than_the_longest_parts` in `tests/unit/test_control_timeline.py` hold the list of parts to every line a learner can record. The full suite passed on the rebased branch, 12,752 tests. Documents checked: `docs/INTERFACE.md` (§ "Minimum displayed outputs" and the readout-row paragraphs, updated), `docs/MODEL.md` (no longer holds a window width, since the split by reader moved the 1366 px case to `docs/INTERFACE.md`), `docs/ARCHITECTURE.md` (no new module).

Both blind review passes found that the label's word wrap asked the row for a width Qt guesses, about forty characters, so the version-and-model text broke over two lines at every window width and made the transport row taller in a wide window too. The label is now a `OneLineWhereRoomLabel` (`src/anesthesia_sim/app/qt_widgets.py`), which asks for its one-line width and wraps between words only where the row gives it less, with its longest word as its least width. `test_the_version_and_model_label_keeps_one_line_where_its_row_has_room` holds it: run before this fix it fails with `assert 279 > 361`, the label's width against its text's. A build whose version cannot be read has the longest text, and at 1366 px it still wraps, because the row is then short of room. Pass 2 also noted that a break at any space can part "Version" from its number at a narrow window; that is kept, because breaking only at the dash would hold the row at the width of "Version unavailable (this build is not traceable)", which brings back much of the floor this item removed.

The self-audit's mutation run left one survivor, and it is equivalent: in `longest_unbroken_parts` the mutant writes `unit=None` into the `ControlAdjustment`, and `format_adjustment` never reads that field, because it takes each value's unit from the control through `format_control_value`. So the rendered parts, and every assertion on them, are the same either way.
