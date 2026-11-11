---
id: PL-KH7Y
title: Require the merge-hold check on main, then remove its not-required marker and name it in the GitHub rules check
priority: P1
effort: S
status: done
classes: defect, infra
feature: irreversible-actions-refused-at-github
touches: .github/workflows/merge-hold.yml, tools/github_refusals_check.py, tests/unit/test_github_refusals_check.py, tests/unit/test_required_checks_check.py, docs/maintainer.md, docs/apparatus.md
blocked-by: PL-39Y1
deferred-from: v0.7.0 - a guard of the workflow, which nothing in the schematic's gate depends on
added: 2026-11-11
closed: 2026-11-11
pr: 2123
payoff: a pull request that the arming rule holds cannot merge, whoever arms it and by whatever route
verify: ! grep -q 'not-required' .github/workflows/merge-hold.yml && grep -q 'default-merge-hold' tools/github_refusals_check.py
---

**Problem.** Require the merge-hold check on main, then remove its not-required marker and name it in the GitHub rules check

**Why it matters.** `PL-39Y1` added the `merge-hold` check, which fails on a pull request that `bin/docket arm` holds. Until `main` requires that check, a failed run refuses nothing: a session that arms a held pull request still sees it merge on green.

**Done when.** `main`'s required status checks include `merge-hold`. The job in `.github/workflows/merge-hold.yml` carries no `# not-required:` line. `tools/github_refusals_check.py` has a rule that fails where `merge-hold` is not required, and its row for `enable_pr_auto_merge` names that rule and no longer says the action is open.

**Why it could not ride `PL-39Y1`.** The workflow runs on `pull_request_target`, which GitHub reads from the default branch, so the check first runs after the file is on `main`. Requiring it earlier would have held `PL-39Y1`'s own pull request on a check that could never report.

**Start it once `.github/workflows/merge-hold.yml` is on `main`**, which is when `PL-39Y1`'s pull request has merged and the check has run on a pull request at least once.

**Order, which matters.** `tools/required_checks_check.py` fails on a job marked not required that settings require, and on a reporting job with no marker that settings do not require.

1. Open the pull request that removes the marker and adds the rule. Its `checks` job fails until step 2.
2. The project owner adds `merge-hold` to `main`'s required status checks: Settings > Branches > the rule for `main` > Edit > "Require status checks to pass before merging" > search for `merge-hold` > Save changes. The same change by command: `gh api -X POST repos/stuthedew/open-anesthesia-sim/branches/main/protection/required_status_checks/contexts -f 'contexts[]=merge-hold'`.
3. Re-run the failed `checks` job, and merge.

Between step 2 and the merge, every other open pull request fails `checks` until it brings `main` in, so do the three steps in one sitting.

**Also decide here** whether `checks` should move behind `pull_request_target` too. `quality.yml` runs on `pull_request`, so a pull request can edit the job that reports `checks`. `PL-39Y1` records this as not yet weighed.

**Decided 2026-11-11: `checks` stays on `pull_request`.** The session decided this, because one option is clearly correct. Moving the job would not close the gap. `checks` has to run the pull request's own tests, `Makefile` and tools to test them, so a pull request that made those pass without testing anything would pass `checks` whichever copy of the workflow started the job. The move would also run a pull request's code with the base repository's rights. GitHub's page on the event warns against that: "Running untrusted code on the `pull_request_target` trigger may lead to security vulnerabilities. These vulnerabilities include cache poisoning and granting unintended access to write privileges or secrets" (https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows, the `pull_request_target` section, read in full through the web-fetch subagent on 2026-11-11). `merge-hold` can use that event because it runs nothing the pull request brought.

**Measured 2026-11-11, before the owner was asked for the setting.** `PL-39Y1` read two facts from GitHub's documentation only. Both hold in the workflow's first seven runs, on pull requests `#2103`, `#2094`, `#2114` and `#2119`.

- **The check reports on the pull request's head commit.** Run 42956812477 carries `head_sha` 59752d43c, the newest commit of `#2103`'s branch, and its job 130313749472 is among the check runs GitHub lists for `#2103`'s head commit. The same holds for `#2094` at 566eff9a4 (jobs 130317179140 and 130317570052). The documentation gives `GITHUB_SHA` for this event as "Last commit on default branch", so the commit the check attaches to could not be read from that page.
- **The checkout holds the pull request's branch.** The log of job 130313749472 shows the fetch `+refs/heads/*:refs/remotes/origin/*`, which brought `origin/claude/great-carson-yb0g29` with every other branch, and then `git checkout --progress --force -B main refs/remotes/origin/main` at b5cde5e99. So the files that run are `main`'s and the branch is in the clone as data. The step then read that branch: "hold - claude/great-carson-yb0g29: a merge would erase its open claim on PL-62PF, PL-9YPR, PL-CBYS".
- **Both results occur.** Five runs failed on a held pull request, and two passed on `#2094` once its claim was released: "pass - nothing `bin/docket arm` reads from claude/gracious-darwin-3hq5tg's commits holds its merge".

*Troubleshooting required status checks* says "A required status check must have completed successfully in the chosen repository during the past seven days", and the two passing runs meet that.

**Not measured: a job of the same name in the pull request's own workflow.** `PL-BJR6` (measure whether a pull request's own job named `merge-hold` can satisfy the required check) holds it.

**Fixed in place, 2026-11-11.** The docstring of `tools/required_checks_check.py` said `main`'s protection was set to `non_admins`, so that an administrator could merge past a red check. GitHub returned `enforcement_level: everyone` on that date. The paragraph now names the rule in `tools/github_refusals_check.py` that reads that setting.

**Generator check.** A member of the family `PL-39Y1` heads: the second step of that fix, split off because GitHub runs a `pull_request_target` workflow only from the default branch. It adds no mechanism of its own.
