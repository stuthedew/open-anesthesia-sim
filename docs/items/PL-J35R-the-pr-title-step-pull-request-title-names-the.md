---
id: PL-J35R
title: The pr-title step 'pull request title names the items it closes' failed in 102 of the 643 red CI runs recorded in docs/ci-runs.tsv from 2026-08-22 to 2026-10-26; find whether some of those fail by design, such as a draft opened by bin/docket claim with a title written from the item, and if so add the step to the model review's hold list
priority: P3
effort: S
status: ready
classes: infra
feature: model-review
touches: .claude/skills/model-review/SKILL.md
added: 2026-10-26
payoff: the model review's red-run measure stops counting pull request titles that fail only until the title is edited, if that is what most of the 102 failures are
verify: grep -qE '^\*\*Measured\.' docs/items/PL-J35R-*.md
---

**Problem.** The pr-title step 'pull request title names the items it closes' failed in 102 of the 643 red CI runs recorded in docs/ci-runs.tsv from 2026-08-22 to 2026-10-26; find whether some of those fail by design, such as a draft opened by bin/docket claim with a title written from the item, and if so add the step to the model review's hold list

**Why it matters.** The model review compares red CI runs per pull request across models, effort levels and weeks. `PL-SW87` took the two `pr-title` record holds out of that count, because they fail by design until a later hand step. This step was left in. If many of its 102 failures are the expected order of work rather than mistakes, the red-run measure still carries a by-design share, and a week with more claims or more fix-now closures looks worse than it was.

This step differs from the two holds in one way that matters. It also catches real mistakes, such as a title that leaves out an item the branch closes. So adding the whole step to the hold list would hide those. The likely answer is a rule that leaves out only the by-design failures, not the step.

**Done when.** The 102 failures, or every one still readable, are sorted by cause, with counts, under a `**Measured.**` paragraph in this item. A deterministic signal to try first: `pr-title` runs again when the title is edited, so a failed run followed by a green `pr-title` run on the same `head_sha` was cleared by a title edit with no new commit. Then one of three outcomes follows, chosen on the counts. If the step fails only by design, it joins the hold list in `.claude/skills/model-review/SKILL.md`. If it fails by design in a subset that a rule over `docs/ci-runs.tsv` can name, that rule goes into the skill's red-run row. If the by-design share is small, the item records that and the count stays as it is.

**Generator check.** Not a generator. This item asks a measurement question that `PL-SW87`'s refresh opened, and no reader misread a fact. The fact it would settle, which CI steps fail by design, is held once, in the model review skill's hold list, and this item adds to that record rather than copying it.
