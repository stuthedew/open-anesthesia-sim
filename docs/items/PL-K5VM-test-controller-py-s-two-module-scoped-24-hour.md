---
id: PL-K5VM
title: test_controller.py's two module-scoped 24-hour controller runs are rebuilt in every xdist worker that runs one of their six tests: 4 builds where 2 would do on main, 6 and 7 under PL-4Z5Y's dealing, 33 to 133 s each, and they set the run's tail
status: untriaged
feature: ci-cost
added: 2026-10-17
---

**Problem.** test_controller.py's two module-scoped 24-hour controller runs are rebuilt in every xdist worker that runs one of their six tests: 4 builds where 2 would do on main, 6 and 7 under PL-4Z5Y's dealing, 33 to 133 s each, and they set the run's tail

**Measured 2026-10-17, by `PL-4Z5Y`'s session.** Four local runs of CI's own
pytest command (`-n 8 --dist worksteal --cov=anesthesia_sim.core --cov-branch
--cov-fail-under=100`, 8 workers on this container's 4 vCPUs), each test's
start and finish timestamped per worker by a scratch plugin passed with `-p`.
The two fixtures are `trunk_stepped_onto_the_limit` and
`trunk_halted_on_a_mark_at_the_limit`, both `scope="module"`, each taking
`maximum_step_count` 0.1 s steps through a `SimulationController`. A worker
builds the ones its tests need the first time it needs them, so one build
lands in whichever test comes first on that worker:

| Run | Dealing | Run ends | Builds | Where |
| --- | --- | ---: | ---: | --- |
| baseline | xdist's own | 309 s | 4 | gw0 51 s + 106 s; gw5 92 s (both, in `offers_no_place`) |
| baseline | xdist's own | 315 s | 4 | gw1 57 s + 98 s; gw7 103 s (both) |
| hook on | `PL-4Z5Y`'s | 338 s | 6 | gw1 54 s + 93 s; gw6 86 s (both); gw7 33 s + 54 s |
| hook on | `PL-4Z5Y`'s | 352 s | 7 | gw0 88 s + 56 s; gw3 55 s; gw2 104 s; gw1 133 s (both); gw6 93 s |

Two builds would do. On `main` today the run pays two more than it needs,
and the last of them ends within a few seconds of the run itself. Under
`PL-4Z5Y`'s dealing it pays four or five more, because the dealing shifts
the slice boundaries and stealing then splits the six tests over three or
four workers.

**Why `worksteal` splits them.** The six tests sit together at the end of
the module, and stealing takes the tail half of the longest queue, so the
module's tail is what moves. `xdist_group` marks would keep them together,
but they work only under `--dist loadgroup`, and CI runs `worksteal`.

**Candidate approaches.**

1. **Share the two runs across workers the way `washout_curve` shares a
   curve** (`PL-F08Y`): flock plus a pickle in the basetemp parent. Each
   fixture is built once per run, and each worker still gets its own copy,
   which is what a module fixture already gives it. This needs a
   `SimulationController` stepped to the limit to round-trip through pickle,
   and that has to be checked first. A first check, 2026-10-17: one stepped
   36,000 times pickles in 4,063 bytes, and its unpickled copy's `snapshot()`
   compares equal to the original's.
2. **A cheaper route to the limit.** This changes what the tests exercise:
   "whichever route put it there" is `PL-5291`'s point. So it is the
   owner's call, not a CI-cost fix.

`PL-4Z5Y`'s dealing trial waits on this item: until the builds are shared,
the dealing moves the tail onto them and makes it longer.

**Answered 2026-10-17: closed by `PL-4Z5Y`'s dealing, not by sharing**
(project owner, 2026-10-17, ratified, in `PL-H9KW`'s session, over
`PL-H9KW` extending the hook after `PL-4Z5Y` merges). The six tests are dealt
back to back at the head of one worker's first slice, so each trunk is built
once per run. Candidate (1)'s flock is not built. `PL-H9KW`'s brief, on its
pull request #1479, holds the same finding, reached independently.
`PL-4Z5Y`'s brief has the steps.
