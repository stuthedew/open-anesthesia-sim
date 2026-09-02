---
id: PL-D1ST
title: v0.4.0's Required scope describes items whose ids it never prints, so PL-SN2C and the playback multiplier are placed nowhere
priority: P2
effort: S
status: done
classes: docs
feature: planning-cadence
touches: ROADMAP.md
added: 2026-09-01
closed: 2026-09-02
pr: 231
verify: grep -qF 'PL-SN2C' ROADMAP.md
---

**Problem.** After `PL-HDY6`, a milestone places an id when its `Required
scope` prints that id. v0.4.0's `Required scope` is eleven bullets and seven of
them carry an id; the rest describe work that has a queue item without naming
it. `PL-SN2C` (add the playback multiplier as steps per tick, with the rate
always visible) is the clearest case: the bullet "**A playback multiplier**,
implemented as steps per tick, with the current rate visible beside the clock"
is that item, word for word, and `PL-SN2C` appears nowhere in `ROADMAP.md`
(measured 2026-09-01, zero occurrences).

So the item is `unplaced` - `docket next` neither includes it in the current
step nor marks it `scoped to v0.4.0`. Three ids in the same subsection were in
the same state and were fixed with `PL-HDY6` because that section's own prose
claimed they appeared there (`PL-VM40`, `PL-F52R`, `PL-ZRSP`); nothing claims
it for the rest, so they were left rather than guessed at.

**Why it matters.** This is roadmap content rather than machinery: the reader
is answering correctly about a document that does not say what its author
means. The cost is that a v0.4.0 item looks unplanned while the milestone is
being worked, which is the marking `PL-1TPM` and `PL-0RS6` exist to produce.

**Where.** `ROADMAP.md`'s "Required scope" under v0.4.0. The work is deciding,
per bullet, which queue item it is - a judgment, not a match - and printing the
id in the convention the sibling bullets already use, `(queue item PL-SN2C)`.
Check v0.3.0 too, which records no `Required scope` at all.

**Done when.** Every v0.4.0 `Required scope` bullet that corresponds to an open
queue item prints that item's id, and `bin/docket next` marks each of them
`scoped to v0.4.0`.

**Triaged 2026-09-01.** P2, `docs`, `planning-cadence` with the rest of the
roadmap-reader cluster. `docs` rather than `defect`: the reader is behaving
correctly and the document is what is incomplete, so this is not gate debt and
is not admitted to v0.2.8's frozen list.

P2 rather than P3 - above `PL-6P9Y` (a milestone's out-of-scope list read as
silence), triaged in the same pass - on two counts. It affects four bullets
rather than one id, and the fix is pure content with no design question in it,
where `PL-6P9Y` needs a fourth `Scope` answer designed before anything can be
written. `ROADMAP.md` is also the authoritative version and milestone map, so a
bullet describing an item it never names is a statement a reader can act on
wrongly.

Confirmed 2026-09-01, rather than carried from the brief: `PL-SN2C` appears
zero times in `ROADMAP.md`. The `verify:` command was run before being written
down and exits 1.

**Closed 2026-09-02.** All four bullets now print their id: `PL-SN2C` (the
playback multiplier), `PL-CC23` (the vertical scale that fits the run),
`PL-DR1Z` (the recorded control-input timeline) and `PL-RCTQ` (the
documentation sweep). Two bullets added in the same change print theirs too —
`PL-WB0X` with `PL-B9PY` for the interface-layer extractions, and `PL-W3DD` for
the substance-keyed history record — so every one of v0.4.0's thirteen
`Required scope` bullets is now placed, checked by parsing the section rather
than by eye.

Taken alongside the milestone-scope change in the same commit rather than on
its own, because that change was already rewriting this section and because
v0.4.0 had just become the step the project is on: four of its thirteen items
reading as unplanned is a cost every session doing this milestone would have
paid.

v0.3.0 records no `Required scope`, which the brief flagged to check. That is
correct rather than a second instance: its whole content is Gate 0's frozen
list, recorded under v0.4.0, and the timeline row says so.
