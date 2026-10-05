---
id: PL-7WNJ
title: A quality job GitHub never gives a runner is cancelled at the 15-minute timeout with no steps and runner_id 0, which reads as a hang in the code - main's runs 4805 and 4809 and #1379's 4807 died that way on 2026-10-05, and a session diagnosing red main read the first as the timeout firing on a hung check
status: untriaged
added: 2026-10-05
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

**Not decided here.** This could be answered in the docket skill's red-`main`
procedure, the stop rule's wording, or a check. The last is a new mechanism
and waits on the generator pause (`PL-R417`) while that holds. Triage
decides which.
