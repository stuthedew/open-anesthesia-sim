---
id: PL-B3M6
title: The compartment schematic's line under its axis top control scrolls out of sight with the View, while the control stays pinned above it
priority: P3
effort: S
status: done
classes: defect
feature: schematic
touches: src/anesthesia_sim/app/views.py, src/anesthesia_sim/app/area_layout.py, tests/integration/test_compartment_schematic_view.py, docs/INTERFACE.md
deferred-from: v0.7.0 - new: PL-GWSY's review found it on 2026-11-28; not safety or science, and no user sees a wrong value from it, since the control shows the top in force (triage 2026-11-28)
added: 2026-11-28
closed: 2026-11-28
pr: 2369
filed-pr: 2368
payoff: a user who has scrolled the compartment schematic is still told, beside its axis top control, when the top was refused or will not be kept
tests: tests/integration/test_compartment_schematic_view.py::test_the_line_under_the_axis_top_control_is_in_view_at_any_scroll_position, tests/integration/test_compartment_schematic_view.py::test_an_area_too_short_for_the_line_under_the_axis_top_control_shows_the_too_small_notice, tests/integration/test_compartment_schematic_view.py::test_a_narrower_window_counts_the_rows_the_line_under_the_axis_top_control_takes_there
---

**Problem.** The compartment schematic's line under its axis top control scrolls out of sight with the View, while the control stays pinned above it

The axis top control of `CompartmentSchematicView` sits in the View's
`pinned_row`, which its Area keeps above the box that scrolls the View. The
line under that control, `ceiling_notice`, is added to the scrolled column
instead, above the schematic heading. So a reader who has scrolled the
schematic down, for example to the second run of a comparison in a short
Area, and then picks a top sees no line at all. The line is above the part of
the View on screen. In a Workspace with the schematic and neither a
concentration chart nor an agent cost View, nothing on screen then says that
the saved top was refused, that the picked top could not be saved, or that
the preferences file is not in use.

The refused-top line has had this fault since `PL-7LZ7` put the control in
the pinned row. `PL-GWSY` added two more lines that take the same place, and
pass 2 of its blind review found the fault (should-fix). The concentration
chart View declares no pinned row, so its control and its line scroll
together and it does not have the fault.

**Why it was not fixed in `PL-GWSY`.** Moving the line into the pinned row
changes what the Area needs. `AreaLayout`'s legible-height arithmetic in
`app/area_layout.py` adds the pinned row's height to the View's
`legible_height`. A line that wraps onto more than one row there could tip a short
Area into the notice it shows in place of a View that is too small, at the
moment the line appears, which would hide every schematic value. So the fix
needs a placement that keeps the line on screen without that swap. Two to
weigh: the line in the pinned row with the legible height measured with it,
or the View scrolled to show the line when it appears. The second keeps the
Area's arithmetic. `ViewScroll` is a `QScrollArea`, whose
`ensureWidgetVisible` "Scrolls the contents of the scroll area so that the
childWidget of widget() is visible inside the viewport" (Qt for Python 6
documentation, `QScrollArea`,
https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QScrollArea.html, read
2026-11-28).

**Why it matters.** A user who has scrolled the schematic and picks a top
while saving is off, or after a failed save, is not told that the top will
reset at the next launch. The control itself shows the top in force, so no
user sees a wrong value, but the line that `PL-GWSY` put beside every control
is missing at the moment it is needed.

**Placement chosen** (triage 2026-11-28, decided from sources rather than
put to the owner, because one route is clearly better). The line moves into
the pinned row, under the line that holds the control, and the Area's legible
height counts it only while it is shown.

1. Nielsen Norman Group's error-message guidelines (Neusesser and Sunwall,
   2023-05-14, nngroup.com/articles/error-message-guidelines, read 2026-11-28
   with curl): "Display the error message close to the error's source", because
   "Proximity helps users associate the error message content with the
   interface elements needing attention." The control is pinned, so only a
   pinned line stays beside it.
2. The three conditions last a session or until the user picks a top. Scrolling
   the View to show a line at the top of the scrolled column shows it once, and
   it leaves the screen again at the next scroll. It also moves the user away
   from the run they scrolled to, whose containers they picked the top to read.
3. `.claude/rules/ui-reader.md` § "Standing text and conditional text":
   conditional text "costs nothing when the condition is false". So the legible
   height does not reserve room for the line while it is hidden.

The cost: an Area whose box has less spare height than the line and the gap
above it shows the too-small notice while the line is shown, which is
`PL-GWTR`'s rule that containers are never drawn cut. The line takes one row
(14 or 15 px, plus a 6 px gap) at every width the schematic's Area can have
in the container's font, Inter, and two rows at its least width in DejaVu
Sans, the CI font. A refused saved top quotes the file's value, so it can take
more. Measured 2026-11-28 (offscreen platform) in the Maintenance Workspace,
the one shipped Workspace that shows the schematic, with a top that could not
be saved:

1. With one run, the schematic stays shown at 1280 by 800, 1366 by 768, 1440
   by 900 and 1920 by 1080, in both fonts.
2. With two compared runs, it is already too short without the line at 1280
   by 800 and 1366 by 768, and stays shown with the line at 1920 by 1080.
3. With two compared runs at 1440 by 900, the box is 21 px taller than the
   schematic needs in Inter and 42 px in DejaVu Sans. The line takes 21 and
   20 px, so the schematic stays shown in both, with no pixel to spare in
   Inter.

The item's first done-when asked that no Area swap the View because of the
line, and this placement replaces that clause with the measurement above.
`PL-4XNT` records that the swap also hides the control and the line.

**Generator check.** Not a generator. The schematic is the only View whose
pinned row holds a control (`views.py`'s `_panel_row` is called with a control
only there), so no other View has a line that could sit apart from its control.

**Done when.** The line under the schematic's axis top control stands in the
pinned row, so it is on screen at every scroll position of the View. A test
scrolls the View to its end, makes the line appear by a pick that cannot be
saved, and checks that the line is visible and outside the scroll box. A test
checks that the Area's legible height grows by the line's height while it shows
and returns when it clears, and one that it counts the line's rows at the width
a resize draws it. At each size measured above, a shipped Workspace that
shows the schematic without the line keeps showing it with the line.

**Docs swept:** `docs/INTERFACE.md` § "The compartment schematic" (the
paragraph on the row above the scrolling part, now naming the line and the
too-small notice), § "The chart's fixed MAC axis" (the line's wording and
place, still true), § "An area's header and its view's pinned row stay in view
while the page scrolls the area" (still true; the sideways case is
`PL-WV2L`), `docs/ARCHITECTURE.md` (no mention of the pinned row's contents).

**Regression tests run before the fix.** With `src/` stashed, `uv run pytest
-q tests/integration/test_compartment_schematic_view.py -k axis_top_control`
failed both first tests: `assert not True` where the scroll box was an
ancestor of the line, and `ValueError: not enough values to unpack (expected
1, got 0)` where no too-small notice appeared. With only `views.py` changed,
the row was sized from its size hint: `assert 30 == 15` for the line's height
and `assert 237 == ((201 + 6) + 15)` for the needed height. The third test,
added for both review passes' first finding, passes with the row measured at
the frame's width as well. A window resize settles the Areas again after the
splitters take their new sizes, so the stale width the reviewers described
was not reproduced. The row is measured at the settled width anyway, as
`_floor` and `_narrowed` are.
