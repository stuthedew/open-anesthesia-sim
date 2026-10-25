---
id: PL-3PKN
title: tools/worker_runs.py spells the agent branch prefix again as BRANCH_PREFIX = "claude/" beside docket.claims.AGENT_BRANCH_PREFIX, which fact_home_check passes because a plain string under two names is not compared and claude/ names no path in the tree
status: untriaged
feature: one-source-of-truth
added: 2026-10-25
---

**Problem.** tools/worker_runs.py spells the agent branch prefix again as BRANCH_PREFIX = "claude/" beside docket.claims.AGENT_BRANCH_PREFIX, which fact_home_check passes because a plain string under two names is not compared and claude/ names no path in the tree

**Next steps, written 2026-10-25 by the thread that filed it, which stopped for length.** `tools/worker_runs.py:82` has `BRANCH_PREFIX = "claude/"`, and the home is `subprojects/docket/src/docket/claims.py:194`, `AGENT_BRANCH_PREFIX = "claude/"`. Replace the copy with a read of the home. Then fix the shape: `tools/fact_home_check.py` rule 2 refuses one call, and since `PL-S08Z` one repository path, bound under two names in two apparatus modules. A plain string constant such as this one is compared under neither, so the next copy would also pass. Decide whether rule 2 should also compare upper-case string constants of a few characters or more across modules, and measure how many false matches that gives on `main` before choosing.
