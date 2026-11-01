---
id: PL-CSK0
title: Under the drift run's upgraded dependencies, test_every_run_state_surface_outside_the_run_view_reads_alike_on_a_drawn_run_and_a_halted_one finds a QWidget that reads differently on a halted dashboard and on the same one drawn; it passes on uv.lock, so either a newer PySide6 exposes a real stale-state surface after a halt or the test reads a property the new Qt changed (drift run 41279184121, 2026-11-01)
status: untriaged
feature: restated-constants
added: 2026-11-01
---

**Problem.** Under the drift run's upgraded dependencies, test_every_run_state_surface_outside_the_run_view_reads_alike_on_a_drawn_run_and_a_halted_one finds a QWidget that reads differently on a halted dashboard and on the same one drawn; it passes on uv.lock, so either a newer PySide6 exposes a real stale-state surface after a halt or the test reads a property the new Qt changed (drift run 41279184121, 2026-11-01)

**Evidence.** The test failed in both the `dependencies` and `interpreter`
jobs of drift run 41279184121 with `assert ['QWidget'] == []`. The `order`
job, which runs the suite on `uv.lock` in random order, passed. The run of
2026-10-26 passed all three jobs. Which package moved has not been checked:
the `uv pip list --outdated` step's output is in the job log.

**Generator check.** Undecided until it is reproduced. If a real widget goes
stale after a halt, it is an instance of `PL-X7D5`'s fact and `PL-J5GC`'s
(what states a run's state, restated on every path that changes it). If the
new Qt only changed a property the test reads, it is a one-off in the test.
