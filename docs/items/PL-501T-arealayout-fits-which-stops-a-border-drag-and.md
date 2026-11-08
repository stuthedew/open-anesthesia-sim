---
id: PL-501T
title: AreaLayout._fits, which stops a border drag and lights the WARNING line, still estimates each Area's drawn size as its window share minus one handle, not from the apportionment the splitters draw: the estimate ignores nested handles and overstates an Area whose split neighbour is held wider than its share, and two adapter tests pin the stop it gives, a handle's width short of the neighbour's need (found building PL-16BG)
priority: P2
effort: M
status: ready
classes: defect
feature: area-layout-sizing
touches: src/anesthesia_sim/app/area_layout.py, tests/integration/test_layout_adapter.py
added: 2026-11-01
payoff: a border drag stops where the neighbouring Area reaches the size it needs, so the stored layout matches what is drawn
verify: grep -q 'def test_a_drag_into_a_nested_split_stops_at_the_drawn_need' tests/integration/test_layout_adapter.py
reenters: PL-16BG
---

**Problem.** AreaLayout._fits, which stops a border drag and lights the WARNING line, still estimates each Area's drawn size as its window share minus one handle, not from the apportionment the splitters draw: the estimate ignores nested handles and overstates an Area whose split neighbour is held wider than its share, and two adapter tests pin the stop it gives, a handle's width short of the neighbour's need (found building PL-16BG)

**Why it matters.** Both errors overstate an Area's drawn size, so a drag can go past the point where an Area reaches its least size. Qt then holds the frame at its minimum, and the stored border no longer matches the drawn one. `PL-MH5T` and `PL-97WX` removed that mismatch from the other readers of the drawn size.

**Reproduced 2026-11-03, by reading; not run in Qt.** `_fits`'s docstring in `src/anesthesia_sim/app/area_layout.py` states both errors and names this item. `test_a_drag_stops_where_the_neighbour_reaches_its_views_declared_need` in `tests/integration/test_layout_adapter.py` pins the stop a handle's width short of the neighbour's need, as its comment says.

**Done when.** `_fits` reads each Area's drawn size from the apportionment the splitters draw. A test with a nested split, and one with a neighbour held wider than its share, shows the drag stopping where the neighbour reaches its least size. The two tests that pin the handle-width stop are rewritten to the new stop.

**Generator check.** An instance of `PL-16BG`'s fact, filed the day that head closed: the size an Area is drawn at. `_fits` is one more reader that works the drawn size out for itself (`reenters: PL-16BG`).

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. `AreaLayout._fits` already estimated an Area's drawn size as its share less one handle at `817a4d88` (`281045a3`, 2026-10-19), and Areas held wider than their share existed (`8ae7824c`).
