---
id: PL-MQ50
title: bin/docket inflow names PL-4W2L (whether a branch's diff weakens its tests) re-entered by PL-MR8Z, PL-W6ZD and PL-CZXN since 2026-10-19, with no successor head and no no-successor answer: decide which is owed
priority: P2
effort: S
status: ready
classes: housekeeping
feature: generator-heads
touches: docs/items
added: 2026-11-01
payoff: bin/docket inflow stops asking every session whether the check for weakened tests held, because the answer and its reason are recorded
verify: grep -q '^\*\*Answer' docs/items/PL-MQ50*.md
---

**Problem.** bin/docket inflow names PL-4W2L (whether a branch's diff weakens its tests) re-entered by PL-MR8Z, PL-W6ZD and PL-CZXN since 2026-10-19, with no successor head and no no-successor answer: decide which is owed

**Evidence.** `bin/docket inflow`, run on 2026-11-01, prints this head under
"Re-entered by three or more filings, a generator whose fix did not hold". It
prints no successor and no `no-successor:` answer for it. No open item named
the head before this one. All three re-entering items are closed. `PL-FM15`
is the model for the answer.

**Why it matters.** `bin/docket inflow` prints this line on every run until an
item answers it, so each session that reads the report is asked the same
question again. If the fix of `PL-4W2L` did not hold, a successor head is owed,
and it ranks as a generator. If the fix held, a `no-successor:` answer with its
reason stops the question from returning.

**Read at triage, 2026-11-01.** These are facts from the four item files, not
the answer. `PL-4W2L` replaced verify's line matcher with parsed statements
compared against the base, and closed on 2026-09-23. `PL-MR8Z` (filed
2026-10-04) and `PL-W6ZD` (filed 2026-10-10) were found by `PL-R417`'s sweeps
of every reader. Both are defects in the unified-diff reader that the check
used. `PL-CZXN` (filed 2026-10-19) found that sessions waived about 15 of the
check's 17 rejections. Its fix merged in `#1728` on 2026-10-24. That fix removed
the check "no existing assertion removed" and replaced it with mutation testing
of the lines a branch changed. So the mechanism that `PL-4W2L` built is no
longer in the tree.

**Done when.** This brief records the answer, with its reason, in a paragraph
that opens `**Answer`, as `PL-FM15` does. Either this item sets
`no-successor: PL-4W2L`, or the answer names a successor head that records
`root-cause-of:`, `generator:`, `misread:` and `reenters: PL-4W2L`.
Afterwards `bin/docket inflow` no longer lists `PL-4W2L` under "a generator
whose fix did not hold".

**Generator check.** One-off. This item records a decision about `PL-4W2L`'s
line and does not misread a fact itself.
