---
id: PL-YMW8
title: PL-BKDP and PL-KFWL were filed for the same v0.4.8 tag event, and PL-BKDP's Done when is already met, so a moot P1 needs-decision entry sits in the queue and in the next gate's count
priority: P2
effort: S
status: dropped
classes: planning
feature: release-process
touches: docs/items
added: 2026-09-07
closed: 2026-09-07
reason: void on the facts, and the premise was already false when it was written. PL-BKDP is not moot but finished: `origin/claude/missing-release-v0.4.8-hwhs25` carries `6cf503e9 PL-BKDP: cut v0.4.8` and closes it `done` with a verify naming the version bump, docs/releases/v0.4.8.md and the two ROADMAP rows, and that branch is open as #440. It took route 1 of the two the item itself set out - the route it recommended. This item read the tag deletion alone as satisfying PL-BKDP's Done when; the deletion was only route 1's first half, and the cut followed within the hour on a branch that had not been pushed when the triage pass fetched. The duplicate-filing observation it recorded is kept, and moved into PL-5GBV's brief where the check that would catch it is designed
---

**Problem.** PL-BKDP and PL-KFWL were filed for the same v0.4.8 tag event, and PL-BKDP's Done when is already met, so a moot P1 needs-decision entry sits in the queue and in the next gate's count

**Why it matters.** `PL-BKDP` is `P1 · needs-decision`, so it is debt by status
in `docket.toml`'s gate rule and it is the top-band entry `bin/docket status`
prints for the `release-process` feature. Both are wrong now. Verified
2026-09-07 during the `PL-2B7B` triage pass:

- `git ls-remote --tags origin` returns no `v0.4.8`, so the tag it is about is
  gone;
- `python3 tools/doc_check.py check` reports 0 errors and 0 advisories on this
  checkout, which is `PL-BKDP`'s stated **Done when** condition;
- the decision it poses - delete the tag, or cut 0.4.8 and leave the tag behind
  the commit - was taken by the first route, outside the item.

What remains of `PL-BKDP` is one dependency on ordinary process rather than on
anybody's judgment: "the next release is cut under its own number", which is
what will happen when 0.4.8 is cut because there is no longer a tag claiming
otherwise.

**Where.** `docs/items/PL-BKDP-a-v0-4-8-tag-exists-on-the-commit-that-closed.md`
and `docs/items/PL-KFWL-the-v0-4-8-tag-is-pushed-onto-a-commit-where.md`. The
two were filed hours apart on 2026-09-07 for one event, from two different
sessions: `PL-BKDP` by `doc_check` while closing `PL-JX0Z`, `PL-KFWL` while
closing `PL-GBBZ`. `PL-KFWL` was triaged to `ready` in the `PL-2B7B` pass
holding the residue neither of them has yet - the guard, that nothing refuses or
names a tag with no cut behind it - so the two are no longer the same item, and
this is a close-out of the resolved half rather than a merge.

This pair is also a second live instance of `PL-5GBV` (surface near-duplicate
open items during triage), and is recorded in that item's brief as such. Neither
title shares a distinctive phrase beyond `v0.4.8`, which is worth knowing when
that check is designed: a title comparison alone would have caught this one only
on the version string.

**Decision needed.** Whether `PL-BKDP` closes as `dropped` with a reason - the
disposition its own condition and `PL-KFWL`'s note both support, and the one
this item recommends - or stays open until 0.4.8 is actually cut, on the
strict reading of its second clause. The triage pass that found this did not
close it, because closing a `P1 · needs-decision` item is a decision rather
than a field, and the `docket` skill's triage mode is explicit that a pass must
not become the fix.

**Done when.** `PL-BKDP` is closed with a reason naming the tag deletion and
pointing at `PL-KFWL` for the guard, or its brief says why it stays open with
`doc_check` already green.

**Correction, 2026-09-07, same day.** Everything above was written against a
checkout whose most recent fetch predated
`origin/claude/missing-release-v0.4.8-hwhs25` being pushed. On the next fetch
that branch appeared, `bin/docket show PL-BKDP` marked the item **IN FLIGHT**,
and the branch turned out to have cut v0.4.8 and closed `PL-BKDP` as `done` -
route 1 in full, not merely its first half. So the recommendation in **Decision
needed** is withdrawn: `PL-BKDP` is finished work awaiting the merge of `#440`,
not a moot entry to drop. The reading that produced this item - "the tag is gone
and `doc_check` is green, therefore the Done when is satisfied" - was wrong
because route 1 has two halves and only one had happened.

The transferable lesson is not about this item. It is that `bin/docket status`
and `bin/docket gate` read the checkout, so an entry can be stale by an hour
without anything saying so, and the guard that catches it is the fetch plus
`bin/docket show <id>` that the `docket` skill already requires before starting
an item. This pass ran that guard before editing `PL-BKDP` and it did its job.
