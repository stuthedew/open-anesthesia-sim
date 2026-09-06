---
id: PL-7RTN
title: An open pull request can carry no check runs at all, so a branch merges with nothing having gated it
status: untriaged
added: 2026-09-06
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
