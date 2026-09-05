---
id: PL-9HDH
title: The pr-title workflow buys a whole billable minute for twelve seconds of work the floor job already pays for and leaves idle
status: dropped
feature: ci-cost
touches: .github/workflows/quality.yml, .github/workflows/pr-title.yml
added: 2026-09-05
closed: 2026-09-05
reason: Would reintroduce the defect PL-3V8K and PL-0ZP8 both diagnosed
  independently. `quality.yml`'s `pull_request` trigger excludes `edited` on
  purpose, because adding it would re-run the whole suite on every title and
  body edit. So a title check living in that workflow cannot see a corrected
  title - the rename it asks for fires no event, and an Actions re-run replays
  the stale one, leaving the job red with no way to clear it but a new commit,
  which the working agreement forbids pushing to kick CI. That is exactly what
  splitting `pr-title.yml` out fixed in #256. The billable minute it buys is the
  correct price for a check that can clear itself. PL-D551 took the half that is
  sound - folding the floor job in - and stopped there.
---

**Problem.** The pr-title workflow buys a whole billable minute for twelve seconds of work the floor job already pays for and leaves idle

**Why it matters.**

**Where.**

**Done when.**
