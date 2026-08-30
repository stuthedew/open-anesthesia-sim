---
id: PL-J786
title: Require a green `checks` run before any merge into main
priority: P2
effort: S
status: ready
classes: infra, defect
feature: public-history
added: 2026-08-30
not-delegable: the rule lives in GitHub repository configuration, not in the tree, and no MCP tool in this session exposes rulesets. A session can confirm the result on a throwaway pull request but cannot make the change.
---

**Problem.** Nothing gates a merge into main. Across the last twelve pull
requests the median time from open to merge is under two minutes — #64 merged
23 seconds after opening, #71 in 30 — while the `quality` workflow's `checks`
job takes about 50 seconds. #71's check run completed 26 seconds *after* it was
merged.

Split out of `PL-S4M2` (switch main to squash-merge and delete the head
branch) on 2026-08-30. `PL-S4M2` bundled this with the squash-merge switch and
was therefore blocked behind `PL-ZQ9C` (record an item's pull request), but
only the squash half needs `PL-ZQ9C`: nothing about requiring a check depends
on how the merge commit is composed. Separating them makes this landable
immediately.

**Why it matters.** Merging before the checks finish means unverified code
reaches main in a repository whose stated standard is that a displayed value
could influence patient management. The `checks` job — `ruff format --check`,
`ruff check`, `mypy src`, `pytest`, `docket check`, `doc_check` — is the only
automated statement that the pinned reference states still hold. It is also
the failure mode that scales with throughput: one ungated merge is a risk, and
a release cadence of eight items is eight of them.

**Where.** GitHub repository settings for `stuthedew/open-anesthesia-sim`. No
files in the tree change.

**Blocked on the account plan, not on another item.** The repository is
**private**, and GitHub enforces neither rulesets nor classic branch
protection on private repositories under GitHub Free — rulesets need Pro or
above, and on a Free plan the rules can be created but are not enforced.
Two ways out:

  - **GitHub Pro.** Cheapest and immediate. Rulesets become enforceable on
    this repository with no other change.
  - **Nothing, and keep merging on discipline.** Records the risk honestly
    rather than pretending a rule exists.

**Publishing the repository is not one of them (project owner, 2026-08-30).**
Rulesets are free on public repositories, and `public-history`'s premise —
`PL-XH1D` (state how the project is developed) is "read by anyone evaluating
whether to trust the simulator" — assumes an audience, so it reads like the
cheap route. It is not available. When this project is published is the
owner's decision to make personally, and it will not be taken in order to
obtain a CI gate. Do not re-raise it here or in any sibling item: a settings
problem is not a reason to publish a repository, and offering it as one puts
an irreversible disclosure decision behind a routine convenience.

**Do not require an approving review.** GitHub forbids a pull request's author
from approving it, as a platform rule no setting overrides, and every pull
request in this repository is opened by the project owner. An approval
requirement would lock him out of his own repository, and a rule that has to
be bypassed on every merge trains bypassing rather than review. Require the
check; leave review to happen without a gate enforcing it.

**Leave "require branches to be up to date" off.** It forces every pull
request to absorb main before merging, which on a single-maintainer repository
buys nothing and costs a rebuild per merge.

**The bypass list must stay empty.** "Administrators included" is what makes
the rule bind the only person who merges; a ruleset with the owner in its
bypass list is a rule that reports itself as active and stops nothing.

**Done when.** A pull request against main with a failing or still-running
`checks` job cannot be merged, including by the repository owner, confirmed on
a throwaway pull request — or, if the plan question above is answered by doing
nothing, this item is dropped with that reason recorded.
