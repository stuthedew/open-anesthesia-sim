---
id: PL-3FYK
title: Record who holds an item as a Claim trailer bound to the holder's own branch, read by one claims.holdings reader under a 7-day lease
priority: P2
effort: M
status: done
classes: defect
feature: claim-record
touches: subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claims.py
deferred-from: v0.6.0 - filed after the freeze by PL-MB2W's design round (2026-09-24), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-24
closed: 2026-09-24
payoff: part of the claim record that ends PL-MB2W's generator: one recorded fact decides who holds an item
verify: grep -q 'def holdings' subprojects/docket/src/docket/claims.py && grep -q 'LEASE_TERM' subprojects/docket/src/docket/claims.py && grep -q 'def test_' subprojects/docket/tests/test_claims.py
---

**Problem.** Record who holds an item as a Claim trailer bound to the holder's own branch, read by one claims.holdings reader under a 7-day lease

**Part of `PL-MB2W`'s design** (who holds an item is recorded as a claim; design round of 2026-09-24, in `PL-MB2W` under "Design round, 2026-09-24"). Read that section's spec before starting: this brief names only this item's slice of it.

The core of the reader: the `Claim:`/`Yield:` trailer grammar and its read (`git log --no-merges` with `%(trailers:key=Claim,valueonly,separator=%x1e)`, git >= 2.22 declared as the floor and declined below it); binding a claim to the ref whose name equals its `<branch>` token; the 7-day lease renewed by non-merge commits (`%cI`) with break-then-reclaim; ordering by `(%aI, hash)` with `over <ref>@<hash>` sorting ahead of the claim it names; release by `Yield`, by the branch copy reaching a releasing status, by `over`, by lapse; legacy decided per commit tree (a claim commit whose tree lacks `claims.py`); the unread and unbounded ref guards inherited from `vcs.py`; one UTC `now` per call.

Tests use real git in temporary repositories: the trailer in the last paragraph, the branch token, the lease chain with an explicit `now`, `%aI` against `%cI` after a rebase, and a legacy start commit after merging main.

**Decision for the project owner, held here because this item defines `RELEASING_STATUSES`.** Should a claim also be released when the branch's own copy of its item moves to `blocked`, not only `done` or `dropped`? It reopens `PL-KWCY`'s ratified arming rule ("it holds until its item is closed in the branch's own copy"), which is why it is the owner's.

**Recommended: yes.** A session that blocks its own item has stopped working it, and holding the claim strands a queue-only branch that never arms. It is one constant, so building this item never waited on the answer.

**Why it matters.** `PL-MB2W` is a live generator: twenty items were each a new shape of work that some reader misread, because who holds an item is inferred from commit subjects, touched paths and ref age. This item is one slice of replacing that inference with a recorded claim, and the generator stops producing members only once the slices through `PL-DDYD` land.

**Done when.**

- `claims.py` reads `Claim:`/`Yield:` trailers bound to their branch token, under a 7-day lease with break-then-reclaim, ordered by `(%aI, hash)` with `over`, and declines below git 2.22.
- Legacy claim commits are told apart by their own tree, and the tests named above run against real git.

**Answered 2026-09-24: yes** (project owner, 2026-09-24, ratified, over holding the claim until the item is `done` or `dropped`, `PL-KWCY`'s rule). Ship `RELEASING_STATUSES = CLOSED_STATUSES + ("blocked",)`. `CLAUDE.md`'s arming bullet was amended in the same session, so the prose rule already reads this way.

**Build order.** First; nothing blocks it.
