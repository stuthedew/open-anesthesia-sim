---
id: PL-NQ0M
title: tools/headless_worker.py states the credit left from this machine's ledger alone, so on a second Mac it printed $200.00 left after a $2.10 run on the first; it should say the figure covers only runs recorded on this machine, or read the spend from a record both machines share
status: untriaged
added: 2026-10-19
---

**Problem.** tools/headless_worker.py states the credit left from this machine's ledger alone, so on a second Mac it printed $200.00 left after a $2.10 run on the first; it should say the figure covers only runs recorded on this machine, or read the spend from a record both machines share

**What happened, 2026-10-19.** The first run, PL-3R6L at $2.10, ran on one Mac. On a second Mac, `--dry-run` printed "$200.00 left", but the Console showed $197.72. The $2.28 gap is that run plus a `claude -p "Say hi"` test of about $0.19, which never went through the runner. So the ledger also misses any spend made outside the runner.

**The Console's own figure is reachable, at a cost.** The Cost API, `GET /v1/organizations/cost_report`, returns the organization's spend in USD in daily buckets, usually within 5 minutes of a request. It returns spend, not the remaining balance, so the runner would still subtract it from the credit. It needs an Admin API credential (`sk-ant-admin01-...`), which ordinary keys are not, and "The Admin API is unavailable for individual accounts" (https://platform.claude.com/docs/en/manage-claude/usage-cost-api, read 2026-10-19).

**Recommendation** (the session's, not yet the owner's): keep the ledger, and have the runner say that its figure counts only the runs recorded on this machine, with a pointer to the Console's usage page. Reading the Cost API would make the figure true across machines and outside spend, but an admin key can manage the whole organization, including its keys and members. That is a lot of reach to keep on a laptop to save a glance at a web page. Reopen if the owner runs workers from more than one machine regularly.
