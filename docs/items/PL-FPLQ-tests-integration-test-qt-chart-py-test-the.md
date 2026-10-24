---
id: PL-FPLQ
title: tests/integration/test_qt_chart.py::test_the_hover_answers_the_point_under_the_pointer failed in make check under a load average of about 30 on four cores, reading the previous point's hover, and passed alone in 2.9 s: _wait_for_hover gives delivery only _HOVER_DELIVERY_MS = 1000 ms of wall-clock time
status: untriaged
added: 2026-10-24
---

**Problem.** tests/integration/test_qt_chart.py::test_the_hover_answers_the_point_under_the_pointer failed in make check under a load average of about 30 on four cores, reading the previous point's hover, and passed alone in 2.9 s: _wait_for_hover gives delivery only _HOVER_DELIVERY_MS = 1000 ms of wall-clock time

Observed 2026-10-24 on `claude/triage-7fpd-88hc-646j`, a branch that changes only item files, while other sessions shared the container. The assertion read "Modelled sevoflurane · 5m ... 1.45%   0.73 ×MAC" where the test expected the 15-minute point, "2.40%   1.20 ×MAC". The same test passed when run alone.
