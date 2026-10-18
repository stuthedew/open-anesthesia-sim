---
id: PL-JTWV
title: A failed drift.yml run reaches no session: the 2026-10-01 failure went unread for 17 days because tools/main_ci_status.py reads only quality.yml
priority: P2
effort: S
status: done
classes: defect, infra
milestone: v0.5.30
touches: tools/main_ci_status.py, tests/unit/test_main_ci_status.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-18 triage pass
added: 2026-10-18
closed: 2026-10-18
pr: 1607
payoff: the session-start digest prints one line when the newest drift.yml run on main failed, so a red drift result reaches the next session
verify: grep -q 'def test_a_failed_drift_run_is_named' tests/unit/test_main_ci_status.py
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

**Done when.** `tools/main_ci_status.py` prints one line, naming the run, its
date and its failed jobs, when the newest completed `drift.yml` run on `main`
concluded `failure`, and prints nothing for that workflow otherwise. A test in
`tests/unit/test_main_ci_status.py` pins both cases.

**Generator check.** Not an instance of a closed head's fact. Nothing records
that a scheduled run failed except the run itself, and the fix reads that run
from the module that already reads `main`'s CI.
