---
id: PL-ZNPQ
title: Reference test modules other than the 24-hour washout file keep per-process caches that each xdist worker recomputes; measure what they cost before sharing any of them the way washout_curve does
status: untriaged
touches: tests/reference/test_published_wash_in_and_elimination.py, tests/reference/test_control_resolution.py, tests/reference/test_coupled_dynamics.py
added: 2026-09-27
---

**Problem.** Reference test modules other than the 24-hour washout file keep per-process caches that each xdist worker recomputes; measure what they cost before sharing any of them the way washout_curve does

**Observed 2026-09-27, by `PL-F08Y`.** Under `--dist loadgroup`, which deals
ungrouped tests out one at a time across all eight workers, the suite without
the washout file ran 8.0 and 10.7 s slower than under `worksteal`. In the same
runs `tests/reference/test_control_resolution.py`'s
`test_the_ventilator_start_binds_the_per_rate_table_at_every_rate` went from
under 8 s to 18.3 s. That is what a per-process cache recomputed on a worker
that had not warmed it looks like, though it was not traced. `git grep` finds
`functools.cache` or a module- or session-scoped fixture in
`test_published_wash_in_and_elimination.py` (three), `test_control_resolution.py`
and `test_coupled_dynamics.py`. The Qt integration modules have some too, but
a `QApplication` cannot cross a process, so they are not candidates. Under
`worksteal` a module's tests sit together in one worker's slice, so fewer
workers pay each cache, and nothing has measured what they still cost.
Measure first - `--durations=0` under `worksteal`, and per cached function the
calls that miss - and share one only where the measurement says it pays,
through the pattern `washout_curve` set.
