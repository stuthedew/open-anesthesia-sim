---
id: PL-2R2C
title: A branch's drawn columns are anchored to its own zero, so most land at case instants the trunk never draws
status: untriaged
added: 2026-09-14
---

**Problem.** A branch's drawn columns are anchored to its own zero, so most land at case instants the trunk never draws

**Measured 2026-09-14, on the seam `PL-J2TD` landed.**
`RunDefinition.evaluate_anchored` anchors its grid to the definition's own
`t = 0` - deliberately, and `PL-Q197` is why: a grid anchored to the window
instead makes every drawn point a new instant on every frame, which is what
saturated the Flutter client at 2 700 control mutations a frame. A branch's
definition opens at the fork, so its columns land at `fork + m x spacing` while
the trunk's land at `m x spacing`.

Where the fork instant is itself a multiple of the spacing the two coincide and
nothing shows: a fork at 60.0 s drawn on a 13-column 120 s axis put all 7 of the
branch's columns on instants the trunk also drew. Move the fork off the grid -
55.3 s, an ordinary instant for a control change - and **2 of the branch's 8
columns** land where the trunk draws. The trunk draws 0, 10, ... 120 plus an
event column at 55.3; the branch draws 55.3, 65.3, 75.3, 85.3, 95.3, 105.3,
115.3, 120.

**Nothing here is wrong, which is why it needs deciding rather than fixing.**
Every column is a correct state at a correct instant, and each trace read alone
is right. What is missing is that the two traces are not sampled together, so a
learner cannot read "at this instant the trunk was here and the branch was
there" off matched points, and any overlay that assumes matched columns - a
difference trace, a table of both runs at one instant, a shared tooltip - would
be wrong rather than merely coarse.

**Whose problem it is.** `PL-B9PY` decomposes `SimulationView` so two runs can
be rendered at once, and this is the first thing that decomposition meets. Three
routes, and the choice is between them rather than obvious:

1. Anchor the grid to the *case* rather than to the definition, by passing the
   origin into `evaluate_anchored`. Keeps one column set for every run on the
   axis; costs a parameter on the display path.
2. Have the overlay ask each run for the other's column instants. Correct and
   exact, and it doubles the evaluation the frame costs.
3. `PL-ZMRT` - open a branch's definition at the fork instant, after which
   every definition on one axis shares one origin and the grids align for free.

Route 3 makes this vanish rather than solving it, which is a point in its
favour and an argument to decide `PL-ZMRT` first.
