---
id: PL-3HNP
title: Retire tools/worker_runs.py and docs/worker-runs/ unless PL-6FX6's worker runs go ahead
priority: P3
effort: M
status: done
classes: infra
feature: standing-weight
milestone: v0.6.19
touches: Makefile, .github/workflows/quality.yml, tools/worker_runs.py, tests/unit/test_worker_runs.py, docs/worker-runs, tools/headless_worker.py, tests/unit/test_headless_worker.py, tools/branch_sweep.py, tests/unit/test_branch_sweep.py, docket.toml, docs/apparatus.md, docs/maintainer.md, .claude/skills/pull-request/SKILL.md, subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/config.py, subprojects/docket/README.md, subprojects/docket/tests/test_verify.py, tools/model_home_check.py, tests/unit/test_model_home_check.py, tools/model_rewrite.py, tools/rules_paths_check.py, tools/fact_home_check.py, tests/unit/test_fact_home_check.py, docs/items/PL-6FX6-make-the-first-month-of-api-credit-runs-the.md
added: 2026-11-21
closed: 2026-11-21
pr: 2198
payoff: make check and CI stop running a check whose record nothing writes any more, and four workflow files stop describing it
verify: ! grep -qF 'worker_runs.py' Makefile
---

**Problem.** Retire tools/worker_runs.py and docs/worker-runs/ unless PL-6FX6's worker runs go ahead

**Why it matters.** `PL-LY24` counted what each workflow-record check refused in CI from 2026-08-22 to 2026-11-21, and the owner agreed in `PL-KGPR` to retire this one (project owner, 2026-11-21, ratified, "Agree with recs"). Its 2 refusals were the hold it was built to make, and no headless worker has run since 2026-10-20. The owner's answer keeps it if `PL-6FX6` (the first month of API-credit worker runs) goes ahead, because those runs need the review record.

**What to do.** If `PL-6FX6` is dropped or closed without worker runs, remove `tools/worker_runs.py check` from `make check` and CI, and delete the tool, its test and `docs/worker-runs/`. If `PL-6FX6` starts, drop this item.

**Done when.** Either nothing runs `tools/worker_runs.py` and `docs/worker-runs/` is gone, or this item is dropped because `PL-6FX6` started.

[superseded 2026-11-21: `PL-6FX6` was dropped, below] **Triaged 2026-11-21: blocked on `PL-6FX6`** (the trial that runs five items on three models with API credit). The owner's answer in `PL-KGPR` makes this removal depend on whether that trial runs, and `PL-6FX6` is open at `ready`, kept by the owner on 2026-10-19. So this item waits for `PL-6FX6` to close. If the trial ran, drop this item. If `PL-6FX6` is dropped, do the removal.

The removal is larger than `make check` and CI. `tools/headless_worker.py` writes each run's record through `tools/worker_runs.py`. `tools/branch_sweep.py` reads `worker_runs.sent_back` to delete a sent-back worker's branch. `bin/docket verify` accepts a run record as a sanctioned edit through `worker_runs_dir` in `docket.toml`. `.claude/skills/pull-request/SKILL.md` tells a reviewer to record the review with `tools/worker_runs.py review`. Each of these changes with the tool.

**Unblocked 2026-11-21.** The owner dropped `PL-6FX6` (the model trial on API credit) on 2026-11-21, so this item does the removal.

**Done 2026-11-21.** Nothing runs `tools/worker_runs.py`, and the tool, its test and `docs/worker-runs/` (four run records from 2026-10-20 and a README) are deleted.

1. `make check` and the floor section of `quality.yml` no longer run its check, and `docs/apparatus.md`'s floor-command list no longer names it.
2. `tools/headless_worker.py` no longer writes or commits a run record, and its report line no longer names one. The runner itself stays: `docs/maintainer.md` § "Spend the monthly API credit on delegable items" still runs it. Its two tests of the record are removed, and one of them became `test_a_run_that_left_a_commit_unpushed_keeps_its_clone`, which keeps the part about the clone.
3. `tools/branch_sweep.py` no longer reads a sent-back review. With no record, the problem `PL-W5JR` named returns for any later worker run: a sent-back worker branch hides its item from `bin/docket next` until the owner deletes it. No headless worker has run since 2026-10-20. The `firm` reasons, which only that step read, are gone too. `.claude/skills/pull-request/SKILL.md` and `docs/maintainer.md` now say that a session names a sent-back branch to the owner for deletion.
4. `docket verify` no longer treats a run record as a sanctioned edit. The `worker_runs_dir` setting is removed from `docket.toml`, from `docket.config` and from the docket README, with its three tests in `subprojects/docket/tests/test_verify.py`.
5. `tools/model_home_check.py`, `tools/model_rewrite.py` and `tools/rules_paths_check.py` no longer list the folder, and `docket.toml`'s workflow paths no longer name the folder or the test.

**Documents checked.** `docs/apparatus.md`, `docs/maintainer.md`, `.claude/skills/pull-request/SKILL.md`, `subprojects/docket/README.md`, `docket.toml`, and a search of the tree, outside closed items and release notes, for `worker_runs`, `worker-runs`, `PL-87BR` and `sent-back`. `ROADMAP.md` names `PL-W5JR` in a released milestone's list, which is history.

**Generator check.** One-off. It is the removal that the owner decided in `PL-KGPR` from `PL-LY24`'s count, and no fact was misread to cause it.
