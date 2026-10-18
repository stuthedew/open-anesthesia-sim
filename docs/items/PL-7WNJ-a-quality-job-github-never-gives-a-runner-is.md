---
id: PL-7WNJ
title: A quality job GitHub never gives a runner is cancelled at the 15-minute timeout with no steps and runner_id 0, which reads as a hang in the code - main's runs 4805 and 4809 and #1379's 4807 died that way on 2026-10-05, and a session diagnosing red main read the first as the timeout firing on a hung check
priority: P3
effort: S
status: done
classes: defect
touches: tools/main_ci_status.py, tests/unit/test_main_ci_status.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-05
closed: 2026-10-18
pr: 1538
payoff: A red main whose job never got a runner stops being read as code hanging at the 15-minute timeout, so no session root-causes a tree that never ran.
verify: grep -q 'def test_names_a_job_no_runner_took_as_nothing_ran' tests/unit/test_main_ci_status.py
---

**Problem.** A `quality` job GitHub never hands to a runner sits queued and
is cancelled 15 minutes after creation, the same `timeout-minutes: 15`
cutoff `PL-FSH9` set for a hung step. The run reads `failure` and the job
`cancelled` either way. So a session sees a red `main` cancelled at 15
minutes and reads it as the code hanging, which is what this session did
with run 4805. It never ran a step.

**Seen 2026-10-05**, read through the Actions API (`get_workflow_job`):

| Run | Ref | Created (UTC) | Cancelled (UTC) | `steps` | `runner_id` |
| --- | --- | --- | --- | --- | --- |
| 4805 | `main`, `b67dace8` | 19:34:02 | 19:49:04 | none | 0 |
| 4807 | #1379's head, `89b04f7a` | 20:43:01 | 20:58:03 | none | 0 |
| 4809 | `main`, `3165728d` | 20:59:41 | 21:14:43 | none | 0 |

Each job's `started_at` equals its `created_at`, and its `runner_name` is
empty. Run 4808, a pull-request run on the tree 4809 later ran on, got a
runner 7 seconds after creation and passed in 8 minutes 7 seconds. 4809's
re-run (attempt 2) got runner 1000011567 and passed at 21:26:20. Local
`make check` on `b67dace8` passed in 5 minutes 44 seconds. Run 4806, on
#1379 at 19:54, also ran 15 minutes 3 seconds and was not read.

**Why it matters.** `CLAUDE.md`'s stop rule halts a session on `main` red,
or on the same check failing twice, and a session that misreads a queue
stall as a hang stops on it, or root-causes code that never ran. The
`get_job_logs` call returns 404 for such a job, which looks like missing
logs rather than "nothing ran". The two cases are told apart by one field:
a job that ran has a `steps` array and a non-zero `runner_id`.

[superseded 2026-10-11: triage chose the digest's line, under **Where it is
answered** below] **Not decided here.** This could be answered in the docket skill's red-`main`
procedure, the stop rule's wording, or a check. The last is a new mechanism
and waits on the generator pause (`PL-R417`) while that holds. Triage
decides which.

**Re-confirmed 2026-10-11** on main at `16a20a4f`: run 4805's one job, read
again through the Actions API, is `checks`, `cancelled`, `runner_id` 0, no
steps, created and started at 19:34:02 and completed at 19:49:04. Run 4806, the
one not read above, is the same shape, so four runs died this way on
2026-10-05; none of the 133 `quality.yml` runs numbered after 4809 has run 15
minutes and failed. Fed that run and its jobs, `tools/main_ci_status.py`'s `advisory`,
which the session-start digest prints, says only "main's quality run #4805 on
b67dace8 concluded failure - main is red and no pull request will show it.":
no step named, and nothing saying none ran. `step_conclusions` returns empty
for such a job, the same answer it gives a payload it cannot read.

**Where it is answered (triage, 2026-10-11).** In the digest's red-`main` line,
not in prose. That line is the one place every session meets a red `main`, the
docket skill has no red-`main` procedure to amend, and the stop rule is right
to stop on it: a red `main` from outside the item is still the owner's to
re-run. What is missing is the reading, and `tools/main_ci_status.py` already
fetches the jobs and already separates "the queue, not the tree"
(`_is_queue_failure`), so a third reading there is a repair to an existing
reader rather than a new mechanism. The generator pause would not hold it
either way: no open item carries `generator: live` on 2026-10-11.

**Done when.** `tools/main_ci_status.py` tells a run whose every job has no
steps and `runner_id` 0 from one that ran and failed, and its line says no
runner took the job, so nothing ran and a re-run rather than a fix is what
clears it. A test in `tests/unit/test_main_ci_status.py` pins run 4805's
payload shape, and a job that ran keeps today's line.

**Generator check.** The fact misread is whether a run's conclusion judged the
tree: GitHub concludes a run `failure` when its only job was cancelled before
any runner took it, counted against `timeout-minutes` from creation. That is an
external behaviour nothing here models, and no head's `misread:` states it. The
nearest neighbours are `PL-JTHW` (closed 2026-10-01, a `cancelled` run is not a
verdict) and `PL-T83R` (closed 2026-09-20, a replay failure is the queue, not
the tree), both in the same tool. Neither fix should have covered a run
concluding `failure`, so this is not a re-entry: a one-off. A fourth reading
of "which runs judged the tree" would make the three a head.

**Built 2026-10-18.** `idle_jobs` in `tools/main_ci_status.py` names each job
with a `runner_id` of integer 0 and no steps, and `advisory` takes them. When
no other step failed, the line says no runner took the job, so nothing ran, and
asks for a re-run rather than a fix. Beside a real failure it names the steps as
before and adds that the idle jobs ran nothing. The queue reading is withheld
while any job is idle. Against the code before the fix,
`uv run pytest "tests/unit/test_main_ci_status.py::TestIdleJobs::test_names_a_job_no_runner_took_as_nothing_ran"`
failed with the old line: "main's quality run #4805 on b67dace8 concluded
failure - main is red and no pull request will show it."
