---
id: PL-YVV4
title: Run the suppression count expert-review.md requires before any triage-bar change
priority: P2
effort: M
status: ready
classes: planning
feature: queue-hygiene
touches: docs/items
added: 2026-09-13
verify: grep -q '^## The count' docs/items/PL-YVV4-run-the-suppression-count-expert-review-md.md && bin/docket check
---

**Problem.** `.claude/rules/expert-review.md` requires that before proposing to
tighten any bar, filter or threshold, a session states what the suppressed side
would have to be worth for the proposal to be wrong, and then measures it.
`PL-VV6N` (retention rule for items captured but never worked) is a tightening
proposal and no such count has been run for it.

**Why it matters.** `PL-LKGL` and `PL-27S8` record the last time this was
skipped: a session measured the workflow lane's self-generation rate at 0.69
items per item worked and proposed raising the apparatus capture bar on the
strength of it. The count it never ran - how many open items that bar would have
suppressed - came back 67% still-real findings, which killed the proposal. This
is the same proposal shape.

**Done when.** For the 70 open P3 items, each is read and classified as would-
still-be-real or would-not-have-mattered, and the break-even is stated: the
retention rule is worth adopting only if fewer than N% of what it suppresses
would have mattered. Note that 91% of open P3 items have never appeared in a
commit touching a non-item file (6 of 70), which is a measure of *not yet
worked*, not of *not real* - the distinction is the whole point of the count and
it needs reading, not counting.
## Triaged 2026-09-13

`PL-VV6N` (decide a retention rule for items captured but never worked) already
declares `blocked-by: PL-YVV4`, so the edge this count sits upstream of is in
the store rather than only in prose. Nothing to add there.

The `verify:` command looks for a `## The count` heading in this file. That is
deliberate: the deliverable is the classification and the stated break-even
recorded *here*, where the proposal resting on it can read them, not a number in
a reply that no later session sees. `PL-LKGL` is the precedent - the count that
killed the last tightening proposal is only reconstructable because it was
written down.
