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

**The account cannot read the Cost API (tested 2026-10-20).** The Console had no Admin keys page for this account. The documentation also accepts "a personal or service account key that isn't scoped to a workspace", with "the same permissions as the linked account" (https://platform.claude.com/docs/en/manage-claude/admin-api, § "Authentication", read 2026-10-20). So the project owner created a personal key scoped to the whole organization. Its prefix, `sk-ant-usr-`, is not in the documentation. `GET /v1/organizations/cost_report` with that key returned `permission_error`, "Missing permissions" (request `req_011CgCY9G5a2ChyoqGJtVWzP`). This matches "The Admin API is unavailable for individual accounts". The documentation offers turning the account into an organization, at platform.claude.com/settings/organization. Nothing read so far says what that does to the credit included with Max, so it is not recommended.

**Question for the project owner: where does the runner get the credit left?**

- **A. The owner gives it the Console's figure at each launch.** The runner refuses to start without `--credit-left`, the figure on the Console's billing page. During the batch it subtracts each finished run's reported cost from that figure. Nothing stores spend between launches, so the Console stays the only record of it. The cost is reading one number from the Console and typing it at each launch.
- **B. Keep the local ledger and label its figure "runs recorded on this Mac".** No step at launch, but it is the second copy the owner refused on 2026-10-19. It also misses spend made outside the runner, such as the $0.19 test.
- **C. Turn the account into an organization to open the Cost API.** This needs an answer from Anthropic about the Max credit first.

**Recommendation: A.** It is the only option that keeps the Console as the single record without the Cost API, and a missing figure stops the runner rather than letting it guess.

**Decided: A** (project owner, 2026-10-20, ratified, over keeping the labelled ledger and over turning the account into an organization). The runner refuses to start without `--credit-left`, the figure from the Console's billing page, and subtracts each finished run's reported cost from it during the batch. The ledger no longer decides anything. Build it together with PL-44SP, which changes the same loop in `main()`.
