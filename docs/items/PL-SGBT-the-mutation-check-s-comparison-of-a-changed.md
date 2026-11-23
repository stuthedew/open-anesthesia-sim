---
id: PL-SGBT
title: The mutation check's comparison of a changed test reruns each mutant whose test module fails to import one at a time on one core: 238 reruns took over 20 minutes for one changed test in tests/unit/test_wash_in.py on 2026-11-11, 182 of them mutants of core/parameters.py
priority: P2
effort: S
status: done
classes: perf
feature: tests-detect-wrong-values
touches: tools/diff_mutation.py, tests/unit/test_diff_mutation.py
deferred-from: v0.7.0 - present at the freeze, but no frozen entry remains for this gate to clear (bin/docket wave, 2026-11-22: 0 open entries this gate can clear), so it costs no remaining entry anything, and it has no connection to v0.7.0's Required scope, all of which has closed
added: 2026-11-11
closed: 2026-11-22
pr: 2247
payoff: Each simulator branch's mutation check settles in minutes rather than spending twenty or more on one core.
tests: tests/unit/test_diff_mutation.py::test_settle_reruns_the_mutants_at_once_on_every_worker
recurrences: 2026-11-22 PL-WYDF
---

**Problem.** The mutation check's comparison of a changed test reruns each mutant whose test module fails to import one at a time on one core: 238 reruns took over 20 minutes for one changed test in tests/unit/test_wash_in.py on 2026-11-11, 182 of them mutants of core/parameters.py

**What was measured.** One run on 2026-11-11, in a four-core container, with `PL-R8HY`'s change to `tools/diff_mutation.py`: `make mutate ARGS=--verdict` with one changed line in `app/wash_in.py::is_wash_in` and one assertion deleted from `tests/unit/test_wash_in.py`. The base compare run tested 3,647 mutants of 12 files in about 10 minutes. mutmut recorded exit status 255 for 238 of them, because the mutant made the test module fail while it was imported: 182 in `core/parameters.py`, 45 in `app/formatting.py` and 11 in `core/supported_ranges.py`. `settle` then ran `tests/unit/test_wash_in.py` whole for each of the 238, one after another in one process, for over 20 minutes. The load average stayed near 1.

**Not yet known.** Whether the reruns can run four at a time, and whether the tool before `PL-R8HY`'s change took as long on the same change.

**Checked 2026-11-22**, at `d4e8200c`. `settle` in `tools/diff_mutation.py` still loops over the raised mutants and calls `_pytest_in_mutants` for each one in turn, so the reruns still run one at a time. The loop was already in the tree at the freeze, `0947408`.

**Why it matters.** Every branch that changes simulator code and a test meets this step at its close-out mutation check. A change near a widely imported module, such as `core/parameters.py`, makes hundreds of mutants raise at import, and each one costs a whole-file run. That is twenty minutes or more per branch on a four-core machine with three cores idle. `PL-33CG` (a core mutation check that did not finish in an hour) is the same cost seen from a core change.

**Done when.** Settling the raised mutants no longer costs one whole-file run after another on one core. Either the reruns use every available core, or the mutants that fail only at import are settled without a run each. A test of `tools/diff_mutation.py` shows the chosen behaviour, and the item records the time of a rerun of the 2026-11-11 change.

**Generator check.** A one-off. Nothing was misread: `settle` was written serial when few mutants raised, and `PL-R8HY` and `PL-19M4` widened the mutated files, which raised the count. No head's `misread:` covers a tool's run time.

**Done 2026-11-22.** `settle` in `tools/diff_mutation.py` now looks up each raised mutant's test files and reruns them `RERUN_WORKERS` at a time, one worker for each processor. That is the number of workers mutmut 3.8.0 starts when nothing sets `max_children` (`_run` in `mutmut/__main__.py`, read in this session). Stryker's default is the same on a machine of four cores or fewer: "`cpuCoreCount <= 4? cpuCoreCount : cpuCoreCount - 1`" (https://stryker-mutator.io/docs/stryker-js/configuration/, § `concurrency`, read 2026-11-22). Threads are enough, because each worker only waits on a subprocess. Settling only the mutants that fail at import without a run was not taken: pytest's `-x` already stops such a run at collection, so its cost is the collection that would have to run anyway.

The 2026-11-11 change was replayed on 2026-11-22 at this branch's head, in a four-core container: the same one-line change to `is_wash_in` and the deletion of `assert is_wash_in(0.0)` from `tests/unit/test_wash_in.py`. The whole `make mutate ARGS=--verdict` took 296 s with four workers and 369 s with one. Fewer mutants raise now than on 2026-11-11, because the comparison runs a changed test's own ids before its whole file (`PL-D59R`): 27 raised in each of the two compare runs, of 6,602 mutants. Settling them took 13.9 s and 14.2 s with four workers, against 49.6 s and 48.0 s with one. `tests/unit/test_diff_mutation.py::test_settle_reruns_the_mutants_at_once_on_every_worker` fails with `BrokenBarrierError` when `RERUN_WORKERS` is 1.
