---
id: PL-RJLQ
title: PL-6T44 and PL-8YXJ state one fact - an item's current queue state: its status, what blocks it, and what it must land after - and no head names it at family altitude; decide whether it is a generator, and if so record its head with a verdict
priority: P2
effort: M
status: ready
classes: housekeeping
feature: generator-identification
touches: docs/items
added: 2026-09-24
payoff: one family head says whether reading an item's queue state wrongly is still producing work, so the next reader who misreads it is ranked rather than filed
verify: grep -q '^generator: ' docs/items/PL-6T44-*.md docs/items/PL-RJLQ-*.md
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
