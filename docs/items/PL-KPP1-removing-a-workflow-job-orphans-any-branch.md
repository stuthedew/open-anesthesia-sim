---
id: PL-KPP1
title: Removing a workflow job orphans any branch-protection required check named after it, and nothing in the repository can see that list
priority: P2
effort: S
status: ready
classes: infra, docs
feature: ci-cost
touches: .github/workflows/pr-title.yml
added: 2026-09-05
verify: python3 tools/doc_check.py check && grep -q 'load-bearing outside the tree' .github/workflows/pr-title.yml
---

**Problem.** Removing or renaming a workflow job orphans any branch-protection
required status check named after it. Nothing in the tree can see that list, so
nothing can warn about it.

**Why it matters.** The failure mode is silence rather than a break. A required
check is matched by *name*; with no job of that name nothing reports it, so
every pull request waits forever on a check that cannot arrive — pending, which
looks like CI still running, not failing, which would be visible. It cost the
project owner a manual merge and cost a session a wrong diagnosis (see below).

The requirement itself has been removed from branch protection, which was the
fix, and the guard note landed on `quality.yml`'s `checks` job in #367. **What
remains is the other half of that guard**: `.github/workflows/pr-title.yml`'s
`pr-title` job carries no such note and is the repository's only other job that
reports on a pull request — so it is the only other name a required check could
plausibly hold, and the next rename of it re-arms exactly this trap. This
item's own "What would prevent a repeat" already asked for the note beside
*each* job name; one of two got it.

`drift.yml`'s `dependencies` and `interpreter` jobs are deliberately out of
scope. That workflow runs on a schedule and never on a pull request, so it
never reports a check to require; a requirement naming one would block every
pull request permanently rather than silently, which is the visible failure and
not this one.

**Where.** `.github/workflows/pr-title.yml`, at the `pr-title:` job key on line
37. Match the wording already at `.github/workflows/quality.yml:41` rather than
writing a second version of it.

**What happened.** `PL-D551` (fold the floor job into checks, ahead of the uv
install) merged the `floor` job's steps into `checks` and deleted the job.
`floor` was also a required status check in this repository's branch
protection. Observed on #361 as `mergeable_state: blocked` with every actual
check green. That session misread it as a missing approving review and told the
project owner so; they had to merge past it by hand, and diagnosed it from the
GitHub UI, which is the only place it is visible. The misread is part of the
finding: `blocked` does not distinguish "waiting on a review" from "waiting on
a check that will never report", and the pull request API surfaces no list of
which required checks are outstanding.

**Why nothing caught it, and why the fix is prose.** The required-check list
lives in branch-protection settings, not in the tree. Reading it needs an
authenticated API call, which `tools/` deliberately cannot make — those scripts
are standard-library only so they run in a bare checkout with no virtualenv.
So the decidable half genuinely is not available here, and `CLAUDE.md` is
explicit that a tool guessing at the judgment half is worse than no tool. The
comment beside the job name, where somebody about to rename it is already
looking, is the cheapest real guard available.

**Done when.** `.github/workflows/pr-title.yml`'s `pr-title` job carries the
same load-bearing-name note that `quality.yml`'s `checks` job carries, so every
job in this repository that can report a status check to a pull request says at
its own name that the name is matched off-tree.
