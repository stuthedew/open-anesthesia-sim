---
id: PL-MH5T
title: In a window smaller than the Areas' floors, a press on a border and a zero-pixel move still rewrite the stored fractions and emit layout_changed, because _drawn_position maps the pointer through settle's apportionment while Qt draws the frames at their larger minimum sizes; reproduced as root fractions (0.4026, 0.4647, 0.1328) becoming (0.4026, 0.3492, 0.2482) with the screen unchanged (found reviewing #1880)
priority: P2
effort: S
status: ready
classes: defect
feature: area-layout-sizing
touches: src/anesthesia_sim/app/area_layout.py, tests/integration/test_layout_adapter.py
deferred-from: v0.7.0 - filed after the gate froze; it needs a window smaller than every Area's floor, and it changes a layout, not a displayed value
added: 2026-10-27
payoff: a press on a border in a too-small window no longer rewrites the learner's saved arrangement with nothing visible changing
verify: grep -q 'def test_a_press_in_a_window_below_the_floors_keeps_the_stored_fractions' tests/integration/test_layout_adapter.py
reenters: PL-97WX
---

**Problem.** In a window smaller than the Areas' floors, a press on a border and a zero-pixel move still rewrite the stored fractions and emit layout_changed, because _drawn_position maps the pointer through settle's apportionment while Qt draws the frames at their larger minimum sizes; reproduced as root fractions (0.4026, 0.4647, 0.1328) becoming (0.4026, 0.3492, 0.2482) with the screen unchanged (found reviewing #1880)

**Why it matters.** The stored fractions are the learner's arrangement of the
workspace, and they are saved with it. Here a press on a border, with no
visible change, rewrites them. When the window grows past the floors again,
the Areas come back at sizes the learner never chose, and nothing on screen
explained the change when it was made. The cause is that `_drawn_position`
maps the pointer through settle's apportionment. Below the floors, Qt draws
each frame at its larger minimum size instead, so the two disagree about where
the border is.

**Done when.** In a window smaller than the Areas' floors, a press on a border
and a move of zero pixels leave the stored fractions unchanged and emit no
`layout_changed`. Either the pointer is mapped through the sizes Qt actually
draws, or a drag is refused while the layout cannot be held.
`tests/integration/test_layout_adapter.py` has
`test_a_press_in_a_window_below_the_floors_keeps_the_stored_fractions`,
starting from the reproduced root fractions (0.4026, 0.4647, 0.1328).

**Generator check.** A re-entry of `PL-97WX`, at the sibling site that its
fix in #1880 did not cover: the window too small for even the floors, where
settle's apportionment and Qt's drawn sizes part. The fact misread is where a
border is drawn. `PL-XX18` is the other site.
