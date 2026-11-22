---
id: PL-501T
title: AreaLayout._fits, which stops a border drag and lights the WARNING line, still estimates each Area's drawn size as its window share minus one handle, not from the apportionment the splitters draw: the estimate ignores nested handles and overstates an Area whose split neighbour is held wider than its share, and two adapter tests pin the stop it gives, a handle's width short of the neighbour's need (found building PL-16BG)
priority: P2
effort: M
status: done
classes: defect
feature: interface-areas
touches: src/anesthesia_sim/app/area_layout.py, tests/integration/test_layout_adapter.py
added: 2026-11-01
closed: 2026-11-16
pr: 2169
payoff: a border drag stops where the neighbouring Area reaches the size it needs, so the stored layout matches what is drawn
verify: grep -q 'def test_a_drag_stops_where_an_area_in_a_nested_split_reaches_its_views_need' tests/integration/test_layout_adapter.py
reenters: PL-16BG
---

**Problem.** AreaLayout._fits, which stops a border drag and lights the WARNING line, still estimates each Area's drawn size as its window share minus one handle, not from the apportionment the splitters draw: the estimate ignores nested handles and overstates an Area whose split neighbour is held wider than its share, and two adapter tests pin the stop it gives, a handle's width short of the neighbour's need (found building PL-16BG)

**Why it matters.** Both errors overstate an Area's drawn size, so a drag can go past the point where an Area reaches its least size. Qt then holds the frame at its minimum, and the stored border no longer matches the drawn one. `PL-MH5T` and `PL-97WX` removed that mismatch from the other readers of the drawn size.

**Reproduced 2026-11-03, by reading; not run in Qt.** `_fits`'s docstring in `src/anesthesia_sim/app/area_layout.py` states both errors and names this item. `test_a_drag_stops_where_the_neighbour_reaches_its_views_declared_need` in `tests/integration/test_layout_adapter.py` pins the stop a handle's width short of the neighbour's need, as its comment says.

**Done when.** `_fits` reads each Area's drawn size from the apportionment the splitters draw. A test with a nested split, and one with a neighbour held wider than its share, shows the drag stopping where the neighbour reaches its least size. The two tests that pin the handle-width stop are rewritten to the new stop.

**Generator check.** An instance of `PL-16BG`'s fact, filed the day that head closed: the size an Area is drawn at. `_fits` is one more reader that works the drawn size out for itself (`reenters: PL-16BG`).

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. `AreaLayout._fits` already estimated an Area's drawn size as its share less one handle at `817a4d88` (`281045a3`, 2026-10-19), and Areas held wider than their share existed (`8ae7824c`).

**Done 2026-11-16.** `AreaLayout._fits` now reads each Area's size from `apportion` in `layout/sizing.py`, the one function that lays out the splitters (`settle` calls it, and `_parts_hold_the_floor` and `_drawn_position` read its result). It lays out the moved layout at the widget's size, with every other Area held at its `Fit.bounds` entry, as the splitters hold it. The Area being measured is given no bound of its own, because `apportion` would otherwise hold it at its least size whatever its fraction, so no drag would ever stop and the stored border would drift from the drawn one. Its size is then the one its fraction gives it once every handle and every held neighbour is counted. The floor of a too-small Area is still measured at that width (`PL-16BG`), and the rule that an Area already short at the start may stay as it was is unchanged.

Tests in `tests/integration/test_layout_adapter.py`: the two that pinned the handle-width stop are rewritten to the new stop. `test_a_drag_stops_where_a_neighbour_reaches_its_least_size_and_its_line_turns_warning` now expects 0.8 less Area 4's least width over the 792 px that the bottom row's three Areas share, and Area 4 drawn at exactly that width. `test_a_drag_stops_where_the_neighbour_reaches_its_views_declared_need` now expects 0.625 and sizes of 500 and 300 px. Two are new: `test_a_drag_stops_where_an_area_in_a_nested_split_reaches_its_views_need` (stop at 0.5, bottom row drawn 500, 300 and 200 px) and `test_a_drag_stops_where_an_area_reaches_its_least_size_beside_a_neighbour_held_wider` (Area 5 held at 300 px beside a 160 px share, stop at 0.8 - 0.8 × least / 500). Each expected value is worked out in the test from the fractions and the pixel count, and each tolerance is one pixel of the split, the rounding of `pixel_sizes`. Run against the code before the fix with `QT_QPA_PLATFORM=offscreen uv run pytest -q tests/integration/test_layout_adapter.py`, all four failed: "assert 0.627970007658005 == 0.63459595959...6 ± 0.00126263", "assert 0.618811845779419 == 0.625 ± 0.00125", "assert 0.4968502913202559 == 0.5 ± 0.001" and "assert 0.6296568481048734 == 0.5904 ± 0.0016". With the fix, the 351 tests in every test file that imports `area_layout` pass. Docs checked: `docs/INTERFACE.md`, `docs/ARCHITECTURE.md` (its tree line for `area_layout.py` says only that a drag stops at an Area's least size, which still holds) and `docs/MODEL.md`, none of which states how the stop is worked out.

The `verify:` command named a test that triage guessed on 2026-11-03. The test that pins the nested-split stop is `test_a_drag_stops_where_an_area_in_a_nested_split_reaches_its_views_need`, so the command now names it (2026-11-16).
