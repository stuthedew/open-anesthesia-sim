---
id: PL-Q740
title: The schematic's tests still pass if the compartment names leave the run's heading, a name or value is painted over another compartment's container, or the heading stops hiding the rows under it or stops moving with its section
priority: P1
effort: S
status: done
classes: defect, safety
feature: presentation-safety
touches: tests/integration/test_compartment_schematic_view.py, tests/integration/test_pinned_heading.py, ROADMAP.md
added: 2026-11-27
closed: 2026-11-27
pr: 2337
filed-pr: 2337
payoff: a later change that moves a compartment's name off its heading, paints a value under the wrong compartment, or lets rows show through a run's name fails a test
tests: tests/integration/test_compartment_schematic_view.py::test_each_name_and_label_line_is_painted_in_its_own_container_s_column, tests/integration/test_pinned_heading.py::test_the_heading_hides_the_rows_scrolled_under_it, tests/integration/test_pinned_heading.py::test_a_section_moved_inside_its_box_moves_its_own_heading, tests/integration/test_compartment_schematic_view.py::test_no_value_is_in_view_without_its_run_and_compartment_at_any_scroll_position
---

**Problem.** The schematic's tests still pass if the compartment names leave the run's heading, a name or value is painted over another compartment's container, or the heading stops hiding the rows under it or stops moving with its section

**What the review found** (the review of `PL-3NGZ`'s tests after it merged,
2026-11-27, offscreen platform). Each change below to `PL-3NGZ`'s code passed
every test that touches the schematic, and a scratch script showed what a user
would see.

1. The compartment names moved out of the run's heading, into the rows above
   the containers. A tension then stays in view after its compartment's name
   has scrolled away. The scroll tests read the heading's own rectangle and
   never asked whether the names stood in it.
2. Each name, or each label line, painted in the mirrored container's cell.
   "Fat" then stands over the circuit. The test of names over containers
   compares the cells that `name_cell` and `container` return, and nothing
   read where the strings are painted.
3. The heading no longer raised over the rows, or no longer given its own
   surface. Rows then show through the run's name. The scroll tests count a
   value under the heading as hidden, and nothing checked that it is.
4. `PinnedHeadingSection.moveEvent` no longer moving the heading. A section
   moved down, by the run above it growing a line, then shows rows above its
   own heading.

**Fix.** Four tests.

1. The scroll tests in `tests/integration/test_compartment_schematic_view.py`
   now require the run's name, the share caption and the compartment names to
   stand in the heading, and to be in view wherever a value is seen
   (`_qualifiers`).
2. `test_each_name_and_label_line_is_painted_in_its_own_container_s_column`
   compares the pixels of each name's and each label line's cell with that
   cell cleared and painted with its own string alone. Probed with every
   other string of the same row in each cell, it told all 120 wrong
   placements from the 24 right ones.
3. `tests/integration/test_pinned_heading.py` builds sections from rows
   painted solid in `INK`. `test_the_heading_hides_the_rows_scrolled_under_it`
   requires the heading's pixels to be the same with rows under it as with
   none.
4. `test_a_section_moved_inside_its_box_moves_its_own_heading` moves a section
   down, without a resize or a scroll, and requires its heading at the top of
   its new part in view.

**Run against each change** (`.venv/bin/pytest -q` on the tests named, with the
change applied to the source and then reverted):

| Change | Failing test |
| --- | --- |
| Names moved out of the heading | `test_no_value_is_in_view_without_its_run_and_compartment_at_any_scroll_position` |
| Names painted in the mirrored cell | `test_each_name_and_label_line_is_painted_in_its_own_container_s_column` |
| Label lines painted in the mirrored cell | the same |
| `self.heading.raise_()` removed | `test_the_heading_hides_the_rows_scrolled_under_it` |
| The heading's surface stylesheet removed | the same |
| `pin_heading()` removed from `moveEvent` | `test_a_section_moved_inside_its_box_moves_its_own_heading` |

The last row needed room under the sections. Without it, the section above
grew into the space of the one below, which was resized as well as moved, so
its `resizeEvent` moved the heading and hid the gap.

**A fifth gap, from the pull request's review.** The three scroll tests
checked that a run's heading was in view wherever its values were, and not
that the values stood below it. A heading left partway down its section shows
the rows above it directly under the run above, where they read as that run's
values. Each seen value must now stand below its own run's heading
(`_heading_in_view`, and the same check in
`test_no_value_is_in_view_without_its_run_and_compartment_at_any_scroll_position`).
The schematic's tests still pass with `pin_heading()` removed from
`moveEvent`, because their runs are paused and no section moves without a
scroll. The plain-widget test in the table's last row catches it.

**Nearest string, not an exact copy (2026-11-27).** The painted-cell test
first held each cell to an exact copy of the cell painted with its own string.
That passed here under both fonts and failed on CI's ARM runner at the first
name, "Circuit", in run 46078107422 of the pull request. The cause cannot be
seen from this container. The test now paints each string of the cell's row in
the cell in turn, and nothing, and requires the painted cell to be nearest to
its own string, by the summed difference of its colour bytes. Each change in
the table's second and third rows still fails it under both fonts, and so do
two more: two names swapped, and names not painted at all.

**Two findings not taken.** The review found that removing
`ViewScroll._pin_headings` from a resize changed no test, and could not
show a resize that needs it. It stays: since `PL-H55Q`, a change of range also
moves the headings, so the call costs one pass and removing it would change no
behaviour a test could show. The review also found that the horizontal scroll
bar's connection in `pin_on_scroll` re-applies the same heading geometry. It
stays, because the fix for `PL-DKQ5`'s sideways case moves the heading on a
sideways scroll and needs it.

**Gate.** Placed on v0.7.0's frozen list beside `PL-3NGZ`, which it completes,
as `PL-H55Q` is.

**Generator check.** No generator. Each gap is a test that read a rectangle or
a string the code reports instead of what is painted. `PL-0G2P` made the
schematic report what it paints; these tests now read the pixels where the
report could differ from them.

**Done when.** Each change in the table fails a test.
