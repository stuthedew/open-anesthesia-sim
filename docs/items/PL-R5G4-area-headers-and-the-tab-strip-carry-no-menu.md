---
id: PL-R5G4
title: Area headers and the tab strip carry no menu buttons: the Area and Layout menus open on a right-click or the Menu key, as Blender's header and tab menus do, Ctrl and a corner drag swap two Areas, and the View chooser's arrow no longer overlaps its title
priority: P2
effort: M
status: done
classes: feature, ux
feature: interface-areas
milestone: v0.6.0
touches: src/anesthesia_sim/app/, tests/integration, docs/interface-provenance.md, docs/ARCHITECTURE.md
added: 2026-10-19
closed: 2026-10-19
pr: 1668
payoff: the Area headers and the tab strip show only what the reader is looking at, as in Blender, and every layout operation still works by drag, right-click and keyboard
verify: uv run pytest -q 'tests/integration/test_layout_adapter.py::test_a_right_click_on_the_header_or_its_chooser_opens_the_area_menu' 'tests/integration/test_layout_adapter.py::test_ctrl_and_a_corner_drag_into_another_area_previews_a_swap_and_makes_it_on_release' 'tests/integration/test_layout_keyboard.py::test_the_strip_holds_no_layout_button_and_a_right_click_beside_the_tabs_opens_the_menu'
---

**Problem.** Area headers and the tab strip carry no menu buttons: the Area and Layout menus open on a right-click or the Menu key, as Blender's header and tab menus do, Ctrl and a corner drag swap two Areas, and the View chooser's arrow no longer overlaps its title

**Why it matters.** The project owner test-drove `main` at `0.5.42+g312f4a70`
on 2026-10-19 and found the header controls "overlapping and intrusive". Each
Area header carried an "Area" button with a drop-down arrow, and the tab strip
carried a "Layout" button. On his screen the arrows overlapped the labels.
They also sat beside the Area corner grips. Blender's headers carry no such
button. Its Area operations are on a right-click of the header or a border,
and its Workspace operations are on a right-click of a tab (Blender Manual,
"Areas", "Regions" section "Header", and "Workspaces", read 2026-10-19). Corner drags
to split and to join were already built here (`PL-2KXB`, `PL-30L5`), so the
buttons were a second, louder route to the same operations.

**Decision (project owner, 2026-10-19, ratified, over removing every menu,
which would break the v0.6.0 rule that each layout operation works from the
keyboard, and over keeping the buttons and fixing only the arrow).** He chose
"Blender-style" on a card in the thread "header menu arrows". The Area and
Layout menus keep their entries and lose their buttons. They open on a
right-click, and on the Menu key or Shift+F10 for a keyboard reader, so
`PL-M352`'s keyboard routes still hold. Ctrl and a corner drag swap two Areas,
as in Blender's "Swapping Contents". The View chooser stays, as Blender's
Editor Type selector does. The comparison he read is in
`/mnt/project-files/v0.6.0/area-header/blender-comparison.md`.

*Placeholders* (the 2026-10-18 rule on look, wording and placement): which
part of the strip opens the Layout menu, which entries the tab menu repeats,
and the chooser's arrow size and gap.

**Done when.**

1. No Area header holds an Area menu button, and the tab strip holds no
   Layout button.
2. A right-click on an Area header, or the Menu key or Shift+F10 on its View
   chooser, opens the Area menu with every entry it had before.
3. A right-click on the tab strip outside a tab opens the Layout menu. A tab's
   own menu also holds Previous and Next Workspace, Save as default, Restore
   shipped Workspaces and Reset all layouts, so the keyboard reaches them.
4. Ctrl and a corner drag from one Area to another previews and makes a swap.
5. The View chooser's arrow sits to the right of its title and does not overlap
   it.
6. `tests/integration/test_layout_keyboard.py` still drives every layout
   operation with key presses alone, and `docs/interface-provenance.md`
   records the change.

**Regression check (test-oracles rule 6, 2026-10-19).** The new tests were
copied into an `origin/main` worktree (`5df2f841` plus `PL-80R5` and `PL-40PL`)
and run with `PYTHONPATH` set to that worktree's `src`:

```
pytest -q tests/integration/test_layout_adapter.py -k "right_click or ctrl_and or swap_in_primary or holds_the_chooser or arrow_sits" tests/integration/test_layout_keyboard.py::test_the_strip_holds_no_layout_button_and_a_right_click_beside_the_tabs_opens_the_menu
```

All eight failed there. The arrow test failed under both styles with
`assert (77 - 75) > 4` (Fusion) and `assert (76 - 75) > 4` (Windows): the
arrow's ink started one or two pixels after the title's. The right-click test
failed with `assert not True`, because the old header button stayed visible.
The strip test failed with `At index 3 diff: 'Layout' != 'Maintenance'`. The
mouse-driven Ctrl drag failed with `'JoinPreview' == 'SwapPreview'`, using a
variant that compares the preview's class name, since `SwapPreview` does not
exist before the fix. The two swap tests that call
`corner_pressed(..., swap=True)` need that argument, which the fix added, so
the mouse-driven test is their variant.
