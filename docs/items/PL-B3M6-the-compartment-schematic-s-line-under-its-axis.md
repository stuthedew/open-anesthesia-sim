---
id: PL-B3M6
title: The compartment schematic's line under its axis top control scrolls out of sight with the View, while the control stays pinned above it
priority: P3
effort: S
status: ready
classes: defect
feature: schematic
touches: src/anesthesia_sim/app/views.py, src/anesthesia_sim/app/area_layout.py, tests/integration/test_compartment_schematic_view.py, docs/INTERFACE.md
deferred-from: v0.7.0 - new: PL-GWSY's review found it on 2026-11-28; not safety or science, and no user sees a wrong value from it, since the control shows the top in force (triage 2026-11-28)
added: 2026-11-28
filed-pr: 2368
payoff: a user who has scrolled the compartment schematic is still told, beside its axis top control, when the top was refused or will not be kept
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

The cost: an Area whose box has less spare height than the line (14 to 30 px at
the schematic's widths) shows the too-small notice while the line is shown,
which is `PL-GWTR`'s rule that containers are never drawn cut. Measured
2026-11-28 (offscreen platform, Inter and DejaVu Sans): in the Maintenance
Workspace, the one shipped Workspace that shows the schematic, the box has at
least 42 px spare at 1440 by 900 with two runs, and more at every larger size.
At 1366 by 768 with two runs the box is already too short without the line. So
only an Area a user has dragged to within 30 px of its least height meets the
cost. The item's first done-when asked that no Area swap the View because of
the line, and this placement replaces that clause with the measurement above.

**Generator check.** Not a generator. The schematic is the only View whose
pinned row holds a control (`views.py`'s `_panel_row` is called with a control
only there), so no other View has a line that could sit apart from its control.

**Done when.** The line under the schematic's axis top control stands in the
pinned row, so it is on screen at every scroll position of the View. A test
scrolls the View to its end, makes the line appear by a pick that cannot be
saved, and checks that the line is visible and outside the scroll box. A test
checks that the Area's legible height grows by the line's height while it shows
and returns when it clears. Every shipped Workspace that shows the schematic at
the sizes the shipped-Workspace tests use keeps showing it with the line shown.
