---
id: PL-SRMZ
title: CI pays about two minutes per pull request push replaying every open item's verify command
status: dropped
feature: ci-cost
touches: .github/workflows/quality.yml, .github/workflows/pr-title.yml
added: 2026-09-05
closed: 2026-09-05
reason: Declined by the project owner, 2026-09-05, when it was put to them with
  the measurement (about 2 of the `checks` job's 3m44s, a third of the CI bill
  at the time). The `--verify` replay stays on every pull request push. Recorded
  rather than left open so the finding is not re-raised as new; reopen if the
  replay's cost changes materially.
---

**Problem.** CI pays about two minutes per pull request push replaying every open item's verify command

**Why it matters.**

**Where.**

**Done when.**
