---
id: PL-NST2
title: claims.holdings reads status dispositions, the landed prefix, the item resource field and cut holds, and adapts to FlightReport
priority: P2
effort: M
status: ready
classes: defect
feature: claim-record
touches: subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claims.py, subprojects/docket/src/docket/vcs.py
blocked-by: PL-3FYK
deferred-from: v0.6.0 - filed after the freeze by PL-MB2W's design round (2026-09-24), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-24
payoff: part of the claim record that ends PL-MB2W's generator: one recorded fact decides who holds an item
verify: grep -q 'def flight' subprojects/docket/src/docket/claims.py && grep -q 'def holder' subprojects/docket/src/docket/claims.py
---

**Problem.** claims.holdings reads status dispositions, the landed prefix, the item resource field and cut holds, and adapts to FlightReport

**Part of `PL-MB2W`'s design** (who holds an item is recorded as a claim; design round of 2026-09-24, in `PL-MB2W` under "Design round, 2026-09-24"). Read that section's spec before starting: this brief names only this item's slice of it.

The rest of the reader: a disposition hold (the ref's tip `status:` differs from the fork copy and the base copy, the item exists at the fork and on the base, the base has not superseded the ref's copy; read by id prefix so a rename does not matter; status only; carries the ref's lease; never orders against claims and never holds arming); the landed-prefix test (the newest commit k in `base..R` whose added blobs have all been on the base spends every claim at or before k), replacing `_taken_on_base`; `resource:` read from the claimed item's copy on the claiming ref; cut holds (today's `cuts_in_flight` read); `Holdings.flight()` returning today's `FlightReport` shape.

Tests: a capture absent at the fork holds nothing; a block is a disposition (`PL-8GV1`); landed prefix after a partial squash (`PL-8JQQ`); a `verify:` rewrite across many items holds nothing (`PL-3W3P`).

**Why it matters.** `PL-MB2W` is a live generator: twenty items were each a new shape of work that some reader misread, because who holds an item is inferred from commit subjects, touched paths and ref age. This item is one slice of replacing that inference with a recorded claim, and the generator stops producing members only once the slices through `PL-DDYD` land.

**Done when.**

- `Holdings` reports disposition holds, cut holds and the `resource:` a claim is on, and spends claims by the landed-prefix test.
- `Holdings.flight()` returns a `FlightReport` that today's callers accept unchanged.

**Build order.** After `PL-3FYK`.
