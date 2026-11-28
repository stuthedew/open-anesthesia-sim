---
id: PL-4XNT
title: The too-small notice hides an Area's pinned row too, so a schematic that a top that cannot be saved tips into the notice also hides the axis top control and the line that says why
status: untriaged
feature: schematic
touches: src/anesthesia_sim/app/area_layout.py
added: 2026-11-28
filed-pr: 2369
---

**Problem.** The too-small notice hides an Area's pinned row too, so a schematic that a top that cannot be saved tips into the notice also hides the axis top control and the line that says why

Found by both passes of `PL-B3M6`'s blind review (pass 1 should-fix, pass 2
optional), 2026-11-28. `AreaFrame._set_content_hidden` hides the pinned row
with the View while the too-small notice shows. Since `PL-B3M6`, the line
under the schematic's axis top control is in that row and counts in the
height the schematic needs. In an Area within the line's height (15 to 36 px)
of that height, a pick that cannot be saved, or a refused or unused saved top
at launch, replaces the whole schematic with the too-small notice. The
control and the line go with it, so the user does not read why the top will
not be kept, and cannot pick another top in that Area. The notice states the
size the View needs and how to give it that size, so no value is misread.
Measured 2026-11-28: the Maintenance Workspace at 1440 by 900 with two
compared runs leaves the box 21 px taller than the schematic needs in the
container's font, and the 21 px line fits exactly.

A route to weigh: keep the pinned row shown over the too-small notice, so the
unit lines, the control and the line stay in view. That changes how every
View with a pinned row looks while its Area is too small, so it needs a
source first (Blender's manual and the platform guides on a region too small
for its content).
