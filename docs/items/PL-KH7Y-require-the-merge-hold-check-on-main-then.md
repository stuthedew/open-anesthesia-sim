---
id: PL-KH7Y
title: Require the merge-hold check on main, then remove its not-required marker and name it in the GitHub rules check
priority: P1
effort: S
status: ready
classes: defect, infra
feature: irreversible-actions-refused-at-github
touches: .github/workflows/merge-hold.yml, tools/github_refusals_check.py, tests/unit/test_github_refusals_check.py, tests/unit/test_required_checks_check.py
blocked-by: PL-39Y1
deferred-from: v0.7.0 - a guard of the workflow, which nothing in the schematic's gate depends on
added: 2026-11-11
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

**Generator check.** A member of the family `PL-39Y1` heads: the second step of that fix, split off because GitHub runs a `pull_request_target` workflow only from the default branch. It adds no mechanism of its own.
