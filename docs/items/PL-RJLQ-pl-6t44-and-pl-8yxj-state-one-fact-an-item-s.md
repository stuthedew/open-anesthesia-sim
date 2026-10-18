---
id: PL-RJLQ
title: PL-6T44 and PL-8YXJ state one fact - an item's current queue state: its status, what blocks it, and what it must land after - and no head names it at family altitude; decide whether it is a generator, and if so record its head with a verdict
priority: P1
effort: M
status: ready
classes: housekeeping
feature: generator-identification
touches: docs/items
added: 2026-09-24
payoff: one family head says whether reading an item's queue state wrongly is still producing work, so the next reader who misreads it is ranked rather than filed
verify: grep -q '^generator: spent' docs/items/PL-RJLQ-*.md
root-cause-of: PL-6T44, PL-8YXJ, PL-0H5D, PL-59QW, PL-9F8B, PL-JNWS, PL-2349
generator: live - five instances arrived after its two narrower heads closed, from 2026-09-21 to 2026-10-11, each from a copy or reader the last fix left out; the writer and brief copies are now refused, but cli.cmd_show and render.format_status still decide whether an item can start beside plan._unseated_by, and format_status counts an untriaged item, so a reader can still hand it a member
misread: An item's current queue state: its status, what blocks it, and what it must land after
reenters: PL-6T44, PL-8YXJ
---

**Problem.** PL-6T44 and PL-8YXJ state one fact - an item's current queue state: its status, what blocks it, and what it must land after - and no head names it at family altitude; decide whether it is a generator, and if so record its head with a verdict

**What triage found, 2026-09-24.** Triage mode's head comparison already
answers the "whether": two heads stating one fact, with no head naming it at
family altitude, is a generator. What is left is its verdict and its members.

- `PL-6T44` closed 2026-09-20. Its members are `PL-JFQ3`, `PL-8G48` and
  `PL-CHQY`, and it carries no `generator:` line at all.
- `PL-8YXJ` closed 2026-09-23. Its members are `PL-X4RX`, `PL-7G5M` and
  `PL-9K7K`, and its verdict is `spent`.

Leads for instances filed after a close, each needing its brief read:

- After `PL-6T44`: `PL-162Y` (open, filed in that head's own closing commit),
  `PL-0H5D` and `PL-LDHD`.
- After `PL-8YXJ`: `PL-59QW` and `PL-58JD`, both under `PL-WD5Z`, one level
  narrower.
- Found this pass: `PL-4RK2`'s third shape, where `docket show` calls a blocked
  head ranked, and `render.format_queue_edit`, which calls a closed item
  startable (filed today).

Three post-close instances of one head count as a generator whose fix did not
hold, so on these leads the verdict is likelier `live` than `spent`. That is a
lead for the session, not the answer.

**Done when.** For a `live` verdict, `PL-RJLQ` carries `root-cause-of:` naming
the members, `misread:` in the two heads' shared words, and `generator: live`
with the why. For a `spent` verdict, `PL-6T44` carries the `generator: spent`
line it lacks, and this item closes saying why.

**Decided 2026-10-18.** This is a live generator, so this item stays open as
its head. `PL-6T44` and `PL-8YXJ` state one fact, an item's current queue
state, and no other head states it at family altitude. `PL-WD5Z`'s fact is a
gate entry's disposition, which is different. Five items misread the fact
after one of the two heads closed: `PL-0H5D`, `PL-59QW`, `PL-9F8B`, `PL-JNWS`
and `PL-2349`, filed from 2026-09-21 to 2026-10-11. Three of them followed
`PL-6T44`, which meets triage's bar for a fix that did not hold, and they now
carry `reenters: PL-6T44`. Each fix covered one copy of the state, and the
next instance came from a copy it left out. A check now refuses a stale
`blocked` status and an answered `needs-decision`, and it reports a brief that
narrates an old status. The readers of whether an item can start still have no
single owner. `cli.cmd_show` restates `plan._unseated_by`, and
`render.format_status` names a feature's next item from any open member that
is not blocked, untriaged ones included. It names none today. `PL-162Y`,
`PL-LDHD`, `PL-58JD` and `PL-4RK2` are not members: they are deferred scope,
bookkeeping, or another head's fact. `PL-6T44` now carries a `generator:
spent` line that points here.

**Next: the fix.** Export one predicate from `plan` that says whether an item
can start, and read it in `cli.cmd_show` and `render.format_status`. That
absorbs `PL-4DK2`'s `cmd_show` line, which the one-answer chain holds, so the
fix lands after `PL-4DK2` or takes it with that chain's agreement. Then this
item records `generator: spent - <why>`, which is what its `verify:` now
tests. The old `verify:` passed once this decision was written, so it proved
nothing about the fix.
