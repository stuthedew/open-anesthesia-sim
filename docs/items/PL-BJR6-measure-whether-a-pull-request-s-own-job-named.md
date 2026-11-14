---
id: PL-BJR6
title: Measure whether a pull request's own job named merge-hold can satisfy main's required merge-hold check, which GitHub's documentation leaves undecided
priority: P2
effort: S
status: ready
classes: defect
feature: irreversible-actions-refused-at-github
touches: .github/workflows/merge-hold.yml, tools/github_refusals_check.py
deferred-from: v0.7.0 - workflow tooling outside the schematic release, and it changes no displayed value
added: 2026-11-11
payoff: the owner knows whether a held pull request can be merged past the merge hold, and the hold is fixed if it can
verify: grep -qE '^\*\*Result, measured' docs/items/PL-BJR6*.md
not-delegable: the measurement opens and closes a pull request that adds a workflow file, which docket verify refuses as an edit to the checks
---

**Problem.** `main` requires a status check named `merge-hold` (`PL-KH7Y`). Branch protection matches a required check by name. `.github/workflows/merge-hold.yml` runs on `pull_request_target`, so a pull request cannot edit that job. A pull request can still add a workflow of its own, on `pull_request`, with a job named `merge-hold` that passes. Its head commit would then carry two check runs with that name, one failed and one passed. Nobody has measured which of the two GitHub counts.

**Why it matters.** If GitHub counts the passing one, a held pull request can merge, and the check that `PL-KH7Y` made required refuses less than its header comment says. No session has done this, and one would have to add a workflow file to do it, so the change would show in the diff.

**What the documentation says, read 2026-11-11.** It does not settle the question.

- *About protected branches* tells the reader to "make sure that job names are unique across all workflows", because the same name "can cause ambiguous status check results and block pull requests from being merged" (https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches). It does not say which result is counted.
- *Troubleshooting required status checks* says "If a check and a commit status have the same name, both must pass when that name is required" (https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks). That sentence covers a check beside a commit status, and not two check runs.
- A required check can be tied to the app that reports it. Both jobs here are reported by GitHub Actions, so that setting does not tell them apart.

Each page was read in full through the web-fetch subagent, which returned the quoted sentences.

**Done when.** The result is measured and recorded here, in a paragraph that opens "**Result, measured" and gives the date. Measure it on a pull request made for the purpose, whose branch holds an open claim so that `main`'s `merge-hold` job fails. Add a workflow on `pull_request` with one job named `merge-hold` that exits 0. Then read the pull request's merge state from `GET /repos/{repo}/pulls/{number}` and its check runs, and close the pull request unmerged. If the passing job satisfies the requirement, this item also decides the fix. One candidate is a second rule in `bin/docket arm --merge-hold` that fails a pull request whose branch adds or changes a job with that name.

**Found while building `PL-KH7Y`**, which asked the related question of whether the `checks` job should move to `pull_request_target`.

**Generator check.** A member of the family that `PL-39Y1` heads: a refusal at GitHub whose reach was read from documentation and not measured.
