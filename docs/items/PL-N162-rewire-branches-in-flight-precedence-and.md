---
id: PL-N162
title: Rewire branches_in_flight, precedence and settled_branches onto claims.holdings
priority: P2
effort: M
status: ready
classes: defect
feature: claim-record
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claims.py, subprojects/docket/tests/test_cli.py, .claude/skills/docket/modes/start.md
blocked-by: PL-NST2
deferred-from: v0.6.0 - filed after the freeze by PL-MB2W's design round (2026-09-24), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-24
payoff: part of the claim record that ends PL-MB2W's generator: one recorded fact decides who holds an item
verify: grep -qF 'legacy refs:' subprojects/docket/src/docket/render.py && grep -qF 'unclaimed:' subprojects/docket/src/docket/render.py && ! grep -qF 'branches_in_flight(inv.root' subprojects/docket/src/docket/cli.py && ! grep -qF 'precedence(root, item.identifier' subprojects/docket/src/docket/cli.py
---

**Problem.** Rewire branches_in_flight, precedence and settled_branches onto claims.holdings

**Part of `PL-MB2W`'s design** (who holds an item is recorded as a claim; design round of 2026-09-24, in `PL-MB2W` under "Design round, 2026-09-24"). Read that section's spec before starting: this brief names only this item's slice of it.

`branches_in_flight` becomes `holdings().flight()`, keeping `FlightReport`'s shape so its callers stay unchanged; `precedence` becomes `Holdings.order`, and its 19 tests are rewritten against it; `settled_branches` reads released holds. `flight` gains kind and state columns, an `unclaimed:` row per work branch that holds no claim, and a `legacy refs: N` line, and lists lapsed claims only for open items.

**Why it matters.** `PL-MB2W` is a live generator: twenty items were each a new shape of work that some reader misread, because who holds an item is inferred from commit subjects, touched paths and ref age. This item is one slice of replacing that inference with a recorded claim, and the generator stops producing members only once the slices through `PL-DDYD` land.

**Done when.**

- `branches_in_flight`, `precedence` and `settled_branches` answer from `claims.holdings`, and the digest, `next`, `flight` and `show` print the same fields as before plus kind and state.
- A ref named for its item holds that item where no claim or disposition does, including a ref whose history went unread (`PL-TZ3R`, folded in below).

**Build order.** After `PL-NST2`.

**The fault, reproduced 2026-09-24 on `b1d1b665`.** `cli.py`'s `_flight` still calls `vcs.branches_in_flight`, `cmd_show` still renders `vcs.precedence`, and `cmd_flight`'s settled row still calls `settled_branches` over that report. `claims.holdings` has no caller outside `claiming.py`, and `render.py` prints neither `legacy refs:` nor `unclaimed:`.

**`Holdings.flight()` reads no branch-name id, and this item carries it** (decided 2026-09-24 at triage, folding `PL-TZ3R` in). `branches_in_flight` proves an id from a name like `claude/pl-k7qx-slug`, even for a ref whose history went unread. The spec lists that reading under "Other holds", and this rewire is the change that would lose it. So `claims.holdings` gains it as a fourth kind of hold, beside dispositions and cuts. It never orders against a claim, never holds arming, runs on the branch's lease, and reaches `flight()` only where no claim or disposition holds the item. A ref whose history went unread still proves its id this way, as it does today, and stays in `unreadable` as well. Building it was chosen over dropping it because dropping it departs from the ratified spec, and it is cheap. For now it is also rare: 0 of the 8 non-default remote heads carried a name id on 2026-09-24.

**Leads for the rewire, read from the code on 2026-09-24 and not yet tested:**

- `flight()` drops released holds. A branch that closes its item in its own copy releases its claim (`BY_STATUS`), but it keeps the item in flight through the disposition that the same status move creates. So `settled_branches` probably wants the `Holdings` rather than the `FlightReport`: a ref is settled where it holds no live claim and every live hold it has is a disposition to a status in `CLOSED_STATUSES`. That uses `CLOSED_STATUSES`, not `RELEASING_STATUSES`, because a blocked item is not finished work.
- `test_cli.py` builds real git repositories (none of it fakes `for-each-ref`). No commit tree there holds `CUTOVER_MARKER`, so `holdings` reads every such commit by the legacy rule: subject-led ids on a commit that reaches outside the queue still claim, and the three promotions (`PL-7790`, `PL-VYSP`, `PL-8FJK`) do not. Expect the promotion tests to move, and nothing else by that route.
- `holdings` refuses a naive `now`, so `_flight` passes `_now(args)`.

**Progress, 2026-09-24: slice 1 of 5 landed; the rest is below, in build order.** The claiming session (`d37268d8`) stopped for length after the reading, not for the work. Each slice below is meant to be pushed on its own, green, under this id.

1. **Done: the branch-name hold** (`PL-TZ3R`). `claims.holdings` returns it as `Holdings.named`, kind `NAMED`, one per `(item, branch)`. Two choices made inside the approach:
   - *Lease.* It is live while the branch's newest non-merge commit is within `LEASE_TERM`. It is not a chain from the first commit, because nothing can revive a name the way a new claim revives a claim. A ref whose commits went unread is live, dated `now`, with an empty `commit`, and it stays in `unreadable`.
   - *Release.* Only the base closing the item releases it (`BY_CLOSED`). A branch closing the item in its own copy keeps it in flight, which is where `settled_branches` finds it.

   `flight()` reads it only where no claim or disposition holds the item. `ids` and `editing`'s held set include it. Tested in `test_claims.py`, including the unread-ref case through the shallow-clone topology.
2. **`cli._flight` onto `holdings`.** Cache a `Holdings` on the `Invocation`, built as `holdings(inv.root, now=_now(args), items_dir=inv.tracked, runner=inv.git)`, and return its `.flight()`. `_now` is aware on every path (cli.py `_now`), so lead 3 above holds. Expect `test_cli.py`'s promotion tests to move, per lead 2. A promotion that moves a status (`PL-8FJK`'s close, `PL-7790`'s tag item closing) may still hold as a disposition: the item exists at the fork and on the base, and its status differs from both. `PL-VYSP`'s design round moves no status, so it holds nothing unless claimed.
3. **`show` onto `Holdings.order`.** Replace `precedence` and `format_precedence` in `cmd_show` with the item's live claims (`order`), plus its disposition or name hold where nothing claims it. Print kind and state, and a lapsed claim only where `on_base` (`lapsed_open`). The 19 precedence tests in `test_vcs.py` (from `# --- precedence` onward) are rewritten against `Holdings.order` in `test_claims.py`'s real-git style. Where `test_claims.py` already pins a behaviour (order on `(%aI, hash)`, a tracking ref as one holder, takeover), the old test is deleted rather than ported. `precedence` and `Carrier` are then dead, and `PL-FX5Q` deletes them.
4. **`settled_branches` onto the `Holdings`.** Lead 1 above is the rule. Keep `SettledReport`'s shape and the `opened` callable.
5. **`flight`'s output.** Add kind and state columns, a `legacy refs: N` line counting refs whose live hold is `legacy`, lapsed claims on open items (`lapsed_open`), and an `unclaimed:` row per `claude/*` branch that has a non-legacy commit reaching outside `items_dir` and no live claim. That last is the spec's third "Forgetful session" catch, and it is the same predicate `PL-J9S0`'s `branch_id_check` is building, so reuse theirs rather than write a second. Then drop the "until `PL-N162`" caveats in `.claude/skills/docket/modes/start.md`.
