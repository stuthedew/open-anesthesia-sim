---
id: PL-3HNP
title: Retire tools/worker_runs.py and docs/worker-runs/ unless PL-6FX6's worker runs go ahead
priority: P3
effort: M
status: ready
classes: infra
feature: standing-weight
touches: Makefile, .github/workflows/quality.yml, tools/worker_runs.py, tests/unit/test_worker_runs.py, docs/worker-runs, tools/headless_worker.py, tools/branch_sweep.py, docket.toml, docs/apparatus.md, .claude/skills/pull-request/SKILL.md
added: 2026-11-21
payoff: make check and CI stop running a check whose record nothing writes any more, and four workflow files stop describing it
---

**Problem.** Retire tools/worker_runs.py and docs/worker-runs/ unless PL-6FX6's worker runs go ahead

**Why it matters.** `PL-LY24` counted what each workflow-record check refused in CI from 2026-08-22 to 2026-11-21, and the owner agreed in `PL-KGPR` to retire this one (project owner, 2026-11-21, ratified, "Agree with recs"). Its 2 refusals were the hold it was built to make, and no headless worker has run since 2026-10-20. The owner's answer keeps it if `PL-6FX6` (the first month of API-credit worker runs) goes ahead, because those runs need the review record.

**What to do.** If `PL-6FX6` is dropped or closed without worker runs, remove `tools/worker_runs.py check` from `make check` and CI, and delete the tool, its test and `docs/worker-runs/`. If `PL-6FX6` starts, drop this item.

**Done when.** Either nothing runs `tools/worker_runs.py` and `docs/worker-runs/` is gone, or this item is dropped because `PL-6FX6` started.

[superseded 2026-11-21: `PL-6FX6` was dropped, below] **Triaged 2026-11-21: blocked on `PL-6FX6`** (the trial that runs five items on three models with API credit). The owner's answer in `PL-KGPR` makes this removal depend on whether that trial runs, and `PL-6FX6` is open at `ready`, kept by the owner on 2026-10-19. So this item waits for `PL-6FX6` to close. If the trial ran, drop this item. If `PL-6FX6` is dropped, do the removal.

The removal is larger than `make check` and CI. `tools/headless_worker.py` writes each run's record through `tools/worker_runs.py`. `tools/branch_sweep.py` reads `worker_runs.sent_back` to delete a sent-back worker's branch. `bin/docket verify` accepts a run record as a sanctioned edit through `worker_runs_dir` in `docket.toml`. `.claude/skills/pull-request/SKILL.md` tells a reviewer to record the review with `tools/worker_runs.py review`. Each of these changes with the tool.

**Unblocked 2026-11-21.** The owner dropped `PL-6FX6` (the model trial on API credit) on 2026-11-21, so this item does the removal.

**Generator check.** One-off. It is the removal that the owner decided in `PL-KGPR` from `PL-LY24`'s count, and no fact was misread to cause it.
