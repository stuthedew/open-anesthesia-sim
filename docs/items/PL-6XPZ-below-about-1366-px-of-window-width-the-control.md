---
id: PL-6XPZ
title: Below about 1366 px of window width the control-change record column shrinks to as little as 68 px and clips its lines behind a horizontal scroll bar, because the left column cannot narrow below the transport row's 1115 px minimum width
priority: P3
effort: M
status: ready
classes: ux
feature: replay-findings
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/run_view.py, tests/integration/test_simulation_view.py, docs/MODEL.md
added: 2026-10-25
payoff: the unconditional control-change record stays readable on windows narrower than 1366 px
verify: grep -q 'def test_the_control_change_record_is_readable_at_the_minimum_window_width' tests/integration/test_simulation_view.py
---

**Problem.** The region's row gives the run rows and the record column stretch shares. The run rows' minimum width is 1115 px, and that comes from the transport row (`app/run_view.py`). So all of the window's shortfall comes out of the record column (`app/simulation_view.py`). The reviewer blamed the heading row, but that row now needs only 786 px. The behaviour they described is unchanged.

**Why it matters.** At a 1250 px window the record is 91 px wide. At the window's minimum width it is 68 px wide. Each entry needs about 165 px, so every line of an unconditional record is cut off behind a scroll bar. `docs/MODEL.md` records the 1366 px case only. No test checks a narrower window.

**Done when.** At every window width the application allows, each control-change entry is readable without a horizontal scroll bar. `tests/integration/test_simulation_view.py` has `test_the_control_change_record_is_readable_at_the_minimum_window_width`, and `docs/MODEL.md` records the narrow case.

**Found by.** `PL-TBQS` reviewer replay on #1585, finding r01 F2, checked against main on 2026-10-25. Measured with `e_i_record_width.py`. The record column was 207 px at 1366 px, 141 px at 1300 px, 91 px at 1250 px and 68 px at 1093 px. At 1093 px the window held at 1227 px, and the horizontal scroll bar was visible from 1300 px down.
