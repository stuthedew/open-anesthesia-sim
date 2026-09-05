---
id: PL-W9DW
title: No spending limit and no usage alert, so the first sign of Actions overage is the invoice
priority: P2
effort: S
status: ready
classes: infra
feature: ci-cost
touches: docs/maintainer.md
added: 2026-09-05
verify: python3 tools/doc_check.py check && grep -q 'spending limit' docs/maintainer.md
not-delegable: The limit and the alert are set in GitHub's billing settings for the account, outside this repository; no command in the tree can prove either exists, and the `verify` above proves only that what was set has been written down.
---
**Problem.** The repository has no Actions spending limit and no usage
alert, so the first signal that the workflows have run past the included
minutes is the invoice.

**Why it matters.** `PL-9HDH` and `PL-D551` are both about per-run Actions
cost, and neither is measurable without a figure to measure against. A limit is
also the only mechanism here that fails safely: without one, a workflow that
loops or a matrix that expands bills silently until a person notices, and
nothing in this repository can notice.

**Where.** GitHub's billing settings for the account, which is outside this
repository; `docs/maintainer.md`, which is where what only the project owner
can act on is recorded.

**Done when.** A spending limit and a usage alert are set, and
`docs/maintainer.md` records both values and where they are changed.
