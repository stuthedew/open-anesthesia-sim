---
id: PL-TCR5
title: The chart hover answers the pointer's previous position and never re-answers a resting pointer while paused, because the direct sigMouseMoved slot reads the position the rate-limited proxy stored one event earlier
status: untriaged
added: 2026-09-15
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
