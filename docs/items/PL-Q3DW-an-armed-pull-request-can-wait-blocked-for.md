---
id: PL-Q3DW
title: An armed pull request can wait blocked for hours with every check green: merge-hold and pr-title cancel a run already in progress, two events on one commit in the same second can start in either order, and branch protection reads the newest run, which may be the cancelled one
priority: P2
effort: S
status: done
classes: defect, infra
feature: ci-cost
touches: .github/workflows/merge-hold.yml, .github/workflows/pr-title.yml
deferred-from: v0.7.0 - a merge workflow defect, which changes no simulated or displayed value
added: 2026-11-25
closed: 2026-11-27
pr: 2340
payoff: an armed pull request merges when its checks pass, instead of waiting for hours behind a cancelled run that nobody sees
tests: tests/unit/test_ci_concurrency.py::test_a_required_check_on_a_pull_request_cancels_none_of_its_runs, tests/unit/test_ci_concurrency.py::test_the_title_check_reads_the_pull_request_s_title_rather_than_its_event_s
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

**Done 2026-11-27.** Both `merge-hold.yml` and `pr-title.yml` now set `queue: max` in place of `cancel-in-progress: true`, as the brief's direction said. GitHub's workflow syntax page, section `concurrency`, read 2026-11-27, says that with `queue: max` "Up to 100 jobs or workflow runs can be pending in the concurrency group", and that combining it with `cancel-in-progress: true` "is not allowed and will result in a workflow validation error". So no run of either check is cancelled by another run of the same workflow, and the newest run on the head commit always ends with a verdict.

The two points the brief left to settle:

1. An invalid `merge-hold.yml` would block every merge, and a pull request cannot test its own change to it, because `pull_request_target` runs the default branch's copy. `pr-title.yml` runs on `pull_request`, which runs the pull request's own copy, and it carries the same `queue: max`. So this pull request's own `pr-title` run shows whether GitHub accepts the key before `merge-hold.yml` reaches `main`. **Measured on #2340, 2026-11-27.** GitHub accepted `queue: max` in this pull request's own `pr-title.yml`: the push and the title edit that followed it started two `pr-title` runs on head `9be5a071`, and the second started at 23:23:42 UTC, two seconds after the first finished at 23:23:40. Both passed, and neither was cancelled.
2. `pr-title` used to read the title from its own event's payload (`github.event.pull_request.title`), so each run checked the title as it was at that event. The first draft kept that and argued that the newest run, which read the newest title, is the one that counts. The pull request's blind review showed why that does not hold once runs queue. A run whose event carried an older title can still be running when the title is edited, and GitHub does not order two runs that start in the same second, so the old title's run can also run last. Either way the last result can be a pass on the old title, and auto-merge can then land the new title unchecked. So the title step now asks the pull request for its title with `gh api` when it runs, with `pull-requests: read` added to the workflow's permissions. The run that finishes last has then checked the title the merge uses. The one case left is an edit in the second or so between that read and the run's end. The edit's own run still checks it, but possibly after the merge. `tests/unit/test_ci_concurrency.py::test_the_title_check_reads_the_pull_request_s_title_rather_than_its_event_s` holds the step to it, and fails on the first draft.

`tests/unit/test_ci_concurrency.py::test_a_required_check_on_a_pull_request_cancels_none_of_its_runs` holds both files to `queue: max` and no `cancel-in-progress`. It fails on both files at `8f404cfa`.

**Documents checked:** the comments above both `concurrency` blocks, rewritten; `tests/unit/test_ci_concurrency.py`'s module docstring, which now names the new test; `.claude/skills/pull-request/SKILL.md` and `docs/maintainer.md`, which say nothing about cancelled runs; `tools/main_ci_status.py`, which reads `quality.yml`'s runs on `main` and not these two.
