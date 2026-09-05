---
id: PL-W9DW
title: No spending limit and no usage alert, so the first sign of Actions overage is the invoice
status: done
feature: ci-cost
touches: .github/workflows/quality.yml
priority: P3
effort: S
classes: infra
added: 2026-09-05
closed: 2026-09-05
not-delegable: The work is a GitHub account billing setting, not a change to
  this repository, so nothing in the tree can prove it. `docket verify` would
  have to read the owner's billing page to answer, which it cannot and should
  not be able to. Confirmed done by the project owner, 2026-09-05.
---

**Problem.** No spending limit and no usage alert, so the first sign of Actions overage is the invoice

**Why it matters.**

**Where.**

**Done when.**

**Done.** The project owner set a budget with alerts on 2026-09-05, at
https://github.com/settings/billing -> Budgets and alerts.

Worth keeping for whoever reads this later: the alert matters *because* the
repository is private. Public repositories get standard runners free and
unmetered, so if the plan to go public is carried out this item's whole subject
disappears - which is a reason to revisit the budget then rather than to leave
a stale one in place.
