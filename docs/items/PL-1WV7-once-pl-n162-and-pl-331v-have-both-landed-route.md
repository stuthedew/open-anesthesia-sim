---
id: PL-1WV7
title: Once PL-N162 and PL-331V have both landed, route cli._cuts and cmd_release's release-train read through PL-N162's _holdings(args), so the digest walks the refs once rather than twice
priority: P3
effort: S
status: ready
classes: perf
feature: claim-record
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-25 triage pass
added: 2026-09-24
payoff: A session-start digest that offers a release walks the branch refs once instead of twice, and a release reads who holds the train from the one cached answer every other command shares
verify: ! grep -qF 'holdings(root, now=_now(args), items_dir=tracked, runner=' subprojects/docket/src/docket/cli.py
---

**Problem.** Once PL-N162 and PL-331V have both landed, route cli._cuts and cmd_release's release-train read through PL-N162's _holdings(args), so the digest walks the refs once rather than twice

**Both have landed.** `PL-331V` closed 2026-09-24 (`#995`), and `PL-N162`
closed 2026-09-24 (`#1002`).

Reproduced 2026-09-25 against 46954a81: `grep -nF 'holdings(root,
now=_now(args), items_dir=tracked, runner=' subprojects/docket/src/docket/cli.py`
finds both direct reads, in `_cuts` and in `cmd_release`. The digest also
takes `read=_holdings(args)`, and `_flight` builds on `_holdings(args)`. So a
digest that offers a release builds `Holdings` twice. `cmd_release` builds it
once, but not from the cached read the other commands share.

**Why it matters.** It is a small cost, not a wrong answer. Both reads use the
same `now` and the same memoizing `GitRunner`, so they agree. `_cuts`'s
docstring measures its walk of the unlanded refs at 103 ms. How much of that
the second walk still costs, with git's answers memoized, is unmeasured. Past
the time, one cached read per command is the shape `PL-N162` set for every
other reader of who holds an item.

**One trap for the worker.** The two call sites decline differently from
`_holdings(args)` when the store is not below the repository root.
`cmd_release` builds `Holdings(declined="the store is not below the repository
root")`, which its guards refuse on, and `_cuts` returns the cuts without the
train. `_holdings(args)` passes `inv.tracked` straight to `holdings()`
whatever it holds. Keep both declines when routing through it.

**Not covered by `PL-MB2W`'s close-out.** That item's remaining work is
`vcs.py`'s module docstring, a claims section and git floor in the docket
README, re-scoping `PL-J16N`, and closing the answered members. Its `touches`
do not reach `cli.py`, and its brief names neither `_cuts` nor `_holdings`.

**Done when.** Neither `_cuts` nor `cmd_release` calls `holdings()` directly.
Both read `_holdings(args)`, and both keep their decline for a store outside
the repository root.

**Generator check.** Bookkeeping. `PL-331V`'s session filed this as the
follow-up for when two build items of the claim-record feature had both
landed. Both reads give the same answer, so no reader misreads who holds an
item, and `PL-MB2W`'s `misread:` is not in play.
