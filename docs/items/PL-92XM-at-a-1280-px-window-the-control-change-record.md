---
id: PL-92XM
title: At a 1280 px window the control-change record narrows when the version label is long: the transport row's minimum width includes the version badge, so a dev checkout's 'Version 0.6.18+g0e0aa1cd.dirty' holds the left column at 1028 px, the record's text at 180 px, and 'Alveolar ventilation 12.0 L/min ->' (184 px) no longer fits on one line
priority: P3
effort: S
status: done
classes: ux
feature: replay-findings
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py, tests/integration/simulation_view
added: 2026-11-14
closed: 2026-11-23
pr: 2275
payoff: the control-change record keeps whole lines at a 1280 px window whatever version or agent the badge names
tests: tests/integration/simulation_view/test_simulation_view_page.py::test_the_control_change_record_is_readable_at_the_minimum_window_width, tests/integration/simulation_view/test_simulation_view_page.py::test_the_version_and_model_label_keeps_one_line_where_its_row_has_room
---

**Problem.** At a 1280 px window the control-change record narrows when the version label is long: the transport row's minimum width includes the version badge, so a dev checkout's 'Version 0.6.18+g0e0aa1cd.dirty' holds the left column at 1028 px, the record's text at 180 px, and 'Alveolar ventilation 12.0 L/min ->' (184 px) no longer fits on one line

**Same mechanism as `PL-6XPZ`, found while closing `PL-LKX7`.** The run rows
cannot narrow below the transport row's minimum width, so the record column
absorbs any shortfall. The new fact is that the version badge is part of that
minimum, so the floor moves with the version string. Measured 2026-11-14 with
the integration tests' `_shown_view` at 1280 px: with a clean checkout the
left column takes its 0.82 share, 1014 px, and the record's text is 194 px;
with uncommitted changes the badge reads "Version 0.6.18+g0e0aa1cd.dirty",
the transport row needs 1028 px, the record shrinks to 208 px and its text to
180 px. The widest part of a record line that cannot break is "Alveolar
ventilation 12.0 L/min ->" at 184 px, so in that state its arrow is clipped.
A release build's shorter version string avoids it, but a build without
package metadata shows "Version unavailable (this build is not traceable)",
which is longer than either, and the agent's name in the same badge changes
its width too (both found by the blind review of `PL-LKX7`). The readout row
seats seven across in both measured states.

**Checked 2026-11-22.** `RunView.build_transport_row` in `app/run_view.py` still adds the version-and-model badge (`_agent_header_badge`) at the row's right end, and nothing shortens its text. So the row's minimum width still grows with the version string and the agent's name. The badge was in the transport row at the freeze too (`git show 0947408:src/anesthesia_sim/app/run_view.py`).

**Why it matters.** The control-change record is one of the values that stay on screen in every layout. At a 1280 px window its lines lose their ends whenever the badge grows wider, so a learner can lose the arrow and what follows it. A development build shows this, and so does a build without package metadata, whose version text is longer still.

**Done when.** At a 1280 px window the record's longest unbreakable line fits whatever the badge says. A test shows it with the longest text the badge can carry, "Version unavailable (this build is not traceable)".

**Generator check.** The fact misread is the transport row's minimum width, which sets how wide the record column can be. `PL-6XPZ` (the record clips below 1366 px) is the same mechanism and is still open, so this is a second instance of an open item rather than a re-entry. The two are best fixed together.

**Done 2026-11-23, with `PL-6XPZ`.** The right column of the region, which holds the control-change record, now has a least width: the widest unbroken part of any line the record can show, measured with every digit drawn as the font's widest. `longest_unbroken_parts` in `src/anesthesia_sim/app/control_timeline.py` lists those parts at each control's largest recordable value, the end of the longest supported run and the most settings a run can step under; with the tests' font the column needs 228 px. The version-and-model label beside the run controls now wraps between words, so the transport row's least width no longer grows with the version string or the agent's name. Where the window is too narrow for both, the readout row steps down from seven across to four, below about 1260 px, rather than the record losing its line ends. Sizing the window from the dashboard before its first frame then gave a geometry narrower than the window's own minimum, because the readout labels are empty until that frame, so `main` now presents the first frame before it sizes the window.

Regression test: `test_the_control_change_record_is_readable_at_the_minimum_window_width` in `tests/integration/simulation_view/test_simulation_view_page.py`, which checks the record at the narrowest window the dashboard allows with the longest text the label can carry, "Version unavailable (this build is not traceable)". Run against `origin/main` at `e75ec4d3` it fails with `assert 145 >= 184`: the record's label was 145 px against the 184 px that "Alveolar ventilation 12.0 L/min ->" needs. `test_the_longest_parts_include_the_widest_line_a_learner_can_record` and `test_no_recordable_line_has_a_part_longer_than_the_longest_parts` in `tests/unit/test_control_timeline.py` hold the list of parts to every line a learner can record. The full suite passed on the rebased branch, 12,752 tests. Documents checked: `docs/INTERFACE.md` (§ "Minimum displayed outputs" and the readout-row paragraphs, updated), `docs/MODEL.md` (no longer holds a window width, since the split by reader moved the 1366 px case to `docs/INTERFACE.md`), `docs/ARCHITECTURE.md` (no new module).

Both blind review passes found that the label's word wrap asked the row for a width Qt guesses, about forty characters, so the version-and-model text broke over two lines at every window width and made the transport row taller in a wide window too. The label is now a `OneLineWhereRoomLabel` (`src/anesthesia_sim/app/qt_widgets.py`), which asks for its one-line width and wraps between words only where the row gives it less, with its longest word as its least width. `test_the_version_and_model_label_keeps_one_line_where_its_row_has_room` holds it: run before this fix it fails with `assert 279 > 361`, the label's width against its text's. A build whose version cannot be read has the longest text, and at 1366 px it still wraps, because the row is then short of room. Pass 2 also noted that a break at any space can part "Version" from its number at a narrow window; that is kept, because breaking only at the dash would hold the row at the width of "Version unavailable (this build is not traceable)", which brings back much of the floor this item removed.
