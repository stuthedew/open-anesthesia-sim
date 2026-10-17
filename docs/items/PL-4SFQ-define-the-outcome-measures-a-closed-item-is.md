---
id: PL-4SFQ
title: Define the outcome measures a closed item is scored on - rework items citing it, recurrences, reopenings, churn on its files, red CI runs and review findings - and snapshot the CI run history before GitHub's 90-day deletion removes it
priority: P2
effort: M
status: ready
classes: session-cost, infra
feature: model-evidence
touches: .claude/skills/model-review, docs/ci-runs.tsv
added: 2026-10-17
payoff: whether a cheaper or dearer setting held up is read from defined signals rather than impression, and the CI half of that evidence stops being deleted before anyone reads it
verify: grep -q 'Outcome measures' .claude/skills/model-review/SKILL.md && grep -q 'ci-runs.tsv' .claude/skills/model-review/SKILL.md
---

**Problem.** Define the outcome measures a closed item is scored on - rework items citing it, recurrences, reopenings, churn on its files, red CI runs and review findings - and snapshot the CI run history before GitHub's 90-day deletion removes it

**Why it matters.** The model review (`PL-63CB`) needs three measured
quantities. Treatment is the model and effort, and cost is tokens, dollars and
time; both come from the session ledger (`PL-92ZN`). Outcome, whether the work
held up, is the hardest to define and the one the owner's examples turn on,
and it accrues over weeks after the item closes. The store already holds
candidate signals, counted 2026-10-17: 122 items carry `recurrences:`, 98
`reenters:`, 63 `root-cause-of:`, 7 titles say "found in PL-", 74 briefs
mention a reopening, 1,059 items are classed defect and 79 refactor, and
2,197 items cite another item id across 12,371 edges. Two signals expire. GitHub
deletes workflow runs after 90 days, so red runs per pull request and pushes
after the first red run must be captured before they vanish; `PL-JYJJ` found
this and was dropped for want of a consumer, and this item is that consumer.
Review threads persist on GitHub.

**Done when.** The model review skill's section "Outcome measures" defines
each measure operationally: the field or command it is read from, its window
(recommended 30 days for an implementation item and 90 for a design item,
re-scored at every pass), and how it is normalized by the item's size. The
measures include, at least: later items citing the item that are classed
defect or refactor, with their cost; recurrence and re-entry fields naming it;
reopening of a decision it took; churn on the files its pull request added or
changed; red CI runs on its pull request and pushes after the first; and
review findings on its pull request. `docs/ci-runs.tsv` holds one row per
workflow run on a pull request branch (run id, pull request, head commit,
conclusion, date), the review refreshes it, and the first snapshot covers
every run GitHub still holds.

**Generator check.** Work the owner asked for on 2026-10-17. The CI retention
half re-files `PL-JYJJ`'s finding with the consumer it lacked; not an instance
of a head.
