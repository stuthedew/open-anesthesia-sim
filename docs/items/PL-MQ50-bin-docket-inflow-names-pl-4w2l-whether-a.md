---
id: PL-MQ50
title: bin/docket inflow names PL-4W2L (whether a branch's diff weakens its tests) re-entered by PL-MR8Z, PL-W6ZD and PL-CZXN since 2026-10-19, with no successor head and no no-successor answer: decide which is owed
priority: P2
effort: S
status: done
classes: housekeeping
feature: generator-heads
touches: docs/items
added: 2026-11-01
closed: 2026-11-02
pr: 1928
payoff: bin/docket inflow stops asking every session whether the check for weakened tests held, because the answer and its reason are recorded
verify: grep -q '^\*\*Answer' docs/items/PL-MQ50*.md
no-successor: PL-4W2L
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

**Answer: no successor head is owed for `PL-4W2L`, because the mechanism its
line asks about is no longer in the tree.** This is a session's decision,
taken under Order item 66 of the v0.7.0 project ("Fix generator-heads, drift
and stale source claim features", project owner, 2026-11-02), so ordinary
evidence reopens it. The field `no-successor: PL-4W2L` records it. The line
opens again once three more filings re-enter `PL-4W2L` after 2026-11-01. Read
on `main` at `cdf9a8fdf`.

**What each re-entry was.**

- `PL-MR8Z` (filed 2026-10-04, closed in `#1577`) and `PL-W6ZD` (filed
  2026-10-10, closed in `#1447`) were latent defects in the unified-diff
  reader that the assertion check used. `PL-R417`'s deliberate sweep of every
  reader found both. Neither had let a weakened test through in use.
- `PL-CZXN` (filed 2026-10-19, closed in `#1728`) did not find the fix
  failing to catch a weakened test. It found the check refusing intended
  rewrites, about 15 of its 17 rejections since 2026-10-01. Its fix retired
  the check "no existing assertion removed", which is the mechanism
  `PL-4W2L` built, and put mutation testing of the changed lines in its place
  (project owner, 2026-10-19, ratified, over making the old check an advisory
  and over keeping it).

So the parsed-statement comparison that `PL-4W2L` built cannot fail again,
because it is gone. A successor head would have no mechanism to fix.

**Where the question went.** `PL-4W2L`'s `misread:` is whether a branch's
diff weakens its tests. That question now belongs to `PL-CZXN`'s mutation
route, and the gaps found in that route are already recorded as re-entries of
`PL-CZXN`, not of `PL-4W2L`. `PL-7FPD` (closed in `#1753`) added the comparison
of a changed test's base and branch versions against the display modules'
mutants. `PL-H57W` (closed in `#1807`) settled the same question for core unit
tests. `PL-LBNN` asked it for apparatus tests and was dropped on
2026-10-24, because `PL-CZXN`'s ratified decision named that gap when it was
taken. `bin/docket inflow` counts `PL-CZXN` at two re-entries, so a third
filing about weakened tests would name `PL-CZXN`'s line, which is the right
line for it.

**The suppression half.** `PL-4W2L`'s `generator:` line kept the check that no
skip, fail or ignore marker is added, by `PL-G21K`'s ratified resolution.
`PL-W6ZD`'s first defect, a skip decorator moved between tests, was in that
half, and `#1447` fixed it. The one later defect in that check, `PL-3G9M`
(filed 2026-10-25, a call of `pytest_ignore_collect` counted as a
suppression), is recorded as a re-entry of `PL-G21K`, the head that owns the
marker list, so it does not belong on this line.
