---
id: PL-C9XP
title: AreaLayout's minimum size hint is the sum of the Views' needs, while settle and each frame hold an Area at the larger of need and floor, so where a header floor is wider than a View's need the scrolling page grows too little and a neighbouring View shows "Too small" (568 px hint against a 585 px requirement in one case)
priority: P2
effort: S
status: ready
classes: defect, ux
feature: area-layout-sizing
touches: src/anesthesia_sim/app/area_layout.py, tests/integration/test_layout_adapter.py
added: 2026-10-25
payoff: a host that can grow always grows enough, so no View that fits shows a Too small notice
verify: grep -q 'def test_the_minimum_size_hint_counts_each_area_at_its_floor' tests/integration/test_layout_adapter.py
---

**Problem.** `_settle` computes `least = minimum_extent(tree, AREA_HANDLE_WIDTH, needs)` (`app/area_layout.py`). `settle` instead bounds each Area by `_larger(need, floor)` (`layout/sizing.py`). The branch for a widget not yet shown also builds `Fit(laid_out, needs, ...)` with bare needs as its bounds (`area_layout.py`). The `Fit.bounds` docstring says the window's minimum is the sum of those bounds.

**Why it matters.** `docs/MODEL.md` says a host that can grow never shows the notice. With a narrow View under a wider header, the page grows only to the understated hint, and a View that could have been drawn shows "Too small for ...". The hint should be computed from the larger of need and floor.

**Done when.** `AreaLayout`'s minimum size hint, and the bounds of the not-yet-shown branch, count each Area at the larger of its need and its floor. `tests/integration/test_layout_adapter.py` has `test_the_minimum_size_hint_counts_each_area_at_its_floor`, using the 160 and 400 px row with a 177 px floor.

**Found by.** `PL-TBQS` reviewer replay on #1622, findings r02 F4, r03 F2, r05 F3 and r06 F3, checked against main on 2026-10-25. Reproduced with `e_v_hint_from_needs.py`. For a row whose needs are 160 and 400 px wide, with a 177 px floor and 8 px handles, the hint is 568 px and the true least is 585 px. At 568 px, Area 2 is reported too small at 280 px.
