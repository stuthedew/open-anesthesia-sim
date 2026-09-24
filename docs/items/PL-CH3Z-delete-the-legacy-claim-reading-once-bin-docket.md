---
id: PL-CH3Z
title: Delete the legacy claim reading once bin/docket flight prints legacy refs: 0
priority: P2
effort: S
status: blocked
classes: defect
feature: claim-record
touches: subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claims.py, tools/branch_id_check.py
blocked-by: PL-N162, PL-J9S0
deferred-from: v0.6.0 - filed after the freeze by PL-MB2W's design round (2026-09-24), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-24
payoff: part of the claim record that ends PL-MB2W's generator: one recorded fact decides who holds an item
---

**Problem.** Delete the legacy claim reading once bin/docket flight prints legacy refs: 0

**Part of `PL-MB2W`'s design** (who holds an item is recorded as a claim; design round of 2026-09-24, in `PL-MB2W` under "Design round, 2026-09-24"). Read that section's spec before starting: this brief names only this item's slice of it.

Remove the legacy reading and the CI skip for legacy commits. Starts only once `flight` prints `legacy refs: 0`, which is a fact about the refs rather than a date.

**Why it matters.** `PL-MB2W` is a live generator: twenty items were each a new shape of work that some reader misread, because who holds an item is inferred from commit subjects, touched paths and ref age. This item is one slice of replacing that inference with a recorded claim, and the generator stops producing members only once the slices through `PL-DDYD` land.

**Done when.**

- No legacy reading remains in `claims.py` or `tools/branch_id_check.py`.

**Build order.** After `PL-N162`, `PL-J9S0`.
