---
id: PL-7NH2
title: PL-6YWK is the third verify-replay-cost item but carries feature: queue-hygiene, so bin/docket feature verify-replay-cost reports 0/2 for a problem with three open parts and cannot say when it is finished
priority: P3
effort: S
status: done
classes: infra
feature: verify-replay-cost
milestone: v0.4.28
touches: docs/items
added: 2026-09-19
closed: 2026-09-19
verify: grep -q '^feature: verify-replay-cost' docs/items/PL-6YWK-pl-4l6z-s-verify-runs-the-whole-reference-suite.md
---

**Problem.** PL-6YWK is the third verify-replay-cost item but carries feature: queue-hygiene, so bin/docket feature verify-replay-cost reports 0/2 for a problem with three open parts and cannot say when it is finished

**Where it comes from.** `PL-8T83` and `PL-G6J5` were filed together under
`feature: verify-replay-cost`. `PL-6YWK` is the same problem seen through a
different consumer — a `verify:` command that runs a whole suite, sets the
replay's floor and makes its own exit unreadable — but it was filed from the
digest's red-`main` line rather than from the replay's cost, and landed in
`queue-hygiene`.

**Why it matters.** `feature:` is the store's only grouping, and `docket
feature <name>`, `docket status` and `recommend`'s finish-a-feature preference
all read it. So `bin/docket feature verify-replay-cost` answers `0/2 done` for
a problem with three open parts, and cannot ever report the problem finished:
closing both of its members leaves `PL-6YWK` open and unnamed by the group.
`CLAUDE.md`'s capture rule and `PL-N638` both turn on the owner tracking
problems rather than ids — "when do we stop paying for slow verify commands",
not "when do PL-8T83 and PL-G6J5 land" — and that question has no command
behind it while the third member sits elsewhere.

`queue-hygiene` is also a catch-all carrying 29 items, which `PL-S0MB` records
as a name that can never report completion. Moving `PL-6YWK` out of it is the
same repair in the other direction.

**Done when.** `PL-6YWK` carries `feature: verify-replay-cost` and `bin/docket
feature verify-replay-cost` names all three items.
