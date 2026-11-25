---
id: PL-Q3DW
title: An armed pull request can wait blocked for hours with every check green: merge-hold and pr-title cancel a run already in progress, two events on one commit in the same second can start in either order, and branch protection reads the newest run, which may be the cancelled one
priority: P2
effort: S
status: ready
classes: defect, infra
feature: ci-cost
touches: .github/workflows/merge-hold.yml, .github/workflows/pr-title.yml
deferred-from: v0.7.0 - a merge workflow defect, which changes no simulated or displayed value
added: 2026-11-25
payoff: an armed pull request merges when its checks pass, instead of waiting for hours behind a cancelled run that nobody sees
---

**Problem.** An armed pull request can wait blocked for hours with every check green: merge-hold and pr-title cancel a run already in progress, two events on one commit in the same second can start in either order, and branch protection reads the newest run, which may be the cancelled one

**What happened.** On #2322 (2026-11-24), a session pushed its branch and,
in the same second, marked the pull request ready and armed auto-merge. The
push and the ready-for-review event each started a `merge-hold` run on the
same commit, both created at 20:18:21 UTC. Run 1320 passed. Run 1321, the
newer, was cancelled by `cancel-in-progress: true`. The pull request then
showed `mergeable_state: blocked` with `auto_merge` set and every listed check
green, for six hours, and nothing told the session. Re-running run 1321 by
hand at 02:37 UTC on 2026-11-25 let it merge 30 seconds later. So branch
protection read the newest run, and the newest run was the cancelled one.
`pr-title` had a cancelled run on the same commit too, but there the newer
run passed.

**Why the order can go either way.** GitHub's workflow syntax page, section
`concurrency`, says that runs in one group "are processed in first-in-first-out
(FIFO) order according to the time each one started waiting on the
concurrency group, not the time each workflow was dispatched. Since the actual
start time of a job or run may vary, ordering is not guaranteed"
(https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax,
read 2026-11-25). So with `cancel-in-progress: true`, either of two runs
started in the same second may cancel the other.

**Why it matters.** Auto-merge is how approved work lands without anyone
watching it. A pull request blocked this way looks finished to the session
that armed it and to the owner, so work that is done stays off `main`, and a
later pull request that builds on it can conflict or merge first.

**Direction, to be confirmed by the session that builds it.** The same page
says that without `cancel-in-progress`, a newer run waits as `pending`, that
by default only one run may be pending and "any existing `pending` job or
workflow ... will be canceled", and that `queue: max` lets up to 100 wait
instead. So `queue: max` with no `cancel-in-progress` would cancel no run of
`merge-hold` or `pr-title`, and the newest run would always finish. Both jobs
take under a minute, so a run on a superseded commit costs little. Two things
to settle first. `merge-hold.yml` runs on `pull_request_target`, which runs
the default branch's copy of the workflow, so a pull request cannot test its
own change to it, and an invalid file would block every merge. And
`pr-title.yml`'s comment says its cancellation exists so that a run that read
an old title does not stand beside the run for the new one, so check which run
branch protection reads when both finish.

**Generator check.** One-off for now. The fact misread is which run of a
required check on a commit branch protection reads. `PL-SMN4` and `PL-FFLL`
are about cancellation in `quality.yml` across commits, not two runs on one
commit, so neither describes this.

**Until then.** A session that arms a pull request and finds it unmerged
after about 15 minutes reads its check runs. Two runs of one required check
on the head commit, the newer one `cancelled`, is this case, and re-running
the cancelled run clears it.

**Done when.** No required check on a pull request can end with its newest
run cancelled by a run of the same workflow on the same commit.
