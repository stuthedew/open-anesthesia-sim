---
id: PL-8QMD
title: A gate entry's disposition is still read from ROADMAP.md prose wherever PL-WD5Z's deferred-from: does not reach - a frozen entry and a non-debt deferral - so four readers filed since it closed on 2026-09-23 lose or misplace one: an id-less holding condition (PL-18BD), an off-list blocker read as a deferral (PL-D388), Gate 3's freeze dropping Gate 2's non-debt deferrals (PL-JV5Q), a non-debt entry's lane (PL-QWF8)
priority: P1
effort: M
status: needs-decision
classes: defect
feature: gate-prerequisites
touches: docs/items, ROADMAP.md, subprojects/docket/src/docket/roadmap.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; recorded as a generator head by PL-74T0, 2026-10-11
added: 2026-10-11
payoff: every gate entry's disposition, frozen or not, debt or not, is read from one record, so a freeze or a report stops losing a deferral the prose held
root-cause-of: PL-18BD, PL-D388, PL-JV5Q, PL-QWF8
generator: live - four members since PL-WD5Z closed on 2026-09-23, three filed on 2026-10-03 when a gate was last read whole, and every later freeze or deferral reads the same prose, as PL-JV5Q shows for Gate 3
misread: A gate entry's disposition: whether a milestone's gate holds, clears, defers or still owes it
---

**Problem.** A gate entry's disposition is still read from ROADMAP.md prose wherever PL-WD5Z's deferred-from: does not reach - a frozen entry and a non-debt deferral - so four readers filed since it closed on 2026-09-23 lose or misplace one: an id-less holding condition (PL-18BD), an off-list blocker read as a deferral (PL-D388), Gate 3's freeze dropping Gate 2's non-debt deferrals (PL-JV5Q), a non-debt entry's lane (PL-QWF8)

`PL-WD5Z` closed `spent` on 2026-09-23 having moved a debt item's gate
disposition onto the item as `deferred-from:`, and `PL-J6HP`'s verdict beside
it records that "the record itself stayed prose". Two kinds of entry are outside
that field. An entry a frozen gate places: `bin/docket check` refuses
`deferred-from:` on it, so its deferral is its group heading, which `wave` reads
through `blocked-by` (`PL-0H5D` and `PL-18BD`, both ratified, over a field). And
a non-debt entry, which `bin/docket gate`, reading open debt, never sees. Four
readers have misread one of the two since:

- `PL-18BD` (2026-09-27, closed) - `wave` could not read a deferral whose
  holding condition has no id.
- `PL-D388` (open) - an off-list blocker reads as a deferral, so Gate 2 can read
  clear with an entry undecided.
- `PL-JV5Q` (open) - Gate 3's freeze takes its list from `bin/docket gate`, so
  Gate 2's non-debt deferrals `PL-5B1N` and `PL-B396` will not be on it.
- `PL-QWF8` (open) - a report on a frozen gate cannot read a non-debt entry's
  lane from docket.

**The decision this head carries.** Whether to reopen the ratified choice of a
group heading over a field (`PL-0H5D`, `PL-18BD`) for frozen and non-debt
entries. Ratified, so the evidence above is enough to put it back to the project
owner. The candidate is one record of each gate entry's disposition, frozen or
not, debt or not, read by `gate`, `wave`, the freeze and every report - rather
than a check per reader, which is the shape that left this remainder. The
design round puts it (`.claude/skills/docket/modes/design.md`).

**Not counted.** `PL-W9BK` is a re-entry of `PL-FD5Q`, a reader defect that
`PL-WD5Z`'s own decision kept off its members. `PL-Z64T` (`ROADMAP.md`'s lane
groups restating `Item.lane`) is `PL-G424`'s fact, the link between a document
sentence and the tree fact it restates; it waits on this head because the
record decided here decides where an entry's lane is written, if anywhere.

**Why it matters.** The gate is what decides when a release is due, and every
member here makes it read clear, or drop an entry, on prose a reader
reconstructed: a deferral lost at a freeze is debt that silently leaves the
list the release is held to.

**Decision needed.** Whether a frozen or non-debt gate entry's disposition gets
one record every reader consults, reopening the ratified group-heading choice of
`PL-0H5D` and `PL-18BD`, or stays prose with a check per reader.

**Recommendation: one record.** Four readers misread this prose in two weeks,
and a check per reader is the shape that left the remainder `PL-WD5Z` could not
reach, so a fifth reader would need a fifth check. The cost is reversing a
ratified choice and finding a home every reader already loads - an item field,
or a gate list with a grammar `docket.roadmap` parses - which the design round
weighs against how many readers each would serve.

**Done when.** The decision is taken and recorded, every reader of a gate
entry's disposition reads the one record, the open members close, and
`generator:` says spent.

**Generator check.** This is the head, recorded 2026-10-11 by `PL-74T0`: three
or more post-close instances of `PL-WD5Z`'s fact, which triage reads as a
generator whose fix did not hold. Its `misread:` is the family wording, and
`PL-J6HP`'s and `PL-WD5Z`'s were rewritten to it in the same commit so the
three sort together.
