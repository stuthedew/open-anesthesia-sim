---
id: PL-GQCQ
title: Every pytest worker in CI rewrites the asserts of all 261 test modules, about 13 s of CPU each, because bytecode writing is off (PL-0MLZ) and --part splits inside modules, so each part imports every module: measure whether a split by module or a safe rewrite cache cuts it (found working PL-QQGZ)
priority: P3
effort: M
status: ready
classes: perf, infra
feature: ci-cost
touches: conftest.py, tests/conftest.py
deferred-from: v0.7.0 - filed after the gate froze; a P3 CI cost of about 25 s a part, which waits for PL-ZWQS's rebalance to settle first
added: 2026-10-25
payoff: each CI test part finishes about 25 s sooner, on every pull request and push
verify: grep -qE '^\*\*Measured\.' docs/items/PL-GQCQ-*.md
---

**Problem.** Every pytest worker in CI rewrites the asserts of all 261 test modules, about 13 s of CPU each, because bytecode writing is off (PL-0MLZ) and --part splits inside modules, so each part imports every module: measure whether a split by module or a safe rewrite cache cuts it (found working PL-QQGZ)

**Evidence.** Measured on 2026-10-25 in a 4-core cloud container on `main` at `48c36b64d`. `pytest --collect-only -q` took 20.0 s with pytest's assertion rewriting and 6.9 s with `--assert=plain`. Another pytest run shared the machine, so both figures are high, but the difference of about 13 s is the rewriting. A cProfile of the collection put about 27.5 s of 36 s, under the profiler, in `_rewrite_test` and `visit_Assert`, over 15,482 `assert` statements in 261 modules.

Pytest caches a rewritten module as a `.pyc` beside it, but only when bytecode writing is on. The root `conftest.py` sets `sys.dont_write_bytecode` so that a stale cache cannot run code the source no longer holds (`PL-0MLZ`). So every process rewrites every test module it imports, on every run. In CI each part's job starts `os.cpu_count() * 2` workers. `--part K/N` deals tests in cycles inside each module (`tests/conftest.py`), so every worker of both parts imports all 261 modules, though it runs half of their tests or fewer.

**Two levers, each to be measured before it is chosen.**

1. Split the parts by module, so that each worker of a part imports only that part's modules. That would roughly halve the rewriting in each part. It changes `PART_SHARES` and the balance `PL-ZWQS` is tuning, so it belongs with that work.
2. Let pytest cache its rewritten test modules while ordinary bytecode stays off. A fresh CI checkout has no cache, so this helps CI only if the cache is restored from an earlier run or written once before the workers start. Pytest validates its cache by the source's mtime and size, as CPython does, so `PL-0MLZ`'s hazard of an edit reverted inside one second applies to it too. It is safe only if nothing mutates and restores a test module that fast.

**Why it matters.** It is paid by every worker of both test parts on every CI run, pull request and push alike. On a 4-vCPU runner with 8 workers, about 13 s of CPU per worker is roughly 25 s of each part's wall time, about a twentieth of a part. The cost grows with every assert added, so it grows with the suite.

**Done when.** The collection cost per worker in a CI part is measured before and after, and one lever is taken, or the item records why neither pays for itself. Either way the result goes under a `**Measured.**` heading here.

**Generator check.** One-off. It is one cost with one cause, found while attributing `PL-QQGZ`'s slowdown, and no other open item comes from it.
