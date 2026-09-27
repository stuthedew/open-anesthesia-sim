---
id: PL-7RTN
title: An open pull request can carry no check runs at all, so a branch merges with nothing having gated it
priority: P2
effort: M
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.5.15
touches: .github/workflows/quality.yml, .github/workflows/pr-title.yml, docs/worker.md
added: 2026-09-06
closed: 2026-09-27
pr: 1170
not-delegable: the first work is confirming a hypothesis about GitHub's own behaviour - whether an event raised by the built-in GITHUB_TOKEN creates no workflow run - against the Actions run list for one head SHA and against how the session that opened #395 authenticated. Both are facts about a third party's servers rather than about this tree, so no command run here can be made to fail before the work and pass after.
---

**Problem.** Observed while diagnosing `PL-8P6D` (checks refuse a branch
carrying no item id). #395 (`PL-YGF3`, branch `claude/pl-ygf3-6ocu64`) was
open with **zero** check runs on its head - not queued, not cancelled, none
created - five and then nine minutes after it opened at 19:05:50Z. For
comparison, #394 opened at 19:04:59Z and its two check runs started at
19:05:06Z, seven seconds later, so the runners were not backed up.

Zero check runs is different from a red one and much quieter: branch
protection reports a required check as *pending* rather than failing, which
does not look like a break, and `pr-title.yml`'s own comment already records
that failure mode for a renamed job.

**Not yet established, and this is the first work.** The leading hypothesis is
GitHub's rule that events raised by the built-in `GITHUB_TOKEN` do not create
a workflow run, which would mean a pull request opened by a session holding
such a token silently gets no CI while one opened under a user token does.
That would explain why most agent pull requests here have run checks and this
one did not. It is a hypothesis from one observation; confirm it against the
Actions run list for that head SHA and against how the session that opened
#395 authenticated, before changing anything.

**Why it matters.** Every guarantee this repository's CI provides rests on the
run happening. `quality.yml`'s `checks` and `pr-title.yml`'s `pr-title` are
the only two jobs that report a status to a pull request at all, so a pull
request with neither has had `ruff`, `mypy`, the test suite, `docket`,
`doc_check` and the contrast check applied to it by nobody - on a project that
holds `src/` to a safety-critical standard. A check that silently does not run
is worse than one that fails.

**Where.** `.github/workflows/quality.yml`, `.github/workflows/pr-title.yml`,
and however sessions here authenticate when opening a pull request.

**Done when.** The cause is identified and named in this item; a pull request
opened by an agent session reliably creates both check runs; and if the cause
turns out to be something no workflow file can fix, the failure is made
*visible* rather than silent - a required status check that stays pending
forever is the shape to avoid.

**Cause, found 2026-09-27: no run was missing.** #395 opened at 19:05:50Z on
head `65cbeaf0`. The Actions run list for its branch shows `quality` run 1454
and `pr-title` run 443 created at 19:05:53Z, three seconds later, on that head,
from the `pull_request` event, and both succeeded (`quality` finished at
19:07:10Z). A merge pushed at 19:12, head `0c5159cb`, got `quality` 1457 and
`pr-title` 445 at 19:12:11Z, also green. So at five and at nine minutes after
opening, 19:10:50Z and 19:14:50Z, the head carried finished, passing check
runs.

- **The `GITHUB_TOKEN` hypothesis does not apply.** Every one of those runs has
  `stuthedew` as both `actor` and `triggering_actor`: the owner's account, which
  a session's GitHub calls go through. No event on #395 was raised by the
  workflow token. The one workflow that does write to a pull request's branch,
  `.github/workflows/update-armed.yml`, already makes that write with
  `UPDATE_BRANCH_TOKEN`, a personal access token, and its header says why:
  runs started by `GITHUB_TOKEN` wait for approval.
- **What reads zero is the combined commit status.** Asked on 2026-09-27,
  GitHub's combined status for #395's head (the endpoint the GitHub MCP's
  `pull_request_read` serves as `get_status`) returned `state: pending`,
  `total_count: 0`, no statuses, while the same head's check runs read three,
  all successful. Actions reports through check runs, not commit statuses, so
  that endpoint reads "pending, none" on every head in this repository. That is
  this item's observation word for word: zero runs, not queued, not cancelled,
  none created. That the diagnosing session read that endpoint is inferred,
  since its transcript is not in the tree, but nothing else found reads zero.
- **This repository's own tools read the right one.** `tools/update_armed.py`'s
  `failed_checks` reads `/commits/{sha}/check-runs` and says commit statuses are
  not read; nothing under `tools/` or `subprojects/docket/src/` reads the
  combined status (searched 2026-09-27).

**Closed with no workflow change.** The cause is named above, and pull
requests opened from agent sessions do create both check runs: #395's did
within three seconds, and #1168 had both on every head it carried on
2026-09-27. Done-when's last clause covers a cause no workflow file can fix,
and there was no missing run to make visible. What is left is a reader's
error, not a CI gap: a session asking for `get_status` rather than
`get_check_runs` sees "pending, none" on a green pull request. It is recorded
here rather than as a line in `docs/worker.md`, which a worker reads before
its first edit and never at the moment anyone checks a pull request's CI.
