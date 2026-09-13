---
id: PL-KH58
title: Nothing reads an item's prose sequencing, so a stated prerequisite with no blocked-by edge is invisible to next, gate and concurrent alike
status: dropped
priority: P3
effort: S
classes: infra
feature: delegation
touches: subprojects/docket/src/docket
added: 2026-09-13
closed: 2026-09-13
reason: measured at n=1 the same day it was filed, and `CLAUDE.md`'s gate on building tooling settles it - "Where the benefit is unclear, the answer is no". Across every open item in the store, exactly one names a still-open prerequisite in prose without carrying the `blocked-by` field that would make it visible, and that one (`PL-9SH6`) now carries the edge. A check would therefore fire on nothing, and the cheapest correct version of it - a regex for "after `PL-XXXX`" in a body - is guessing at the judgment half, since the same words appear in sequencing that has already been satisfied, in history notes about what an item landed behind, and in prose naming a *closed* prerequisite. Recorded rather than left silent so the next session to notice the gap finds the count instead of re-deriving it. The trigger that would overturn this is the count reaching three, which would mean the prose form is being used in preference to the field rather than by oversight.
---

**Problem.** An item's `blocked-by` field is what `bin/docket next`,
`bin/docket gate` and `bin/docket concurrent` read. A prerequisite stated only
in an item's prose - "After `PL-H46J`", "Sequencing: behind `PL-GS5X`" - is read
by nobody, so the item ranks as startable, counts as clearable debt, and passes
every in-flight and concurrency check.

**What it cost, once.** `PL-9SH6` (one accessor name for the
partial-pressure-equivalent fraction across `core/`) says "After `PL-H46J`" in
its Sequencing section and repeats it - "Still after `PL-H46J`" - after a later
re-sequencing. `PL-H46J` is still `ready`. On 2026-09-13 the project owner
approved starting `PL-9SH6` next, and the session ran the full start-an-item
procedure - `git fetch`, `bin/docket show` for the in-flight mark,
`bin/docket flight`, `bin/docket concurrent` - and got four clean answers
before opening the brief and reading the sequencing. Nothing was built out of
order, but only because the brief is read before the work rather than after.

**Measured 2026-09-13, and the number is why this is dropped.** Over every open
item in the store, scanning each body for `after|behind|depends on|once` followed
by a `PL-` id, keeping only items with no `blocked-by` field and only references
whose target is still open:

    1 open item(s) name a still-open prerequisite in prose with no blocked-by edge:
      PL-9SH6  (ready)  waits on PL-H46J

One. And it is now fixed at the source: `PL-9SH6` carries `blocked-by: PL-H46J`
and `status: blocked`, per `PL-KBD0`'s rule.

**Why not build the check anyway.** The regex above is not the check; it is a
draft of one, and the difference is the judgment half `CLAUDE.md` says not to
script. The same words appear in prose that names a prerequisite *already
satisfied* ("Sequencing changed: now behind `PL-GS5X`", which has landed), in
history notes recording what an item landed behind, and in a sentence about a
closed item. A tool reporting those as missing edges would fire every run
without changing a decision, which `CLAUDE.md` names as a defect in the check
rather than coverage.

**Found.** 2026-09-13, starting `PL-9SH6` after the v0.4.17 cut.
