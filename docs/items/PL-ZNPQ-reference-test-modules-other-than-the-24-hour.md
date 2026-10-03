---
id: PL-ZNPQ
title: Reference test modules other than the 24-hour washout file keep per-process caches that each xdist worker recomputes; measure what they cost before sharing any of them the way washout_curve does
priority: P3
effort: S
status: done
classes: session-cost
feature: ci-cost
milestone: v0.5.21
touches: tests/reference/test_published_wash_in_and_elimination.py, tests/reference/test_control_resolution.py, tests/reference/test_coupled_dynamics.py
added: 2026-09-27
closed: 2026-10-01
pr: 1268
payoff: measures whether sharing the reference modules' caches across xdist workers would cut make check's wall time, before anyone builds it
not-delegable: a measurement whose result decides whether any code changes, so no command can prove it before it is taken
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

**Why it matters.** Under `worksteal`, each cached function is paid once per
worker that runs its module. If a cache costs seconds per worker, sharing it the
way `washout_curve` does cuts every `make check`; if not, nothing should change.

**Done when.** This brief records `--durations=0` under `worksteal` and each
cached function's misses per run, and either the caches that pay are shared
through the `washout_curve` pattern or the brief says none does.

**Measured 2026-10-01: no cache pays; nothing is shared.**

Configuration: the `make check` pytest line exactly (`-n 8 --dist worksteal
--cov=anesthesia_sim.core --cov-branch --cov-fail-under=100`, eight workers on
four cores) plus `--durations=0 -rA`, at `origin/main` as of 13:52 UTC. Five
full runs: three uninstrumented for wall time and durations, and two with a
temporary plugin (`-p`, kept out of the tree and not committed) that put a
timed, counted `functools.cache` in place of each module's cached function
after collection, and wrote every miss - worker, arguments, seconds - per
worker. All five passed the same 5762 test ids (`PASSED` lines from `-rA`,
sorted and compared), and no file under `tests/` changed.

Wall time, uninstrumented: 215.0, 201.3 and 199.8 s. The run-to-run spread is
15 s. Summed `--durations=0` time for each module, across the three runs:

| Module | Summed test time (s) |
| --- | --- |
| `test_coupled_dynamics.py` | 118.4 / 113.6 / 114.8 |
| `test_published_wash_in_and_elimination.py` | 76.8 / 85.3 / 72.3 |
| `test_control_resolution.py` | 13.4 / 13.0 / 13.6 |
| everything else | 979.3 / 966.7 / 1000.7 |

The module-scoped and session-scoped fixtures the problem statement mentions
do not exist in these three modules: `scope=` appears in none of them. The
five `@cache` functions are all there is. Misses per run (instrumented runs 1
and 2), where *redundant* means a miss on arguments another worker had
already computed, costed at that key's mean miss time:

| Cached function | Calls | Misses | Distinct keys | Workers | Miss time (s) | Redundant (s) |
| --- | --- | --- | --- | --- | --- | --- |
| `test_control_resolution._worst_displacement_pp` | 192 | 45 / 45 | 45 | 1 / 1 | 14.4 / 14.2 | 0 / 0 |
| `test_coupled_dynamics._reference_state` | 18 | 9 / 9 | 9 | 1 / 1 | 13.0 / 12.8 | 0 / 0 |
| `test_published_wash_in_and_elimination._eliminate` | 36 | 21 / 21 | 21 | 1 / 1 | 17.3 / 17.5 | 0 / 0 |
| `…_eliminate_without_rebreathing` | 65 | 35 / 32 | 32 | 2 / 1 | 26.4 / 24.9 | 1.9 / 0 |
| `…_wash_in_system` | 68 | 52 / 52 | 45 | 3 / 3 | 35.5 / 37.1 | 4.6 / 5.2 |

Miss times are inclusive: `_eliminate` and `_eliminate_without_rebreathing`
call `_wash_in_system` through its module global, so that nested cost appears
in both rows. The redundant column is per key and is unaffected.

The reading: under `worksteal`, two of the modules ran entirely in one worker
in both runs, so their caches were never recomputed. Only
`test_published_wash_in_and_elimination.py` was stolen from. Its 18 to 24
re-missed calls were spread over two or three workers, and they recomputed 7
`_wash_in_system` keys and at most 3 `_eliminate_without_rebreathing` keys.
That is 5.2 to 6.5 s of redundant worker time per run, out of about 1190 s of
summed test time. On four saturated cores it is worth about 1.5 s of wall
time. Even if all of it fell on the critical path, it could not exceed 6.5 s.
Both figures are inside the 15 s run-to-run spread, so the saving could not
be measured. `PL-F08Y`'s suspect confirms the mechanism rather than a cost:
`test_the_ventilator_start_binds_the_per_rate_table_at_every_rate` now runs
under the 0.005 s `--durations` floor. It reads `_worst_displacement_pp` keys
that the earlier tests in the same worker already warmed, which is the cache
behaving as intended under `worksteal`.

What sharing would cost against that: the `washout_curve` pattern's lock
directory and pickle round-trip, a session fixture threaded through every
caller of three helpers, and a returned `System` that would come back
unpickled where today it is the very cached instance the docstrings at
`_wash_in_system` and `_eliminate` reason about. The 17 s, 864,000-step curve
justified that cost. Under a second per run does not. The breakeven, stated
beforehand: sharing would pay only if the redundant time came to a
measurable share of the wall clock, meaning above the 15 s noise. It came to
about 1.5 s.

When to reopen: if `make check` changes its distribution away from
`worksteal` (`loadgroup` or `load` deal tests out singly and would multiply
these misses), or if one of these modules gains a computation on the order of
the washout curve's.
