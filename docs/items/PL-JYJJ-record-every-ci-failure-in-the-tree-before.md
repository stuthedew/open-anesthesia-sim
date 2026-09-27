---
id: PL-JYJJ
title: Record every CI failure in the tree before GitHub deletes it: from 2026-10-01 a public repository keeps workflow runs 90 days at most, and the only count so far - 391 failed runs of 6,545, 20% of pull-request branches red at least once, 30% in the week to 2026-09-27 - came from a one-off script in a session's scratchpad
status: dropped
feature: fewer-red-runs
touches: tools/ci_census.py, tests/tools/test_ci_census.py, docs/ci-failures.csv, .claude/skills/docket/SKILL.md
added: 2026-09-27
closed: 2026-09-27
reason: not needed: no decision found that needs CI history older than GitHub's 90-day window; a one-off census inside the window answers every question asked of it (recipe in the brief)
---

**Asked for** by the project owner, 2026-09-27: keep track of every CI
failure, so the causes can be analysed and red runs made rarer. The request
lifts the generator pause for this work, and only for it (`PL-6Q9L`).

**Why a record in the tree.** GitHub lists every run already, so a record
would only duplicate it until 2026-10-01. From that date, checks, workflow runs
and commit statuses fall under the Actions retention setting, and a public
repository cannot set that above 90 days (GitHub Docs, "Configuring the
retention period for GitHub Actions artifacts and logs in your organization",
https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization).
This repository's first runs (2026-08-21) age out around 2026-11-19. After
that, any trend longer than 90 days needs a record in the tree, including
whether a fix held and whether red runs fall as the apparatus settles.

**Measured 2026-09-27.** A one-off script in the session scratchpad read all
6,545 runs from 2026-08-21 to 2026-09-27 through `api.github.com`:

- 391 runs failed (6.0%). `pr-title` failed 159 of 2,453. `quality` failed 231
  of 3,921: 111 on pull requests and 116 on pushes to `main`, which is 9.5% of
  1,219 `main` pushes.
- 169 of 838 pull-request branches (20.2%) went red at least once. By the week
  a branch opened: W35 4%, W36 15%, W37 14%, W38 17%, W39 30%.
- Failures by the step that failed:

  | Step | Failures |
  |---|---|
  | whole-store verify replay, `main` only | 98 |
  | pull-request body record (all on 2026-09-26; `PL-3PH2` retired it that day) | 71 |
  | pr-title names the items it closes | 65 |
  | scoped verify replay | 32 |
  | `doc_check` | 32 |
  | pr-record (from 2026-09-26) | 27 |
  | `docket check` | 27 |
  | pytest | 14 |
  | `branch_id_check` | 8 |
  | ruff and mypy | 8 |
  | infrastructure, such as `setup-python` | 3 |
  | others | 6 |

- Lint, types and tests together account for 22 failures (5.6%). Every other
  failure is one of the apparatus's own bookkeeping checks.
- 131 of the 391 fell in the first three days of three new pull-request gates;
  `PL-1DZF` carries that finding.

**Design (recommended).**

- `tools/ci_census.py`, standard library only, with two subcommands:
  - `record` appends each failed run not yet in `docs/ci-failures.csv`: run id,
    created, workflow, event, branch, failed job, failed step and head sha. It
    also appends each week's total per workflow and event, so rates can still
    be computed after GitHub has deleted the runs. It skips any run id the file
    already holds.
  - `report` prints, from the file alone, failed runs against total runs by
    week and by failing step. It also prints the share of pull-request branches
    that went red at least once.
- It reads `api.github.com`: the list of runs, then the jobs of each failed
  run. That was about 450 calls on 2026-09-27, taking under a minute, and the
  proxy reported a limit of 15,000 calls an hour. It does not read the logs:
  their storage host refused a session at CONNECT on 2026-09-27. It does not
  need them either, because every check here is its own step, so the failing
  step's name already says which check failed.
- Whether a failure was avoidable, for example catchable by `make check`, is
  judgment. It is decided once per step, in the item that fixes that step, and
  never per run by the script.
- `record` runs at each release cut, from the docket skill's release procedure.
  Releases land every day or two, well inside 90 days. A pause in releases also
  means a pause in the CI runs that would need recording.

**Done when:**

- `python3 tools/ci_census.py report` reproduces the 2026-09-27 figures above
  from `docs/ci-failures.csv` alone, with no network;
- the release procedure runs `record`;
- a test shows that a second `record` over the same runs adds nothing.

**Dropped 2026-09-27, the same day it was filed.** The project owner
clarified that the tracker had been an idea, not a request, and asked whether
one is needed at all. It is not.

- **The test.** A record kept in the tree is worth building only if some
  decision needs CI history older than GitHub's 90-day window. None was found.
  - Whether a fix worked shows within days. The body-record burst lasted one
    day, and the `main`-only replay has been quiet since 2026-09-23.
  - The checks change weekly, so a failure more than 90 days old mostly
    describes a check that no longer exists in that form.
  - `PL-04KR`'s convergence signals use no CI data.
- **What would change this.** A question like "is the red rate falling
  quarter on quarter?" needs one number per quarter, written where the
  question lives. It does not need a log of every failure.
- **What building it would have cost.** A tool, its tests, a file that grows
  forever, and a new step in every release, which is one more thing that can
  fail. It would also be a new workflow mechanism while `generator: live`
  items are open, a pause the owner's request lifts only for what was
  actually asked.

**The recipe, so the next census costs minutes rather than rediscovery.** A
session can reach `api.github.com` (the repository is public, and the proxy
reported a limit of 15,000 calls an hour on 2026-09-27).

1. List runs with `GET /repos/stuthedew/open-anesthesia-sim/actions/runs?status=failure&per_page=100`,
   paging through them. For denominators, list all runs, or use `total_count`
   with `event=` and `branch=` filters.
2. For each failed run, `GET .../actions/runs/{id}/jobs` and take the steps
   whose `conclusion` is `failure`. Every check here is its own step, so the
   step name identifies the check.
3. Group the failures by workflow, event (`main` push or pull request) and
   failing step, and by week. Count pull-request branches (`head_branch`) that
   went red at least once.
4. For the error text, do not use the REST logs endpoint: it redirects to
   `*.blob.core.windows.net`, which the proxy refused at CONNECT. Use the
   GitHub MCP `get_job_logs` tool from a subagent, on a sample of job ids.
