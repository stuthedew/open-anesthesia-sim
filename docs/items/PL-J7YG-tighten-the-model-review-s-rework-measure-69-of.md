---
id: PL-J7YG
title: Tighten the model review's rework measure: 69% of closed items have a later defect or refactor item citing them, so it cannot rank settings
priority: P3
effort: M
status: done
classes: defect
feature: model-review
touches: .claude/skills/model-review/SKILL.md
deferred-from: v0.7.0 - a measure in the model review, which no v0.7.0 feature reads; the next review run is due about 2026-11-25
added: 2026-10-25
closed: 2026-10-25
pr: 1814
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

**Measured and decided 2026-10-25.** The first run's analysis scripts were
not kept, so the population was rebuilt the same way: `status: done` with a
`pr:`, a squash commit on `origin/main` ending "(#N)" whose body names a
session the ledger holds, not a design item, and a 30-day window closed by
2026-10-25. That gives 605 items, not 881. The ledger join finds 1,809 joined
items where the run found 1,998, and the cause was not traced. The old measure
still marks 415 of the 605 (68.6%), so the population behaves like the run's.

| Rework definition | Items marked | Rate |
| --- | --- | --- |
| Any later `defect` or `refactor` item naming the id anywhere (the old measure) | 415 | 68.6% |
| The same, but only in the citing item's `**Problem.**` paragraph | 101 | 16.7% |
| A later item's `reenters:` names the id | 16 | 2.6% |
| `reenters:`, or a `**Problem.**` paragraph citation | 109 | 18.0% |
| `reenters:`, or one of the item's own unwithdrawn `recurrences:` entries | 27 | 4.5% |

Including design items gives 793 items and the same picture: 67.7% under the
old measure and 5.7% under the last row.

A random sample of 25 of the 93 items matched only by a `**Problem.**`
paragraph (seed 20261025) was read by hand. Eight said the cited work had
failed or caused the defect, such as `PL-JBRC` under `PL-8BR0` and `PL-5KR2`
under `PL-QTSB`. Six were arguable, mostly a gap just past the cited item's
scope. Eleven cited the item as an example, a stale list entry or a missing
`pr:`. So the candidate in "Done when" is still a text match with about one
true failure in three, and it was not adopted.

The skill now names the last row as the primary outcome: a fix that did not
hold, read from `reenters:` and `recurrences:`. It also records why a citation
count is not used. The rate under-counts early windows, because `reenters:`
was first written on 2026-10-11. Seven of the eight sampled failures were
filed before that date, and none carries a `reenters:` naming the item it
cites. So the skill now says to compare settings only on items closed on or
after 2026-10-11, or to stratify by the week the item closed.
