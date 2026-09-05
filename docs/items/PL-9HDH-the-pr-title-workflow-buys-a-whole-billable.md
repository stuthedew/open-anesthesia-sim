---
id: PL-9HDH
title: The pr-title workflow buys a whole billable minute for twelve seconds of work the floor job already pays for and leaves idle
priority: P3
effort: S
status: needs-decision
classes: infra
feature: ci-cost
touches: .github/workflows/quality.yml, .github/workflows/pr-title.yml
added: 2026-09-05
---
**Problem.** `pr-title.yml` is billed a whole Actions minute for a job
observed at twelve seconds — one checkout, one `setup-python`, one
standard-library script. `quality.yml`'s `floor` job is billed the same whole
minute for eight seconds and sits idle for the rest of it, so every pull
request pays two billable minutes for twenty seconds of work.

**Why it matters.** It is a per-pull-request cost that recurs for the life of
the project and buys nothing — the second minute is a second runner, not
additional coverage. `PL-D551` is the same observation from the other side, and
the two have to be answered together: each proposes moving work into a job the
other proposes moving.

**Where.** `.github/workflows/pr-title.yml`; `.github/workflows/quality.yml`,
the `floor` job.

**Decision needed.** This is not a mechanical merge. `pr-title.yml` was
split out of `quality.yml` under `PL-3V8K` for a trigger reason rather than a
cost one. The check asks an author to rename a pull request; a rename fires
`pull_request: edited`; `quality.yml` does not subscribe to that type. Folding
the job into `floor` reinstates exactly the failure `PL-3V8K` fixed — observed
on #256, where doing what the check asked could not clear it — unless
`quality.yml` also gains `edited`, which its own comment rejects because that
reruns sync, ruff, mypy, the full test suite, docket, doc_check and contrast on
every body edit made while iterating on a description.

So the standing choice is between paying the second minute and paying
full-suite reruns on description edits. A third route has not been costed: a
job inside `quality.yml` gated by a job-level `if` on the event type, which
would let `edited` be added without the other jobs running on it.

**Done when.** The project owner has chosen between keeping the split, folding
`pr-title` into `floor` behind an added `edited` trigger, and the filtered
third option, and the choice with its reasoning is recorded here.
