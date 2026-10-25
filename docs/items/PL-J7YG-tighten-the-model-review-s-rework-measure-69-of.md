---
id: PL-J7YG
title: Tighten the model review's rework measure: 69% of closed items have a later defect or refactor item citing them, so it cannot rank settings
priority: P3
effort: M
status: ready
classes: defect
feature: model-review
touches: .claude/skills/model-review/SKILL.md
deferred-from: v0.7.0 - a measure in the model review, which no v0.7.0 feature reads; the next review run is due about 2026-11-25
added: 2026-10-25
payoff: the next model review ranks model and effort settings on a rework rate that separates failed work from work merely cited
verify: ! grep -qF 'later items whose brief names the item' .claude/skills/model-review/SKILL.md
---

**Problem.** Tighten the model review's rework measure: 69% of closed items have a later defect or refactor item citing them, so it cannot rank settings

**Measured 2026-10-25, in the first model review** (`docs/model-review.md` §
"Run of 2026-10-25, the first"). The skill's "Rework citing it" measure counts
a later item whose classes include `defect` or `refactor` and whose brief names
the item's id anywhere. 608 of the 881 closed items with a closed 30-day
window match it. Briefs in this store cite ids freely, as context, as
precedent and as pointers, so a citation rarely means the cited work failed.
The run used the rate at which a fix did not hold instead, read from
`recurrences:` and `reenters:`: 36 of 881 (4.1%). That rate is triage's own
judgment, not a text match.

**Why it matters.** Every later run ranks model and effort settings on its
outcome measures. A measure that marks most items as failures hides a real
difference between settings and can manufacture a false one.

**Done when.** The skill's outcome table defines rework so that a citation
counts only when it says the cited work failed, or the measure is replaced by
`reenters:` and `recurrences:` as the primary outcome. A candidate: count a
citing item only when its id appears in `reenters:` or in its
`**Problem.**` paragraph. Measure the candidate's rate on the same 881 items
before choosing.

**Generator check.** One measure defined once, in one skill. A one-off.
