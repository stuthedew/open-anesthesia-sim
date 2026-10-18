---
id: PL-CW51
title: A drift.yml interpreter job on CPython 3.15.0 printed 'pure virtual method called' and 'terminate called without an active exception' just before 100% while every test passed, so a C++ object is destroyed under a live Qt call somewhere in the suite (run 39167787757, job 117794282666, found timing PL-QT2J)
status: untriaged
added: 2026-10-18
---

**Problem.** A drift.yml interpreter job on CPython 3.15.0 printed 'pure virtual method called' and 'terminate called without an active exception' just before 100% while every test passed, so a C++ object is destroyed under a live Qt call somewhere in the suite (run 39167787757, job 117794282666, found timing PL-QT2J)

The two lines appeared at 21:40:35Z on 2026-10-18, in job 117794282666 of run
39167787757, which ran `-n auto` on CPython 3.15.0 with the newest PySide6
that `uv sync --upgrade` resolved. The summary line still read 9,423 passed and 2 skipped, and the job concluded
`success`. The other three jobs on 3.15.0 in that run did not print it. Which
test was running is not known: `-n auto` prints dots, not names. That a Qt
object outlived its C++ side is the usual cause of this message, but here it is
inferred, not shown.
