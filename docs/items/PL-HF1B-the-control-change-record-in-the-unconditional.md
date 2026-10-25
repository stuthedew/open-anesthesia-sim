---
id: PL-HF1B
title: The control-change record in the unconditional region is clipped to the height of the run rows (163 px for one run), so after about four changes the older entries fall out of view, and the "N earlier change(s) not listed" note always sits below the fold; in a comparison the branch's whole record starts under the trunk's
priority: P2
effort: M
status: ready
classes: ux, test
feature: replay-findings
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/test_simulation_view.py, docs/MODEL.md
added: 2026-10-25
payoff: a learner always sees that older control changes are missing from the record, instead of a list that seems to end
verify: grep -q 'def test_every_unconditional_value_lies_inside_its_scroll_viewport' tests/integration/test_simulation_view.py
---

**Problem.** `record_scroll` has an Ignored vertical size policy, so it is only as tall as the run rows beside it (`app/simulation_view.py`). The list is newest first. The overflow note is placed after the 12 listed entries, and it appears only when the list is already full. So whenever the note appears, it is below the viewport. Both runs' records stack in this one scroller. The guard `_require_unconditional_values` checks ancestry only. `test_no_unconditional_value_sits_inside_the_layout_container` checks `isAncestorOf` and `isVisible()` (`tests/integration/test_simulation_view.py`). A widget scrolled out of view passes both checks.

**Why it matters.** `docs/MODEL.md` makes the record unconditional. It also says bounds are displayed, not silent. A learner sees a list that seems to end, and nothing in view says that earlier changes are missing. The scroll bar may be hidden at rest on macOS. `PL-J8K2` Q3 ratified "scrolling within itself with the overflow sentence". It did not weigh that the sentence would always be out of view. Ordinary evidence reopens a ratified decision, and this measurement is that evidence.

**Done when.** The note saying earlier changes are not listed is in view whenever it appears, and the check on unconditional values tests that each one lies inside its scroll viewport, not only that it is a visible descendant. `tests/integration/test_simulation_view.py` has `test_every_unconditional_value_lies_inside_its_scroll_viewport`.

**Found by.** `PL-TBQS` reviewer replay on #1585, findings r01 F1, r02 F2, r03 F2, r04 F1 and r05 F1, plus `PL-ZWXD`'s first #1585 entry. Checked against main on 2026-10-25. Measured offscreen with `e_h_record_clip.py` at 1366x900 with one run. The record viewport was 163 px tall. Six changes made 336 px of content. Fourteen changes put "2 earlier change(s) not listed" at y=596.
