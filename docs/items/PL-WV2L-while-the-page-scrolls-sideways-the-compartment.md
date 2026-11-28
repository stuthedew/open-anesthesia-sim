---
id: PL-WV2L
title: While the page scrolls sideways, the compartment schematic's pinned row can grow by a wrapped line under its axis top control, and the Area does not check again that its box still shows a whole row of containers
status: untriaged
feature: schematic
touches: src/anesthesia_sim/app/pinned_heading.py, src/anesthesia_sim/app/area_layout.py
added: 2026-11-28
filed-pr: 2369
---

**Problem.** While the page scrolls sideways, the compartment schematic's pinned row can grow by a wrapped line under its axis top control, and the Area does not check again that its box still shows a whole row of containers

Found by pass 2 of `PL-B3M6`'s blind review (should-fix), 2026-11-28.
`PinnedHeadingSection` draws an Area's header and pinned row narrower while
the page scrolls sideways, down to the widest line's least width. Since
`PL-B3M6`, the schematic's pinned row holds the line under its axis top
control, which wraps, so the heading takes its height from `heightForWidth`
at the drawn width (`_height_at`). Drawn narrower, the line can take one more
row, and the heading and the space reserved under it grow by that row. The
box that scrolls the View then gets shorter. `AreaLayout._legible_need`
measures the row at the Area's full width, and no settle follows a sideways
scroll. So a box that was just tall enough can become too short to show a
whole row of containers, and the containers are drawn cut (`PL-GWTR`).

It needs four things at once: a layout of Areas wider than the window, which
no shipped Workspace makes at 1024 by 768 or larger (`PL-BQB6`'s
measurement); the line shown, which takes a refused, unsaved or unused saved
top; a box within one text row (14 to 15 px) of the schematic's legible
height; and a sideways scroll. Measuring the row at its least width instead
was tried in `PL-B3M6` and refused: it tips the Maintenance Workspace at 1440
by 900 with two compared runs into the too-small notice in the container's
font whenever the line shows.

Whatever `PL-BQB6` decides for lines cut by a sideways scroll decides this
too. With an ellipsis, the line keeps its rows while slid. With wrapping, the
Area has to check its box again when the heading grows.
