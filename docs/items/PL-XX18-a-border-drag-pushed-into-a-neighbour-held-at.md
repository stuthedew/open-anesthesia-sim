---
id: PL-XX18
title: A border drag pushed into a neighbour held at its View's need leaves the border where it is drawn but does not turn its line WARNING, though border_moved's docstring says the line turns WARNING where an Area beside it reaches the least size it can be drawn at (found reviewing #1880)
priority: P3
effort: S
status: ready
classes: defect
feature: area-layout-sizing
touches: src/anesthesia_sim/app/area_layout.py, tests/integration/test_layout_adapter.py
deferred-from: v0.7.0 - filed after the gate froze; a missing WARNING cue on a drag, with no clinical value or stored state at stake
added: 2026-10-27
payoff: a drag that hits a held neighbour shows the WARNING line, as a keyboard step does, so a border that will not move says why
verify: grep -q 'def test_a_drag_into_a_held_neighbour_lights_the_border_warning' tests/integration/test_layout_adapter.py
reenters: PL-97WX
---

**Problem.** A border drag pushed into a neighbour held at its View's need leaves the border where it is drawn but does not turn its line WARNING, though border_moved's docstring says the line turns WARNING where an Area beside it reaches the least size it can be drawn at (found reviewing #1880)

**Why it matters.** The WARNING line is the only sign a learner gets that a
drag has reached a limit. Without it, a border that will not move looks stuck
or broken, and nothing says that the neighbouring View is already at the
least size it can be drawn at. The cause is in `border_moved`: since #1880,
`_position_at` returns `None` when the pointer's share would draw the border
where it already is, and `border_moved` then returns before it sets
`_at_minimum`. `border_stepped` handles the same case by setting
`_at_minimum` and relighting the line, so the keyboard and the pointer now
disagree about one state.

**Done when.** A drag that cannot move the border because a neighbour is held
at its View's need turns the line WARNING, as a keyboard step into the same
neighbour does. `tests/integration/test_layout_adapter.py` has
`test_a_drag_into_a_held_neighbour_lights_the_border_warning`, which drags
into such a neighbour and asserts that the line is WARNING and that the stored
fractions are unchanged.

**Generator check.** A re-entry of `PL-97WX`, the drag that mapped the pointer
linearly while the splitters drew settle's held sizes. Its fix in #1880 moved
the pointer onto the drawn sizes, but covered only the case where the border
moves. The fact misread is where a border is drawn, which `_drawn_position`
now owns. This item and `PL-MH5T` are the two places that fix left out.
