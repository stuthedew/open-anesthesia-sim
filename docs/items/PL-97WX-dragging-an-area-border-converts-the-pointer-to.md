---
id: PL-97WX
title: Dragging an Area border converts the pointer to a fraction linearly across the split while the splitters draw settle's held sizes, so a 1 px nudge of a held border rewrites the stored fraction (0.7 to about 0.626 in one case) and emits layout_changed though nothing moves, and the border then sticks for tens of pixels
priority: P2
effort: M
status: ready
classes: defect
feature: area-layout-sizing
touches: src/anesthesia_sim/app/area_layout.py, tests/integration/test_layout_adapter.py
added: 2026-10-25
payoff: a press-and-nudge the reader cannot see no longer rewrites their saved layout proportions
verify: grep -q 'def test_a_one_pixel_nudge_of_a_held_border_keeps_the_stored_fraction' tests/integration/test_layout_adapter.py
---

**Problem.** `AreaLayout._position_at` computes the share as the pointer's edge divided by the drawable length (`app/area_layout.py`). `_fits` checks sizes taken from the model's fractions. The splitters draw `settle`'s held sizes instead. Take a row at 0.7/0.3 in 808 px whose right View needs 300 px. The border is drawn at 500 px, not at the 560 px that 0.7 would give.

**Why it matters.** A press-and-nudge that the reader cannot see changes their saved proportions. That breaks the stated rule that held sizes leave the stored fractions alone. The drag then feels frozen until the pointer passes the fraction-based position.

**Done when.** Dragging an Area border maps the pointer through the held sizes the splitters draw, so a 1 px nudge of a held border leaves the stored fraction unchanged and emits no `layout_changed`. `tests/integration/test_layout_adapter.py` has `test_a_one_pixel_nudge_of_a_held_border_keeps_the_stored_fraction`, using the 0.7/0.3 row in 808 px.

**Found by.** `PL-TBQS` reviewer replay on #1622, finding r02 F3, which a blind checker confirmed at the merge commit. Checked against main on 2026-10-25 by reading `_position_at`, `_fits`, `_lay_out` and `layout/sizing._held_sizes`. None has changed in a way that maps the pointer through the held sizes. It was not reproduced in Qt.
