---
id: PL-4L8B
title: The controls Area is drawn at 336 px wide at launch though its frame's minimumSizeHint is 590 px, so the first border move of any size jumps the chart Area by about 250 px
priority: P3
effort: S
status: ready
classes: defect, ux
feature: interface-areas
touches: src/anesthesia_sim/app/area_layout.py, tests/integration
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-19
payoff: the dashboard opens at the width it keeps, so a border move moves the border by what was asked and a layout test measures only the move
verify: grep -q 'def test_the_controls_area_has_its_least_width_from_the_first_frame' tests/integration/test_layout_keyboard.py
---

**Problem.** The controls Area is drawn at 336 px wide at launch though its frame's minimumSizeHint is 590 px, so the first border move of any size jumps the chart Area by about 250 px

**Found 2026-10-19, while building `PL-M352`.** In the shipped dashboard at
1400 by 1000, the Area holding the controls has a frame whose
`minimumSizeHint()` is 590 px wide while its `minimumSize()` is 220 px. The
splitter draws it at 336 px at launch. Any move of the root border, by a 20 px
drag on `main` or one arrow-key step on the `PL-M352` branch, then lays the
splitter out again and gives that Area its 590 px hint, so the chart Area
shrinks from 1010 px to 756 px in one move. The reader asked for 20 px and
got about 250 px.

The likely cause (inferred, not traced) is that `PL-K285`'s least size reads
one of these two numbers and the splitter reads the other. Either the launch
layout should already honour the 590 px, or the least size should be the
220 px the frame declares. `tests/integration/test_layout_keyboard.py`'s
dashboard test asserts model fractions instead of pixels, so it passes either
way.

To reproduce, build `SimulationView` at
1400 by 1000, print each Area frame's `minimumSizeHint()` and
`minimumSize()`, then print the splitter's `sizes()` before and after one
`Key_Left` on the focused root border.

**Reproduced 2026-10-19, and the jump is not caused by the move.** On `main`
at `1e5cb9bd`, a `SimulationView` with one run at 1400 by 1000, offscreen,
gave these root splitter sizes and Area frame `(minimumSize, minimumSizeHint)`
widths:

| Moment | `sizes()` | chart Area | controls Area |
| --- | --- | --- | --- |
| after `show()` | 1010, 336 | 420, 415 | 220, 0 |
| after `present(False)` | 1010, 336 | 420, 438 | 220, 590 |
| after one `processEvents()` | 756, 590 | 438, 438 | 590, 590 |

So the controls Area's hint is 0 until the first frame builds its per-run
copies, and the splitter takes the new 590 px at the next pass of the event
loop. A test that sends a key or a drag before that pass, as
`_dashboard` in `tests/integration/test_layout_keyboard.py` does, sees the
jump land on its own move. In the running app the event loop runs at once, so
a reader most likely sees the narrow layout for at most the first frame
(inferred, not observed on screen).

**Why it matters.** A test of a border move measures the late relayout as
well as the move, which is why `PL-G5SX` records its widening drag as shorter
than its narrowing one. A reader may see the chart Area change width once at
launch. `PL-PHPZ` is the same mechanism on the vertical axis: a View that
fills in on its first frame changes its Area's hint after the layout has
already been sized. Fixing both at the point where a frame changes a hint is
likely one change; `PL-MXMG` may be a third case, and if its cause turns out
to be this one the three are a generator.

**Done when.** The splitter sizes after the first `present` already equal the
sizes after the next event-loop pass, so no border move follows a relayout. A
test in `tests/integration/test_layout_keyboard.py` asserts the controls
Area's pixel width straight after the first frame, and a one-step move then
changes it by `AREA_KEYBOARD_STEP` and no more.
