---
id: PL-TCR5
title: The chart hover answers the pointer's previous position and never re-answers a resting pointer while paused, because the direct sigMouseMoved slot reads the position the rate-limited proxy stored one event earlier
priority: P2
effort: S
status: done
classes: defect, ux
feature: qt-port
touches: src/anesthesia_sim/app/qt_chart.py, tests/integration/test_qt_chart.py
added: 2026-09-15
closed: 2026-10-04
pr: 1340
verify: grep -q 'def test_the_hover_answers_the_point_under_the_pointer' tests/integration/test_qt_chart.py && uv run pytest tests/integration/test_qt_chart.py
---

**Problem.** The chart hover answers the pointer's previous position and never re-answers a resting pointer while paused, because the direct sigMouseMoved slot reads the position the rate-limited proxy stored one event earlier

**Found by the Qt-correctness review of `PL-25KS`, 2026-09-15; predates it
(`PL-G59B`).** `app/qt_chart.py` hangs two slots off `scene().sigMouseMoved`:
a rate-limited `pg.SignalProxy` that stores the pointer's position and is
delivered later through a timer, and a direct `_on_pointer` that reads the
stored position synchronously. So each pointer event answers the position the
previous flush stored: the first move into the plot answers nothing, every
later move answers the point under the previous event, and a pointer that
stops is answered only by the next `draw()` - within 200 ms while running,
never while paused. Text and dot agree with each other; both lag the pointer
by one event. Fix: let the proxy's own delivered slot both store the position
and refresh the hover (it already limits to 60 Hz), and drop the direct
connection; a headless test moves the pointer once and asserts the readout
names the point under it.

**Why it matters.** The hover readout is how a reader asks the chart what a
curve is worth at a given instant, so an answer that belongs to the previous
pointer position is a wrong clinical value presented with no sign that it is
wrong - the text and the dot agree with each other, which is exactly what makes
it convincing. `CLAUDE.md`'s presentation clause covers this directly: the
correct number against the wrong patient context or stale state is still a
safety failure, and a readout lagging the pointer by one event is stale state
the reader cannot see.

The paused case is the worse half. While running, the next `draw()` corrects the
answer within 200 ms, so the error is a flicker; while paused nothing redraws,
so a resting pointer keeps an answer for a point the reader is not looking at,
indefinitely. Paused is also when a reader is most likely to be reading values
off carefully rather than watching the trend.

**Done when.** The rate-limited proxy's own delivered slot both stores the
position and refreshes the hover, the direct `sigMouseMoved` connection is gone,
and a headless test moves the pointer once and asserts the readout names the
point under it - including with the run paused, where no `draw()` follows.

**Confirmed 2026-10-04, before the claim**, on the shipped dashboard under the
`offscreen` platform, sevoflurane five minutes in. `QTest.mouseMove` onto the
alveolar point at 100 s and `QTest.qWait(60)`: `hover_text()` was `None`. A
second move, to the point at 200 s, and the same wait: the hover read
`Modelled sevoflurane · 1m39.9s`, the first position. Taken with `PL-J0F7` on
one branch and first, because that item's test drives the real pointer to the
plot's edges and cannot pass while the hover answers the previous event.

**Built 2026-10-04, and a second way to the same stale answer found while
building it.** The proxy's own delivery now stores the position and calls the
chart's `_refresh_hover`, and both charts' direct `sigMouseMoved` connections
and their `_on_pointer` slots are gone. The test then showed the brief had one
mechanism of two: pyqtgraph 0.14.0's `GraphicsScene.mouseMoveEvent` passes on a
move only when `1000 / mouseRateLimit` ms - 10 ms as shipped - have passed
since the last one it passed on, and drops the rest with nothing delivered
after them. So whenever a pointer's last move came within 10 ms of the one
before - every other event from a 120 Hz device - the scene never emitted
where the pointer stopped, the proxy never saw it, and the hover answered a
move earlier, running or paused. Measured headless: two moves sent with nothing
between them, the hover kept the first. That is this item's own outcome
failing, so it was fixed here rather than filed (capture mode: a finding that
completes an in-progress item is not a new item). `_PointerMoves` reads every
move off the plot's viewport with an event filter and feeds the same proxy,
which still caps the lookups at sixty a second and always delivers the newest
position it holds. The process-wide `mouseRateLimit` was left alone: switching
it off would also unthrottle the scene's own hover dispatch to every item.

`test_the_hover_answers_the_point_under_the_pointer` moves the pointer with a
`QMouseEvent` sent to the widget under the pixel - `QTest.mouseMove` moves the
platform cursor, and the offscreen platform gave that move to another chart
left shown at the same screen position - onto three circuit-trace points more
than 30 px clear of the other five traces, the run paused: the first move
answers, each later one answers its own point, a pair of moves with nothing
between them answers the second, and a move over the axis hides the box. The
wash-in plot is held to one move. Each half fails when its fix is reverted:
restoring the direct slot gives `None` on the first move; feeding the proxy
from `sigMouseMoved` again gives the pair's first point (0.73 ×MAC) for its
second (1.11 ×MAC).
