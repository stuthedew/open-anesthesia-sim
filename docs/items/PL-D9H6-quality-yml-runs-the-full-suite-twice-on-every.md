---
id: PL-D9H6
title: quality.yml runs the full suite twice on every push to a branch with an open pull request
priority: P3
effort: S
status: done
classes: infra
feature: dev-tooling
touches: .github/workflows/quality.yml
closed: 2026-09-01
pr: 138
commit: 13b0c2e
added: 2026-08-31
verify: ! grep -qF 'on: [push, pull_request]' .github/workflows/quality.yml && grep -qF '    branches: [main]' .github/workflows/quality.yml && grep -qF '  pull_request:' .github/workflows/quality.yml
---

**Problem.** `.github/workflows/quality.yml` is triggered by
`on: [push, pull_request]`. Once a branch has an open pull request, every push
to it fires both events, so the `checks` job — `ruff format --check`,
`ruff check`, `mypy`, `pytest`, `docket check`, `doc_check`, about 50 seconds —
runs twice for the same commit.

Found 2026-08-31 while designing `PL-N7R9` (the pull request stops being a
question). It is not caused by that item, but that item makes pull requests
open earlier in a session's life, so the doubled window widens from "the minute
before merge" to "the whole implementation".

**Why it matters.** Doubled CI minutes on every push, and two check runs per
commit in the pull request's checks list where a reader expects one. It is
mild, which is why it is `P3` — but it is also two lines to fix and it is
currently invisible because nobody reads a green check twice.

**Where.** `.github/workflows/quality.yml`, the `on:` key. The standard
resolutions are to scope `push` to the default branch
(`on: {push: {branches: [main]}, pull_request: {}}`), so branch pushes are
covered by the `pull_request` event alone, or to add a `concurrency` group
keyed on the ref that cancels the superseded run. The first is the smaller
change and matches how the repository actually works, since every branch here
becomes a pull request.

**Not urgent, and deliberately not bundled.** `PL-N7R9` is a `CLAUDE.md` edit
and this is a CI config edit; pairing them would put an unrelated workflow
change inside a rule change the owner is reading closely.

**Done when.** A push to a branch with an open pull request produces one
`checks` run rather than two, and pushes to `main` are still covered.
