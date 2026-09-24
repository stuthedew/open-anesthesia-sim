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

## Design notes, 2026-09-24 (the implementing session)

Choices made inside the spec, recorded so an interrupted session is not re-derived:

- **Three tuples, not one.** `Holdings.holds` stays the claims, and dispositions and cuts get `dispositions` and `cuts`, each `Hold` still marked by `kind`. Every claims-only reader - `claim`, `yield`, `arm`, `branch_id_check` - would otherwise filter on `kind`, and the one that forgot would read a grooming pass as a claim: the `QueueEdit`/`Branch` split, for the same reason.
- **Landed prefix, made sound.** Read literally, "the newest commit whose added blobs have all been on the base" is true of every empty commit, and so of the claim commit itself, and of a commit reverting a file to a version the base once held. So k must add at least one blob, all of them on the base, and the branch *as of k* must pass `_work_already_on_base` against its fork. The per-commit blob test is a necessary condition of the second (a blob k adds is either in its net diff or is the fork's own), so it filters the candidates for free from the `--raw` walk, and only a candidate costs a diff.
- **Closed on the base** releases a claim as `closed`, apart from the prefix's `landed`, and no disposition is read on such an item.
- **Disposition supersession** is not asked separately: a copy whose `status:` differs from the base's has a diff against it that is neither empty nor removal-only, so `_superseded` can only say "not superseded".
- **A disposition's lease** runs from the newest commit on the branch that touched the item's file, through the branch's later non-merge commits, by `_chain`. Only items a commit on the branch touched are compared, which bounds the reads to what the branch edited.
- **`flight()`** reports the head of `order(key)`, else the first live disposition, per item; `editing` from item-file edits the base has not superseded, for items nothing holds; `unattributed` for readable branches with no leading id and no id in the name. It reads no branch-name id: `PL-TZ3R` holds that gap. `last_commit` is the newest non-merge commit, so an Update-branch merge no longer resets a branch's age.
- **Cut holds** share `cuts_in_flight`'s version read (`vcs._cut_versions`), are always `live` (a cut refuses a release whatever its age), and are `mine` where `HEAD` contains the branch's tip, today's rule.
- **`holds` is sorted into claim order across items**, so `holder(resource)` is the first live claim naming the resource and `order(key)` a filter of it.
