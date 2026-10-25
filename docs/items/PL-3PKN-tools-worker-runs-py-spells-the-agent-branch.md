---
id: PL-3PKN
title: tools/worker_runs.py spells the agent branch prefix again as BRANCH_PREFIX = "claude/" beside docket.claims.AGENT_BRANCH_PREFIX, which fact_home_check passes because a plain string under two names is not compared and claude/ names no path in the tree
status: untriaged
feature: one-source-of-truth
added: 2026-10-25
---

**Problem.** tools/worker_runs.py spells the agent branch prefix again as BRANCH_PREFIX = "claude/" beside docket.claims.AGENT_BRANCH_PREFIX, which fact_home_check passes because a plain string under two names is not compared and claude/ names no path in the tree
