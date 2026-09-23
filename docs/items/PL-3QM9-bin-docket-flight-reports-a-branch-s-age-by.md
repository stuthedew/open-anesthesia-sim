---
id: PL-3QM9
title: bin/docket flight reports a branch's age by calendar-date subtraction, so a branch committed 55 minutes ago reads 'last commit 1 day ago' across midnight and a running session looks abandoned
priority: P2
effort: S
status: done
classes: defect
feature: carrier-detection
touches: subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_cli.py
added: 2026-09-21
closed: 2026-09-22
payoff: a branch pushed to an hour ago stops reading as a day-old abandoned one, so a reader of flight does not start an item another session is holding
verify: grep -q 'def test_a_branch_committed_an_hour_ago_is_not_reported_a_day_old' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket flight reports a branch's age by calendar-date subtraction, so a branch committed 55 minutes ago reads 'last commit 1 day ago' across midnight and a running session looks abandoned

**Observed 2026-09-21T00:29Z**, on a refresh of `main` and the in-flight set.
`bin/docket flight` printed:

```
PL-4KZD  origin/claude/clever-faraday-12bnmf  last commit 1 day ago
PL-LHBY  origin/claude/clever-faraday-12bnmf  last commit 1 day ago
```

That branch's last commit is `2026-09-20T23:34:46Z` - **55 minutes** before
the read - and its session (`PL-LHBY`, "a branch halted on a mark reports
nothing") was `RUNNING` at that moment, resolving a merge conflict on `#811`.

**Where.** `subprojects/docket/src/docket/render.py`'s `_since`, which computes
`days = (today - last_commit).days` over two `date` objects. Both sides have
had their time of day discarded before the subtraction, so the answer is the
number of midnights crossed rather than the elapsed time: any commit made
yesterday reads "1 day ago" from 00:00 onward, and the error is largest for the
freshest branches.

**Why it matters, and why it is the dangerous direction.** `format_flight`'s
own docstring rests the whole design on this number being readable - "a branch
touched an hour ago is a live session, and the same branch three weeks on is
work nobody will merge. Only the reader knows which, so both get the same line
and the date decides it." The date is what decides it, and for the first hours
of every UTC day the date is wrong in the direction that reads a live session
as abandoned. A reader following that line starts an item another session is
holding, which is the collision `flight` exists to prevent.

**Not the same finding as `PL-7TVT`**, which is in `feature:
carrier-detection` beside it. That one says commit age is an insufficient
*discriminator* - a young branch may still be abandoned - and is a design
question. This is arithmetic: the age reported is not the age. `PL-7TVT`'s
answer does not fix it and it does not need `PL-7TVT` to be answered first.

**Done when.** The age is computed from the commit's timestamp rather than its
calendar date, so a branch committed within the last 24 hours never reports a
day or more, and a test under `subprojects/docket/tests/` drives a commit
timestamped shortly before midnight read shortly after it.

**Closed 2026-09-22, in `PL-7TVT`'s second half.** `_Walk.last`,
`Branch.last_commit`, `QueueEdit`, `Carrier` and `SettledBranch` carry the full
`%cI` timestamp, and `render._since` subtracts it from an instant rather than
one date from another: minutes under an hour, hours under a day, days beyond,
each rounded down. `--now` fixes the instant for a test, and `--today` alone is
read as the last instant of that day, so every age pinned under it before still
reads the same. `test_a_branch_committed_an_hour_ago_is_not_reported_a_day_old`
drives the observed case - committed 23:34:46, read 00:29 the next day - and
reads "last commit 54 minutes ago".
