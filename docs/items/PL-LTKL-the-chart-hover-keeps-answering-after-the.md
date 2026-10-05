---
id: PL-LTKL
title: The chart hover keeps answering after the pointer leaves the plot: nothing clears the stored pointer position on a Leave event, so the box stays up and every later frame re-answers for a pointer that has gone
priority: P1
effort: S
status: done
classes: safety, defect
feature: qt-port
touches: src/anesthesia_sim/app/qt_chart.py, tests/integration/test_qt_chart.py, docs/MODEL.md
added: 2026-10-04
closed: 2026-10-05
pr: 1367
payoff: once the pointer leaves the chart, no modelled concentration stays on screen updating with the run, so a glance back cannot take a stale hover for the live state
verify: grep -q 'def test_the_hover_hides_when_the_pointer_leaves_and_a_later_frame_does_not_bring_it_back' tests/integration/test_qt_chart.py
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

**Reproduced 2026-10-04** on `main` at `8f24fe78`, headless
(`QT_QPA_PLATFORM=offscreen uv run python`): the paused run, frame and pointer
move `test_the_hover_answers_the_point_under_the_pointer` uses, then
`QApplication.sendEvent(chart._plot.viewport(), QEvent(QEvent.Type.Leave))`.
The box read `2.40%   1.20 ×MAC` over the circuit trace at 15m, and still read
it a second after the `Leave` and after a following `draw`; the wash-in plot,
on the same `_PointerMoves`, kept its `0.77` the same way. With the run
playing in a following 15-minute window, three frames drawn 30 s apart after
the `Leave` answered 13m9s `2.32%`, 13m39s `2.34%` and 14m9s `2.37%`: the
stored position, mapped through the moved view box, names a new instant each
frame. Nothing under `src/` or `tests/` handles `QEvent.Type.Leave`.

**Why it matters.** The box is a modelled concentration with its unit and MAC
multiple, and `docs/MODEL.md` § "When it answers" promises it "Whenever the
pointer is over the plot". Left up once the pointer has moved to the controls
or the readouts, it describes a point the reader is no longer looking at, and
while a run plays it climbs with the run, so a reader glancing back takes it
for a live readout of the state they are watching. A value shown for stale
state is one `CLAUDE.md`'s clinical-output standard treats as part of safety
even when the number is right for its point.

**Done when.** A `Leave` on either plot's viewport clears the stored pointer
position and hides the box, a following `draw` does not bring it back, and a
`Leave` arriving while a move waits out the cooldown drops that move rather
than letting `_deliver` put the box back up to 17 ms later. Held by
`test_the_hover_hides_when_the_pointer_leaves_and_a_later_frame_does_not_bring_it_back`
in `tests/integration/test_qt_chart.py`.

**Classed `safety`** (triage, 2026-10-04). A modelled concentration and MAC
multiple shown for an instant the reader is not looking at, and updating as
if live, is the stale-state presentation `CLAUDE.md`'s clinical-output
standard counts as a safety failure even where the number is right for its
point. `PL-TCR5`, on the same hover, was classed `defect, ux`; this does not
follow it, for that reason. Captured after v0.6.0's freeze, it joins the
gate's product lane under the `safety` exception.

**Fixed 2026-10-05.** `_PointerMoves` takes the viewport's `Leave` as well as
its moves. It drops the move waiting out the cooldown, stops the cooldown and
delivers `None` at once. Each chart's `_on_pointer` stores that through
`_HoverReadout.move_to`, and `_refresh_hover` already hid the box for a
position of `None`. It is one signal rather than a second one for leaving, so
the one-slot ordering `PL-TCR5` set up still holds. The signal is declared
`object`, because a signal declared `QPointF` and handed `None` delivers the
scene's origin with only a line on standard error (measured under PySide6 in
this container). The test failed on `main`'s code with the box still reading
`1.45%   0.73 ×MAC` after the `Leave`. Against a half-fix that left the
waiting move in place, both boxes came back after the cooldown, the
compartment chart's reading `2.40%   1.20 ×MAC`, the reviewer's own value.
`docs/MODEL.md` gains the hazard's row in § "Reasonably foreseeable misuse,
and the hazards the presentation carries" and a paragraph under § "When it
answers", which is why it joined `touches`.
