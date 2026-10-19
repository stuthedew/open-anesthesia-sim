---
id: PL-CW51
title: A drift.yml interpreter job on CPython 3.15.0 printed 'pure virtual method called' and 'terminate called without an active exception' just before 100% while every test passed, so a C++ object is destroyed under a live Qt call somewhere in the suite (run 39167787757, job 117794282666, found timing PL-QT2J)
priority: P3
effort: M
status: ready
classes: defect, test
feature: qt-teardown-crashes
touches: src/anesthesia_sim/app/, tests/integration
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-18
payoff: The suite stops destroying a Qt object under a live call, so the next interpreter upgrade does not arrive with a worker crash already in it
not-delegable: Reproducing it needs the drift job's CPython 3.15.0 with the newest PySide6, and the message is printed by a run that still passes, so no command run on the base interpreter can fail before the work and pass after it
---

**Problem.** A drift.yml interpreter job on CPython 3.15.0 printed 'pure virtual method called' and 'terminate called without an active exception' just before 100% while every test passed, so a C++ object is destroyed under a live Qt call somewhere in the suite (run 39167787757, job 117794282666, found timing PL-QT2J)

The two lines appeared at 21:40:35Z on 2026-10-18, in job 117794282666 of run
39167787757, which ran `-n auto` on CPython 3.15.0 with the newest PySide6
that `uv sync --upgrade` resolved. The summary line still read 9,423 passed and 2 skipped, and the job concluded
`success`. The other three jobs on 3.15.0 in that run did not print it. Which
test was running is not known: `-n auto` prints dots, not names. That a Qt
object outlived its C++ side is the usual cause of this message, but here it is
inferred, not shown.

**Why it matters.** The message means native code called a method on a C++
object that had already been destroyed. Here the process survived, but the same
fault can kill an xdist worker, as `PL-Q18P` (a worker crash on `main`'s quality
run) shows. On the CPython that `drift.yml` tests ahead of time, it is a
warning that the suite may fail once the project moves to it.

**Done when.** The test that prints the message is found, for example by
running the drift job's interpreter with `-p no:xdist -v`. Then either its Qt
object lifetime is fixed, with a test that would have caught it, or the item
records that the fault is in PySide6 on CPython 3.15, with the upstream
report. If `PL-Q18P`'s fix removes the message, close this item with that
evidence.
