---
id: PL-N162
title: Rewire branches_in_flight, precedence and settled_branches onto claims.holdings
priority: P2
effort: M
status: blocked
classes: defect
feature: claim-record
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py
blocked-by: PL-NST2
deferred-from: v0.6.0 - filed after the freeze by PL-MB2W's design round (2026-09-24), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-24
payoff: part of the claim record that ends PL-MB2W's generator: one recorded fact decides who holds an item
---

**Problem.** Rewire branches_in_flight, precedence and settled_branches onto claims.holdings

**Part of `PL-MB2W`'s design** (who holds an item is recorded as a claim; design round of 2026-09-24, in `PL-MB2W` under "Design round, 2026-09-24"). Read that section's spec before starting: this brief names only this item's slice of it.

`branches_in_flight` becomes `holdings().flight()`, keeping `FlightReport`'s shape so its callers stay unchanged; `precedence` becomes `Holdings.order`, and its 19 tests are rewritten against it; `settled_branches` reads released holds. `flight` gains kind and state columns, an `unclaimed:` row per work branch that holds no claim, and a `legacy refs: N` line, and lists lapsed claims only for open items.

**Why it matters.** `PL-MB2W` is a live generator: twenty items were each a new shape of work that some reader misread, because who holds an item is inferred from commit subjects, touched paths and ref age. This item is one slice of replacing that inference with a recorded claim, and the generator stops producing members only once the slices through `PL-DDYD` land.

**Done when.**

- `branches_in_flight`, `precedence` and `settled_branches` answer from `claims.holdings`, and the digest, `next`, `flight` and `show` print the same fields as before plus kind and state.

**Build order.** After `PL-NST2`.

**`Holdings.flight()` reads no branch-name id** (`PL-TZ3R`, untriaged): `branches_in_flight` proves an id from a name like `claude/pl-k7qx-slug` even for a ref whose history went unread, so the rewire either carries that reading into the reader or records dropping it.
