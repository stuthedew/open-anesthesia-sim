---
id: PL-B3M6
title: The compartment schematic's line under its axis top control scrolls out of sight with the View, while the control stays pinned above it
status: untriaged
feature: schematic
added: 2026-11-28
filed-pr: 2368
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

**Done when.** With the schematic scrolled down in a short Area, a line that
appears under the axis top control is on screen, and no Area swaps the View
for its too-small notice because of it. A test scrolls the View, makes the
line appear, and checks that the line is inside the visible part of the
scroll box.
