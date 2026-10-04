---
id: PL-LTKL
title: The chart hover keeps answering after the pointer leaves the plot: nothing clears the stored pointer position on a Leave event, so the box stays up and every later frame re-answers for a pointer that has gone
status: untriaged
feature: qt-port
added: 2026-10-04
---

**Problem.** The chart hover keeps answering after the pointer leaves the plot: nothing clears the stored pointer position on a Leave event, so the box stays up and every later frame re-answers for a pointer that has gone

**Found 2026-10-04 by the adversarial review of `PL-TCR5`'s pull request
(#1340), and older than it:** `main` behaves the same. A move over the axis
inside the widget is answered by hiding the box, because the stored position
falls outside the view box. A pointer that leaves the widget altogether sends
the plot no move, only a `Leave`, and nothing handles that. So the box stays
up at the last point, and `draw` re-answers the stored position on every
frame. The reviewer measured it re-answering `2.40%   1.20 ×MAC` for a
pointer that had gone. That is the stale-state failure `PL-TCR5`'s own brief
cites: a value answered for a place the reader is not looking. While a run
plays, the value moves with the run, so the box reads as live.

**Where the fix would go.** `_PointerMoves` in `app/qt_chart.py`, which since
`PL-TCR5` filters the plot viewport's events, can take `QEvent.Type.Leave` as
well: clear the stored position, then answer, which hides the box. The test
belongs in `tests/integration/test_qt_chart.py` beside
`test_the_hover_answers_the_point_under_the_pointer`, sending a `Leave` to the
viewport and asserting the box hides and that a following `draw` does not
bring it back.
