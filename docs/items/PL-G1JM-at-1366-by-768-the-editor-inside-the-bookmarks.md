---
id: PL-G1JM
title: At 1366 by 768 the editor inside the Bookmarks View makes the View about 660 px tall, so in Default and Induction most of the editor is below the Bookmarks Area's edge and the Area scrolls 504 and 517 px; consider a more compact editor or a larger share for the View (found in review of PL-D5J4, after PL-CHX0)
status: done
feature: interface-design-review
milestone: v0.6.23
added: 2026-11-22
closed: 2026-11-23
pr: 2285
tests: tests/integration/simulation_view/test_simulation_view_bookmarks.py::test_the_bookmarks_view_lists_each_mark_once, tests/integration/simulation_view/test_simulation_view_bookmarks.py::test_a_row_s_remove_button_removes_that_row_s_mark_and_no_other, tests/integration/simulation_view/test_simulation_view_bookmarks.py::test_each_remove_button_names_its_mark_to_a_screen_reader, tests/integration/simulation_view/test_simulation_view_bookmarks.py::test_a_double_click_on_a_remove_button_removes_one_mark
---

**Problem.** At 1366 by 768 the editor inside the Bookmarks View makes the View about 660 px tall, so in Default and Induction most of the editor is below the Bookmarks Area's edge and the Area scrolls 504 and 517 px; consider a more compact editor or a larger share for the View (found in review of PL-D5J4, after PL-CHX0)

**Fixed, 2026-11-23.** The View was tall because it listed every mark twice.
The forms held a second, selectable copy of each list, with a "Remove
selected" button under it, below the read-only lists at the top of the View.

1. **Each mark is now listed once, with its own Remove button on its row.**
   The forms only add marks, and their headings say so: "Add a time
   bookmark" and "Add a MAC target". Each Add button sits beside its form's
   name field. The field names of both forms share one width, so the fields
   line up. This follows the row-action pattern of the GOV.UK Design System's
   summary list
   (https://design-system.service.gov.uk/components/summary-list/, read in
   full to 39,930 of its 49,053 characters on 2026-11-23, no date shown),
   which adds visually hidden text to each row action "like ‘Change name’"
   so a screen reader names the row it affects. Each Remove button's
   accessible name here is "Remove" and the mark's row text. HMRC's "add to a
   list" pattern
   (https://design.tax.service.gov.uk/hmrc-design-patterns/add-to-a-list,
   read to 39,923 of 50,345 characters) shows the added items as a list with a
   remove link on each row, and the form to add another below the list.
2. **The select-then-remove hazard is gone by construction.** A Remove used
   to act on the selected row, so the View had to deselect after a removal
   (`PL-CHX0`), and a press with nothing selected showed "Select a mark to
   remove it." Now a press names its own row, so that refusal text is
   removed, and the dashboard no longer keeps a selected row. A removal goes
   through its own request, `ViewRequests.mark_remove`, with the row, and
   `MarkEntry` holds only what the forms hold.
3. **Measured offscreen**, the Default Workspace at 1366 by 768 with two time
   marks and one target: the View's least height fell from 688 px to 414 px
   under Inter, and from 672 px to 402 px under DejaVu Sans, the font CI
   draws with.
4. **Tests.** `test_the_bookmarks_view_lists_each_mark_once` counts each
   mark's name across every label, button and list widget in the View, and
   fails on the code before the fix with "assert 2 == 1".
   `test_a_row_s_remove_button_removes_that_row_s_mark_and_no_other` removes
   the middle of three marks of each kind.
   `test_each_remove_button_names_its_mark_to_a_screen_reader` checks the
   accessible names against the marks the test added. The tests that selected
   rows were rewritten to press a row's button, and the two that held the
   selection after a removal or a rebuild were removed with the selection.

5. **Blind review, two passes.** Both found that after a removal the mark
   below moves up into the pressed row, so a double-click removed two marks.
   Fixed: a press of a Remove button within the platform's double-click
   interval of the last removal from that list is ignored
   (`test_a_double_click_on_a_remove_button_removes_one_mark`, which fails
   on the code before the fix with "assert [900] == [600.0, 900.0]"). Baymard
   Institute recommends undo as the ideal guard against accidental presses
   and confirmation only where undo costs too much (Holst, "Handling
   Accidental Taps on Touch Devices", 2017,
   https://baymard.com/research-articles/handling-accidental-taps-on-touch-devices,
   read 2026-11-23). A removed mark can already be entered again in the form,
   so the guard is enough here, and an Undo is filed as `PL-5GX4`. Pass 1 also
   found that a row outside the marks was ignored in silence. It now raises,
   and the halt gate halts every run and says so. Pass 2 expected the new
   Remove buttons to come after the forms in the Tab order. Measured, they do
   not: `test_the_tab_key_visits_the_remove_buttons_before_the_forms_below_them`
   passes without any ordering code, and holds that order.

Files checked: `docs/INTERFACE.md` (the Bookmarks View paragraph and its note
for developers, both changed), `docs/ARCHITECTURE.md`, `docs/MODEL.md` and
`README.md` (nothing names the editor's lists). The on-screen wording changes
are control names and headings, which name no clinical value.
