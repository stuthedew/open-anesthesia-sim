---
id: PL-2D1S
title: Find what drives the rise in red CI runs per pull request, from 17% of closed items in ISO week 38 to 49% in week 43
priority: P2
effort: M
status: ready
classes: infra
feature: model-review
touches: docs/items
added: 2026-10-25
payoff: the cause of the doubling in red CI runs per pull request is named and has an item
verify: grep -qE '^\*\*Classified\.' docs/items/PL-2D1S-*.md
---

**Problem.** Find what drives the rise in red CI runs per pull request, from 17% of closed items in ISO week 38 to 49% in week 43

**Measured 2026-10-25, in the first model review** (`docs/model-review.md` §
"Run of 2026-10-25, the first"). The share of closed items whose pull request
had at least one failed CI run, by the ISO week the item closed: 18% in week
36, 23% in week 37, 17% in week 38, 30% in week 39, 25% in week 40, 37% in
week 41, 32% in week 42 and 49% in week 43. Runs were joined to a pull request
through its head branch and the time it was open, from `docs/ci-runs.tsv`.
Part of week 43 is `#1773`, which broke the second test job on every
apparatus pull request until `#1774`. The rise began weeks before that.

**Why it matters.** A red run costs a push and a wait, and the rise confounds
every comparison of red runs between models, effort levels and origins.

**Done when.** The failed runs since week 39 are classified by the failing
job and step (a check that refused correct work, a real defect caught, a
flaky test, a break on the base branch), with counts, and the largest class
has an item.
Record the classification in a `**Classified.**` paragraph here.

**Generator check.** Not yet known: this item is the search for a mechanism.
If the classification finds one mechanism behind three or more red-run
causes, record it as a generator then.
