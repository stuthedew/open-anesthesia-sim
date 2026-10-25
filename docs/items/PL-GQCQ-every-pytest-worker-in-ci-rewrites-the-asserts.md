---
id: PL-GQCQ
title: Every pytest worker in CI rewrites the asserts of all 261 test modules, about 13 s of CPU each, because bytecode writing is off (PL-0MLZ) and --part splits inside modules, so each part imports every module: measure whether a split by module or a safe rewrite cache cuts it (found working PL-QQGZ)
priority: P3
effort: M
status: done
classes: perf, infra
feature: ci-cost
milestone: v0.6.7
touches: conftest.py, tests/conftest.py, .github/workflows/quality.yml, tests/unit/test_bytecode_guard.py, tests/unit/test_quality_step_order.py
deferred-from: v0.7.0 - filed after the gate froze; a P3 CI cost of about 25 s a part, which waits for PL-ZWQS's rebalance to settle first
added: 2026-10-25
closed: 2026-10-25
pr: 1797
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

**Measured.** On 2026-10-25, on an idle 4-core cloud container, at `main` `48c36b64d` plus this branch, with pytest 9.1.1, pytest-xdist 3.8.0 and CPython 3.14.7.

- One `pytest --collect-only -q` took 23.7 s and 24.6 s with assertion rewriting, and 9.5 s and 8.8 s with `--assert=plain`. So rewriting costs about 14.5 s of CPU in each process, a little more than the 13 s above. With pytest's rewrite cache already written, the same collection took 5.5 s and 4.9 s.
- 181 files get a rewrite cache, the test modules and the conftests. The brief's count of 261 modules does not match the tree: `git ls-files` finds 183 Python files under the two test paths.
- A CI-shaped part 1 (`-n 8 --dist worksteal`, coverage on, `--part 1/2`) from a tree with no `__pycache__` took 168, 169 and 172 s. Writing the cache first, with four collect-only processes on a quarter of the modules each, took 6.8 to 7.9 s. The pytest run after it took 139.6 to 143.3 s. Both together took 148 and 152 s. So the lever saves about 20 s a part, net of the step that writes the cache. That is about 12% of this machine's part 1.

**Lever 1 does not work as the brief describes it.** Each xdist worker collects, and so imports, every module before `pytest_collection_modifyitems` runs. A split by module done in the dealing therefore imports and rewrites exactly as much as today. Only a split made before collection, by path, would save anything. That split would put whole modules in one part, which `PL-ZWQS`'s round-robin balance was built to avoid, and it would have to know which modules hold costly tests before it collects them.

**Lever 2 taken.** `--write-assertion-cache K/N`, given with `--collect-only`, turns bytecode writing back on for that one process and collects only share K of N of the test modules. A module's share is the CRC-32 of its path, modulo N. `tests/conftest.py` registers the option so that `_part` parses it, and the root `conftest.py` acts on it, because it owns the bytecode guard and its hooks reach both test trees. `quality.yml` runs one share per core in a named step before each part's pytest step, and the workers then read the cache. The four shares together collected the same 10,454 test ids as one full collection, with none twice. The option refuses to run without `--collect-only`, so no process that executes a test writes bytecode. The cache is written from the fresh checkout and nothing rewrites it during the run, so `PL-0MLZ`'s hazard of a cache written between a mutation and a restore cannot arise. `make check` does not use it, because a cache written there would stay in the working tree.

**Blind review, and a re-measure.** The one blind review pass found that `tests/unit/test_bytecode_guard.py` loads the root `conftest.py` by path, which re-ran its guard and turned bytecode writing off partway through a share's collection. Every module collected after it in that share went uncached, which is about a fifth of the suite. The measurements above used a stand-in plugin that the same reload undid, so they understate the saving. The fix restores the setting after the load, and a regression test collects that file and one after it with `PYTHONPYCACHEPREFIX` in a temporary directory. It failed before the fix. After it, four shares cached all 183 test modules. Re-measured with the real step, after merging `main` at `55fa2a60`: part 1 took 188 s from a fresh tree, and 163.5 s with the step included. The step took 8.4 s and the pytest run 154 s. That is about 24 s saved a part, and 33 s off each pytest step.

The pytest step's median falls by about 65 s of the 695 s that `tools/main_ci_status.py` holds as its baseline. That is 9%, inside its band of 0.5 to 1.3. The new step is named, so it is not counted as the suite.

**Decision: merged with the hook** (project owner, 2026-10-25, ratified, over reworking the step to list test files with `git ls-files` and over dropping the step). `bin/docket verify --self` refuses the root `conftest.py`'s new `pytest_ignore_collect` as an added suppression, and a session cannot overrule it. The owner agreed to merge as is if a generalist review agreed. A blind generalist reviewer, asked only whether the change lets a test go unrun, a failure go unreported or stale code run in any invocation that executes tests, returned SAFE with no risks. The reviewer read the code and did not run it.
