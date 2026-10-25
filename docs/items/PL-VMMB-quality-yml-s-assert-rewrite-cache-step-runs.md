---
id: PL-VMMB
title: quality.yml's assert-rewrite cache step runs one share per core, and a share that holds no test module makes pytest exit 5 and fails the job: with 183 modules split by CRC-32 that is negligible on 4 cores but likely past about 40, so a larger runner would fail CI for no fault in the code (found closing PL-GQCQ)
priority: P3
effort: S
status: done
classes: defect
feature: ci-cost
touches: conftest.py, tests/unit/test_bytecode_guard.py
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-10-25
closed: 2026-10-25
payoff: moving CI to a runner with dozens of cores cannot fail the assert-rewrite cache step because one core's share of test modules came out empty
verify: grep -q 'def test_a_share_that_collects_no_test_module_exits_cleanly' tests/unit/test_bytecode_guard.py
---

**Problem.** quality.yml's assert-rewrite cache step runs one share per core, and a share that holds no test module makes pytest exit 5 and fails the job: with 183 modules split by CRC-32 that is negligible on 4 cores but likely past about 40, so a larger runner would fail CI for no fault in the code (found closing PL-GQCQ)

**Reproduced 2026-10-25.** `tests/benchmarks` holds one test module. Collecting it in two shares, with `--collect-only -q -p no:cacheprovider --write-assertion-cache K/2 tests/benchmarks`, gives exit 5 ("no tests collected") for share 1/2 and exit 0 for share 2/2. `xargs` exits 123 when any of its commands fails, so the CI step fails.

A share is decided by the CRC-32 of the module's path. The chance that one of n shares gets none of 183 modules is about n × (1 − 1/n)^183. That is close to 0 at 4 shares (the arm64 runners `quality.yml` uses now), about 0.1 at 32 and about 0.4 at 40. At 64 the estimate passes 1, so some share is almost surely empty.

A test module named on the command line is not filtered by `pytest_ignore_collect`, because pytest never asks that hook about an initial path. So the empty share shows only when a directory is collected. In CI that directory comes from `testpaths`.

**Why it matters.** The cache step only saves time: if it caches nothing, the pytest step after it is slower but still correct. So an empty share is a legitimate outcome, and failing the job over it would turn a runner upgrade into a red CI with no fault in the code.

**Done when.** A collection run under `--write-assertion-cache` that collects no test exits 0, and a test shows it on a directory that leaves one share empty. Any other exit status is unchanged.

**Generator check.** No generator. The cause is one assumption in `PL-GQCQ`'s own design, that every share of the CRC-32 split holds a module, and no other item rests on it. The fact misread, whether a share collected anything, has one reader, the cache step, and the fix makes that reader treat an empty share as success.
