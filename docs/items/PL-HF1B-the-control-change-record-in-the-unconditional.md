---
id: PL-HF1B
title: The control-change record in the unconditional region is clipped to the height of the run rows (163 px for one run), so after about four changes the older entries fall out of view, and the "N earlier change(s) not listed" note always sits below the fold; in a comparison the branch's whole record starts under the trunk's
priority: P2
effort: M
status: done
classes: ux, test
feature: replay-findings
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/simulation_view, docs/MODEL.md
added: 2026-10-25
closed: 2026-11-23
pr: 2280
payoff: a learner always sees that older control changes are missing from the record, instead of a list that seems to end
tests: tests/integration/simulation_view/test_simulation_view_branch_display.py::test_every_unconditional_value_lies_inside_its_scroll_viewport
recurrences: 2026-11-22 PL-RXR8
---

**Problem.** `record_scroll` has an Ignored vertical size policy, so it is only as tall as the run rows beside it (`app/simulation_view.py`). The list is newest first. The overflow note is placed after the 12 listed entries, and it appears only when the list is already full. So whenever the note appears, it is below the viewport. Both runs' records stack in this one scroller. The guard `_require_unconditional_values` checks ancestry only. `test_no_unconditional_value_sits_inside_the_layout_container` checks `isAncestorOf` and `isVisible()` (`tests/integration/simulation_view/`). A widget scrolled out of view passes both checks.

**Why it matters.** `docs/MODEL.md` makes the record unconditional. It also says bounds are displayed, not silent. A learner sees a list that seems to end, and nothing in view says that earlier changes are missing. The scroll bar may be hidden at rest on macOS. `PL-J8K2` Q3 ratified "scrolling within itself with the overflow sentence". It did not weigh that the sentence would always be out of view. Ordinary evidence reopens a ratified decision, and this measurement is that evidence.

**Done when.** The note saying earlier changes are not listed is in view whenever it appears, and the check on unconditional values tests that each one lies inside its scroll viewport, not only that it is a visible descendant. `tests/integration/simulation_view/` has `test_every_unconditional_value_lies_inside_its_scroll_viewport`.

**Found by.** `PL-TBQS` reviewer replay on #1585, findings r01 F1, r02 F2, r03 F2, r04 F1 and r05 F1, plus `PL-ZWXD`'s first #1585 entry. Checked against main on 2026-10-25. Measured offscreen with `e_h_record_clip.py` at 1366x900 with one run. The record viewport was 163 px tall. Six changes made 336 px of content. Fourteen changes put "2 earlier change(s) not listed" at y=596.

**Checked 2026-11-22** against `d4e8200`: still applies. `record_scroll` in `SimulationView` (`app/simulation_view.py`) still has an `Ignored` vertical size policy. `RunView` (`app/run_view.py`) still adds `_control_timeline_overflow_text` below the listed entries, and `MAX_LISTED_ADJUSTMENTS` is still 12. `test_no_unconditional_value_sits_inside_the_layout_container` still checks only ancestry and visibility. The requirement that the record is unconditional is now in `docs/INTERFACE.md`, not `docs/MODEL.md`.

**Done 2026-11-23.** Each run's control-change entries now scroll inside a box of their own under the run's heading, and a line under the heading states how many adjustments the run has and how many earlier ones the list leaves out. The page no longer scrolls the record column as a whole, so the heading and the count stay in view however long the list grows, and in compare mode the second run's heading and count stay in view under the first's. A list that scrolls is otherwise read as complete: Flaherty (Nielsen Norman Group, 2016, https://www.nngroup.com/articles/illusion-of-completeness/, read in this session) reports six of eight users in a study not realizing they could scroll a page whose visible part looked finished. The check on unconditional values now tests that each one lies inside every scroll viewport it sits in, not only that it is a visible descendant.

Regression test: `test_every_unconditional_value_lies_inside_its_scroll_viewport` in `tests/integration/simulation_view/test_simulation_view_branch_display.py`, with two long records. Run against `origin/main` at `73957bf0` it fails with `AssertionError: control_input_record is scrolled out of view`. Documents checked: `docs/INTERFACE.md` (§ "Minimum displayed outputs", the record's paragraph, updated), `docs/MODEL.md` (holds no part of the record's layout since the split by reader), `docs/ARCHITECTURE.md` (no new module).
