---
id: PL-4JCC
title: The shipped Workspaces give the Parameters View an Area far taller than its content: 590 by 665 px in Default and 590 by 1083 px in Induction for about 90 px of controls (measured offscreen at 1920 by 1080, 2026-11-11), while no shipped Workspace but Maintenance shows a third View
priority: P3
effort: S
status: ready
classes: ux
feature: window-is-the-frame
touches: src/anesthesia_sim/data/workspaces/default.json, src/anesthesia_sim/data/workspaces/induction.json, tests/integration/test_simulation_view.py
added: 2026-11-11
payoff: at 1920 by 1080 the chart beside the Parameters View gets the height that the controls do not use
verify: grep -q 'def test_the_parameters_area_is_not_far_taller_than_its_controls' tests/integration/test_simulation_view.py
---

**Problem.** The shipped Workspaces give the Parameters View an Area far taller than its content: 590 by 665 px in Default and 590 by 1083 px in Induction for about 90 px of controls (measured offscreen at 1920 by 1080, 2026-11-11), while no shipped Workspace but Maintenance shows a third View

[superseded 2026-11-14] **Triaged, 2026-11-11: waits for `PL-CBYS`.** Since `PL-9YPR`, the column
that held Parameters alone is shared with Bookmarks and Branch in Default and
Induction, so the Parameters Area is about a third of the height it was.
`PL-CBYS` then changes every Area's height again. Measure once that has
landed, and close this item if the Area is no longer far taller than its
controls. Where the Views sit is a placeholder that the session decides.

**Why it matters.** Empty panel beside a chart is room the chart could use.

**Generator check.** A one-off: a placement chosen before a third View
existed to share the column.

**Measured after `PL-CBYS`, 2026-11-14** (offscreen font, one run at 300 s,
on `#2134`'s branch). The Parameters View's content needs 86 px. Its Area is
187 px tall at 1366 by 768 in every shipped Workspace, held at the View's
least height of 160 px plus the header. At 1920 by 1080 it is 266 px in
Default and Induction and 187 px in Maintenance, about 180 px more than the
controls in the first two. The Area is no longer the 665 px and 1083 px the
title records, but it is still about three times its content on a desktop
screen, so the item stays open.

**Done when.** At 1920 by 1080 the Parameters Area in Default and Induction
is no more than its View's least height plus the header, and the room it gives
up goes to the chart beside it. A test opens each shipped Workspace at that
size and checks the Area's height. The shares stay placeholders that the
building session decides.
