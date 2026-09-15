---
id: PL-TCR5
title: The chart hover answers the pointer's previous position and never re-answers a resting pointer while paused, because the direct sigMouseMoved slot reads the position the rate-limited proxy stored one event earlier
priority: P2
effort: S
status: ready
classes: defect, ux
feature: qt-port
touches: src/anesthesia_sim/app/qt_chart.py, tests/integration/test_qt_chart.py
added: 2026-09-15
verify: uv run pytest tests/integration/test_qt_chart.py && grep -q 'def test_the_hover_answers_the_point_under_the_pointer' tests/integration/test_qt_chart.py
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
