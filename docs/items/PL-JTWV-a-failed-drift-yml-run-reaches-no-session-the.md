---
id: PL-JTWV
title: A failed drift.yml run reaches no session: the 2026-10-01 failure went unread for 17 days because tools/main_ci_status.py reads only quality.yml
priority: P2
effort: S
status: ready
classes: defect
feature: drift-visibility
touches: tools/main_ci_status.py, tests/unit/test_main_ci_status.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-18 triage pass
added: 2026-10-18
payoff: a failed monthly or weekly drift run is named at the start of every session until a later run of that job passes, instead of going unread for weeks
verify: grep -q 'def test_a_failed_monthly_job_stays_red_past_a_weekly_run_that_skipped_it' tests/unit/test_main_ci_status.py
---

**Problem.** `drift.yml` reports and does not gate, so its whole value is that
someone reads a red result. The header of the file says "A red result should be
news." The scheduled run on 2026-10-01 failed, and no session or reply
mentioned it until the project owner asked on 2026-10-18. Nothing a session
reads includes that result. The session-start digest prints
`tools/main_ci_status.py`, which reads `quality.yml`'s runs on `main` and no
other workflow. GitHub may email the owner when a scheduled run fails, but that
depends on their notification settings, and an email does not reach a session.

**Why it matters.** The monthly jobs run 12 times a year, and the weekly
`order` job (`PL-75D9`) runs 52 times. A failure that nobody reads costs a
month or more each time. The header's retirement test, "if it goes red
routinely and nobody acts, retire it", also cannot tell a check that nobody
acts on from a check that nobody sees. `PL-FPCK` found two setup defects that
had stayed unseen in the same way.

**Recommendation.** Have `tools/main_ci_status.py` print one line when the
newest completed `drift.yml` run on `main` concluded `failure`. The line should
name the run, its date and the jobs that failed. Print nothing when that run
passed, so the line appears only when there is news. This adds one request,
which the script could make only every so often, as it already does for its
other lines. It follows `CLAUDE.md`'s rule that an advisory goes to the moment
when its decision is taken, and that moment is the start of a session. This
item was not built in the session that filed it, because the owner asked a
question there and did not ask for a new mechanism.

**Triaged 2026-10-18.** The newest run alone cannot answer the question,
because `drift.yml` runs different jobs on different schedules. The monthly
schedule runs `dependencies` and `interpreter`, and the weekly one runs only
`order`. A monthly failure on the 1st is followed within a week by a weekly
run that skips both failed jobs and concludes `success`. Read from the run's
conclusion, the failure would then go silent after at most seven days. So the
line is decided per job: a job is red when the newest run in which that job
reached a verdict failed it. A `skipped` job reached no verdict. The script
reads the jobs of a run only when the page of runs holds a failure, so a
green drift history costs one request at session start.

**Done when.** `tools/main_ci_status.py` prints one line naming each
`drift.yml` job whose newest verdict on `main` was a failure, with the run
number, its date and its URL, and prints nothing when every job's newest
verdict passed. A test pins the case where a later weekly run skipped the
failed monthly jobs.

**Generator check.** One-off. The fact was never recorded where a session
reads it, and no other open item misreads it.
