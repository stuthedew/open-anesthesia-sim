---
id: PL-5GX4
title: Offer Undo after a mark is removed in the Bookmarks View, so an accidental removal can be reversed in one press rather than by entering the mark again (Baymard: undo is the ideal guard against accidental presses; found in PL-G1JM's review)
status: done
feature: interface-design-review
added: 2026-11-23
closed: 2026-11-23
pr: 2288
filed-pr: 2285
tests: tests/integration/simulation_view/test_simulation_view_bookmarks.py::test_undo_puts_a_removed_mark_back_in_its_row_in_every_run, tests/integration/simulation_view/test_simulation_view_bookmarks.py::test_undo_goes_back_through_several_removals_the_latest_first, tests/integration/simulation_view/test_simulation_view_bookmarks.py::test_a_mark_added_after_a_removal_ends_the_offer_to_undo_it, tests/integration/simulation_view/test_simulation_view_bookmarks.py::test_an_undone_removal_of_a_target_a_branch_reached_still_says_it_was_reached, tests/integration/controller/test_controller_marks.py::test_a_reached_target_put_back_after_its_removal_reads_reached_where_it_was, tests/integration/controller/test_controller_marks.py::test_a_target_put_back_after_a_reset_reads_as_the_new_run_has_it, tests/unit/test_bookmarks.py::test_a_mark_put_back_lands_at_its_position_or_at_the_end
---

**Problem.** Offer Undo after a mark is removed in the Bookmarks View, so an accidental removal can be reversed in one press rather than by entering the mark again (Baymard: undo is the ideal guard against accidental presses; found in PL-G1JM's review)

**Research, 2026-11-23.** Pages read in full this session, through a web
fetch:

1. Rosala, "User Control and Freedom (Usability Heuristic #3)", Nielsen
   Norman Group, 2020-11-29: "Support undo and redo", give "a visible option
   to undo an action on the UI", and support several undos where actions come
   in quick succession. It criticises a Google Drive undo message that "only
   appears for a few seconds".
2. Nielsen, "Confirmation Dialogs Can Prevent User Errors — If Not Overused",
   Nielsen Norman Group, 2018-02-18: keep confirmations for actions that
   cannot be undone, and "do not use confirmation dialogs for routine
   actions".
3. Ponamariov, "How To Manage Dangerous Actions In User Interfaces", Smashing
   Magazine, 2024-09-27: put the undo "close to the button that evokes the
   action", where it is noticed.
4. W3C, Understanding WCAG 2.2 Success Criterion 2.2.1 Timing Adjustable
   (updated 2026-08-10): a time limit includes "the expiration of a window of
   opportunity for a user to react", and a message that disappears after a
   few seconds must meet the criterion unless the reader has another way.
5. Apple, Human Interface Guidelines, "Undo and redo" (the page's Markdown
   form): help people predict the result, name what is undone, and "let
   people undo multiple times".

The Material Design snackbar page returned only a script shell and was not
read.

**Built, 2026-11-23.** After a removal, a line under the list names the
removed mark ("Removed: 10m"), beside an Undo button whose accessible name
names the mark ("Undo removing 10m"). The offer has no time limit, which
follows sources 1 and 4. Undo goes back through several removals, the latest
first, which follows sources 1 and 5. An Undo is offered only while the
marks are the ones the removal left and the same runs are on screen, so it
never reverses one edit on top of a later one. The dashboard keeps the
removals (`SimulationView._latest_removal`). Each run gives back a record of
the mark it removed (`RemovedMark`) and puts it back itself
(`SimulationController.restore_mark`), at its old row
(`BookmarkSet.with_time_bookmark_at`, `with_mac_target_at`). A target the run
had reached reads as reached again, unless the run was started over or its
agent changed in between. The Undo button keeps the Remove buttons'
double-click guard, because after an Undo the button can offer the removal
before it in the same place.

No keyboard shortcut was added. The application has no Edit menu and no
undo for any other action, so a Ctrl+Z bound to marks alone would act on
marks wherever the focus was. An application-wide undo is a larger feature
than this item.

Mutation checks: with the restored standing dropped (`same_run = False`),
`test_a_reached_target_put_back_after_its_removal_reads_reached_where_it_was`
and
`test_an_undone_removal_of_a_target_a_branch_reached_still_says_it_was_reached`
fail. With the run check dropped (`same_run = removed.reached`),
`test_a_target_put_back_after_a_reset_reads_as_the_new_run_has_it` fails. The
reached tests let the run go on past its halt, because while a run stands on
its halt the halt alone shows the target as reached.
