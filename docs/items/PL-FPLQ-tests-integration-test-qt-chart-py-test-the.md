---
id: PL-FPLQ
title: tests/integration/test_qt_chart.py::test_the_hover_answers_the_point_under_the_pointer failed in make check under a load average of about 30 on four cores, reading the previous point's hover, and passed alone in 2.9 s: _wait_for_hover gives delivery only _HOVER_DELIVERY_MS = 1000 ms of wall-clock time
priority: P2
effort: S
status: ready
classes: defect
touches: tests/integration/test_qt_chart.py
added: 2026-10-24
payoff: the hover test stops failing on a loaded container, so a red Qt test in make check means something again
verify: ! grep -q '^_HOVER_DELIVERY_MS = 1000$' tests/integration/test_qt_chart.py
---

**Problem.** tests/integration/test_qt_chart.py::test_the_hover_answers_the_point_under_the_pointer failed in make check under a load average of about 30 on four cores, reading the previous point's hover, and passed alone in 2.9 s: _wait_for_hover gives delivery only _HOVER_DELIVERY_MS = 1000 ms of wall-clock time

Observed 2026-10-24 on `claude/triage-7fpd-88hc-646j`, a branch that changes only item files, while other sessions shared the container. The assertion read "Modelled sevoflurane · 5m ... 1.45%   0.73 ×MAC" where the test expected the 15-minute point, "2.40%   1.20 ×MAC". The same test passed when run alone.

**Why it matters.** A test that fails under load and passes alone turns `make check` red on a branch that changed nothing it reads, here a branch that changed only item files. Each such failure costs a session a re-run and an investigation, and teaches it to read a red Qt test as noise. `_HOVER_DELIVERY_MS` is a wall-clock limit, and wall-clock time is what a loaded container runs short of. `QTRY_COMPARE`, the Qt idiom `_wait_for_hover` copies, waits 5000 ms by default. The constant is also used at line 870 as a fixed hold, so raising it there would lengthen that test.

**Done when.** `_wait_for_hover` waits up to Qt's `QTRY_COMPARE` default of 5000 ms, still returning as soon as the hover matches, and the hold at line 870 has a constant of its own so its duration is unchanged. The line `_HOVER_DELIVERY_MS = 1000` is gone from `tests/integration/test_qt_chart.py`.
