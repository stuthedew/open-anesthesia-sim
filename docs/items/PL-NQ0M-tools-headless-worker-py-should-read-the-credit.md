---
id: PL-NQ0M
title: tools/headless_worker.py should read the credit left from the Console's Cost API rather than sum a local ledger, which printed $200.00 on a second Mac when the Console showed $197.72
status: untriaged
added: 2026-10-19
---

**Problem.** tools/headless_worker.py states the credit left from this machine's ledger alone, so on a second Mac it printed $200.00 left after a $2.10 run on the first; it should say the figure covers only runs recorded on this machine, or read the spend from a record both machines share

**What happened, 2026-10-19.** The first run, PL-3R6L at $2.10, ran on one Mac. On a second Mac, `--dry-run` printed "$200.00 left", but the Console showed $197.72. The $2.28 gap is that run plus a `claude -p "Say hi"` test of about $0.19, which never went through the runner. So the ledger also misses any spend made outside the runner.

**The Console's own figure is reachable, at a cost.** The Cost API, `GET /v1/organizations/cost_report`, returns the organization's spend in USD in daily buckets, usually within 5 minutes of a request. It returns spend, not the remaining balance, so the runner would still subtract it from the credit. It needs an Admin API credential (`sk-ant-admin01-...`), which ordinary keys are not, and "The Admin API is unavailable for individual accounts" (https://platform.claude.com/docs/en/manage-claude/usage-cost-api, read 2026-10-19).

**Decided** (project owner, 2026-10-19: "that seems like a terrible idea tracking it ourselves"): the credit left is read from the Console, which holds the fact, never summed from a local ledger, which is a second copy of it. The session had recommended keeping the ledger and labelling its figure, over the admin key's reach. That recommendation is withdrawn.

**What to build.**

1. The runner reads this cycle's spend from the Cost API and subtracts it from `--credit-usd`, both for the dry run's figure and for the check before each run. It stops a batch whose spend it cannot read, as it already does for a run whose cost it cannot read, rather than guessing.
2. The admin key comes from the Keychain or `ANTHROPIC_ADMIN_KEY` in the runner's own environment, and `child_environment` drops it, so a worker never holds a key that can manage the organization.
3. The ledger stops deciding the credit left. A run's own cost, Claude Code's estimate, stays in its record under `docs/worker-runs/`, because the Console cannot attribute spend to one run.
4. The Cost API reports data within about 5 minutes and in daily buckets, so the check before each run can lag the run just finished. The runner adds the last run's reported cost until the Console has caught up, or waits; the build decides which, and says so.

**Before building, confirm the account can do it.** The Admin API "is unavailable for individual accounts", and only an organization member with the admin role can create an Admin API key, at platform.claude.com/settings/admin-keys. A Console key "carries full access to all endpoints that accept Admin API keys", with no scopes (https://platform.claude.com/docs/en/manage-claude/admin-api-keys, read 2026-10-19). If the credit's organization cannot create one, this item is blocked on that, and the runner should at least say its figure is only this machine's ledger.
