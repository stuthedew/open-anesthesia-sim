---
id: PL-YVV4
title: Run the suppression count expert-review.md requires before any triage-bar change
priority: P2
effort: M
status: done
classes: planning
feature: queue-hygiene
touches: docs/items
added: 2026-09-13
closed: 2026-10-11
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

## The count

**Run 2026-10-11 over every open `P3` item, 144 on `main` at `103b07d6`.** The
brief's 70 is the 2026-09-13 figure. Six agents each read a sixth of the briefs
through `bin/docket show` and checked every claim against the tree at that
commit. Each returned a verdict with its evidence: *real* (what the item names
still holds), *partly* (some of it does), or *dead* (fixed by other work,
overtaken, or obsolete). Three verdicts were settled by hand, below. The
per-item tables are in the project's shared folder, at
`v0.6.0/yvv4-count/batch1.md` to `batch6.md`.

| Slice | Items | Still real | Dead | Still real, share |
| --- | --- | --- | --- | --- |
| All open `P3` | 144 | 135 | 9 | 94% |
| filed 14 days ago or less | 40 | 39 | 1 | 98% |
| filed 15 to 28 days ago | 90 | 83 | 7 | 92% |
| filed over 28 days ago | 14 | 13 | 1 | 93% |
| never worked | 127 | 118 | 9 | 93% |
| worked at least once | 17 | 17 | 0 | 100% |

"Never worked" is the brief's own measure: no commit leading with the item's
id touches a path outside `docs/items`. Two of the 144, `PL-CPLX` and
`PL-TDBT`, were worked and closed in `#1407` while the count ran, and are
counted as worked. *Still real* includes six partly real items: `PL-5GBV`,
`PL-FYV7`, `PL-H71N`, `PL-VHHB`, `PL-Y4YX` and `PL-Y5ZB`. Their briefs claim
more than is left, and the re-confirmation `bin/docket show` already asks for
on an item over 14 days old is where each is trimmed. The oldest open `P3` was
filed 48 days ago, and the median 19.

**The three settled by hand.**

- `PL-X5PK`, dead. `PL-MT3R` (`#1116`, 2026-09-26) overtook it: `flight` drops
  a tracking ref whose branch the remote no longer lists. That was this case's
  whole geometry, since `#823`'s head was deleted on merge and the ref
  survived only in one checkout.
- `PL-LWMS`, dead, because its condition never arose. `PL-SL16` closed on
  2026-09-24 (`#1001`). Since then `origin/main` has carried 401
  `Co-authored-by:` trailers, and every one is the plain
  `Claude <noreply@anthropic.com>`.
- `PL-VHHB`, partly real rather than dead. The "nothing computational moved"
  wording left the release notes after v0.5.5. A cut where `core/` moves still
  has to show that the outputs did not, though, and nothing under `tools/`
  re-runs that comparison.

**Break-even.** A rule that closes `P3` items nobody works is right only if
fewer than *b* of what it closes would have mattered, where
*b* = *c* / (*c* + *r*):

- *c* is what a dead item costs while it stays open. That cost is mainly a
  read: the last whole-store sweep read 145,000 tokens of briefs across 166
  items, about 870 an item (`PL-JB3Z`), and a dead item is read again by every
  sweep and triage pass until something drops it.
- *r* is what a still-real item costs once closed. It is at least the same
  read again, when a later session re-finds the finding. At worst it is a
  defect that ships because nobody does re-find it.

Granting that *r* is no larger than *c*, *b* is 50%. With *r* at a
re-diagnosis of several thousand tokens, *b* falls near 10%. Every measured
slice is 92% to 100% still real, so the rule fails by a wide margin at either
bound. The slices a rule could target are no deader than the whole: 93% for
never worked, and 93% for filed over 28 days ago. An age threshold of the kind
`PL-VV6N` cites would close nothing today, since the oldest open `P3` is 48
days old: VS Code's is 60 days and home-assistant's stale bot uses 90. This
is the third count to come out this way, after `PL-LKGL`'s 67% still real and
`PL-JB3Z`'s 10% precision for dropping the `P3` band.

**What follows.** No retention rule. `PL-VV6N` is dropped on its own second
ending, with capture declared deliberately unbounded. The nine dead are dropped
in the same commit, each with its evidence.
