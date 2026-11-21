---
id: PL-3HNP
title: Retire tools/worker_runs.py and docs/worker-runs/ unless PL-6FX6's worker runs go ahead
status: untriaged
feature: standing-weight
added: 2026-11-21
---

**Problem.** Retire tools/worker_runs.py and docs/worker-runs/ unless PL-6FX6's worker runs go ahead

**Why it matters.** `PL-LY24` counted what each workflow-record check refused in CI from 2026-08-22 to 2026-11-21, and the owner agreed in `PL-KGPR` to retire this one (project owner, 2026-11-21, ratified, "Agree with recs"). Its 2 refusals were the hold it was built to make, and no headless worker has run since 2026-10-20. The owner's answer keeps it if `PL-6FX6` (the first month of API-credit worker runs) goes ahead, because those runs need the review record.

**What to do.** If `PL-6FX6` is dropped or closed without worker runs, remove `tools/worker_runs.py check` from `make check` and CI, and delete the tool, its test and `docs/worker-runs/`. If `PL-6FX6` starts, drop this item.

**Done when.** Either nothing runs `tools/worker_runs.py` and `docs/worker-runs/` is gone, or this item is dropped because `PL-6FX6` started.
