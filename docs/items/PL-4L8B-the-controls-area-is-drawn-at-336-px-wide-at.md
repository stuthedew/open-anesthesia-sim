---
id: PL-4L8B
title: The controls Area is drawn at 336 px wide at launch though its frame's minimumSizeHint is 590 px, so the first border move of any size jumps the chart Area by about 250 px
status: untriaged
feature: interface-areas
touches: src/anesthesia_sim/app/area_layout.py, tests/integration
added: 2026-10-19
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
