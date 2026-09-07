---
id: PL-2GQW
title: PL-L9JS's not-delegable reason rests on the recursion claim PL-20CQ disproved, so the item may be delegable after all
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: docs/items/PL-L9JS-eight-open-items-carry-a-verify-command-that.md
added: 2026-09-07
verify: bin/docket check && ! grep -qF 'it would recurse' docs/items/PL-L9JS-eight-open-items-carry-a-verify-command-that.md
---

**Problem.** PL-L9JS's not-delegable reason rests on the recursion claim PL-20CQ disproved, so the item may be delegable after all

**Why it matters.** `PL-L9JS` records `not-delegable: the command that would
prove this is `bin/docket check` itself, which cannot be a `verify:` command
because `docket check` runs every open item's `verify:` command - it would
recurse.` `PL-20CQ` checked that and it is false: `docket check` replays the
commands only under `--verify`, which nothing in the store passes, and a nested
run is stopped by `LANDED_GUARD` anyway. Ten open items already record
`bin/docket check && grep -q ...` without incident.

So the field is withholding an item on a reason that does not hold, and
`not-delegable` is read by `docket next` when it decides which model the work
wants. The second half of the recorded reason - that what is left is eight
judgments no command makes - may well still stand on its own; that is the part
to re-examine.

**Done when.** `PL-L9JS` either carries a `verify:` command, or carries a
`not-delegable:` reason that is true of the tree as it now stands.
