---
id: PL-FX5Q
title: Delete the claim inference and the three promotions from vcs.py, with their tests
priority: P2
effort: M
status: blocked
classes: defect
feature: claim-record
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
blocked-by: PL-N162
deferred-from: v0.6.0 - filed after the freeze by PL-MB2W's design round (2026-09-24), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-24
payoff: part of the claim record that ends PL-MB2W's generator: one recorded fact decides who holds an item
---

**Problem.** Delete the claim inference and the three promotions from vcs.py, with their tests

**Part of `PL-MB2W`'s design** (who holds an item is recorded as a claim; design round of 2026-09-24, in `PL-MB2W` under "Design round, 2026-09-24"). Read that section's spec before starting: this brief names only this item's slice of it.

Delete the claim use of `_annotates_only`; `_Walk`'s claim fields and `credit_claims`; `_queue_only_touches` and `_queue_only_work`; `_deciding_on_base`, `_modified_by` and `_own_edit_claims`; `_claimed_again_since` and `_taken_on_base`; `Carrier`, `_head_carries` and precedence's re-walk; and the tests that pin them. `_closed_at_ref` becomes the reader's `status_at`. Kept: the landing machinery, `leading_ids`, `editing`, `unattributed`, and the unread/unbounded guards.

**Why it matters.** `PL-MB2W` is a live generator: twenty items were each a new shape of work that some reader misread, because who holds an item is inferred from commit subjects, touched paths and ref age. This item is one slice of replacing that inference with a recorded claim, and the generator stops producing members only once the slices through `PL-DDYD` land.

**Done when.**

- None of the named helpers remain in `vcs.py`, and no test pins them; `make check` passes.

**Build order.** After `PL-N162`.
