---
id: PL-KPP1
title: Removing a workflow job orphans any branch-protection required check named after it, and nothing in the repository can see that list
status: untriaged
feature: ci-cost
touches: .github/workflows/quality.yml
added: 2026-09-05
---

**Problem.** Removing a workflow job orphans any branch-protection required check named after it, and nothing in the repository can see that list

**Why it matters.**

**Where.**

**Done when.**

**What happened.** `PL-D551` merged the `floor` job's steps into `checks` and
deleted the job. `floor` was also a **required status check** in this
repository's branch protection, and a required check is matched by *name*
against the checks a run reports. With no job of that name, nothing ever
reports it, so every pull request now sits waiting for a check that cannot
arrive - not failing, which would be visible, but pending forever.

Observed on #361 as `mergeable_state: blocked` with every actual check green.
This session misread that as a missing approving review and told the project
owner so; they had to merge past it by hand. The misread is part of the
finding: `blocked` does not distinguish "waiting on a review" from "waiting on
a check that will never report", and the PR API surfaces no list of which
required checks are outstanding.

**Why nothing caught it.** The required-check list lives in branch-protection
settings, not in the tree. `tools/` can read every workflow file and every job
name in it, but has no way to read what the repository requires - so the
coupling is real, load-bearing, and invisible to `make check`, to CI, and to
`doc_check.py`. Renaming a job is the same hazard as deleting one.

**Options, and the trade.** Removing `floor` from the required list is the
correct fix rather than restoring the job: the job genuinely no longer exists,
and a required check naming a job that does not exist is a latent trap whatever
else is true. Restoring the job would also work and needs no settings change,
but gives back `PL-D551`'s saving and leaves the same trap armed for the next
rename.

**What would prevent a repeat.** A script cannot read branch protection without
an authenticated API call, which `tools/` deliberately cannot make - they are
standard-library only and must run in a bare checkout. So the deterministic
half is not available here, and this is one of the cases where the honest
answer is a note rather than a check. The cheapest real guard is a line in the
workflow next to each job name saying that the name is load-bearing off-tree.
