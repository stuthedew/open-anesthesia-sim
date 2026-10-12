---
id: PL-8QMD
title: A gate entry's disposition is still read from ROADMAP.md prose wherever PL-WD5Z's deferred-from: does not reach - a frozen entry and a non-debt deferral - so four readers filed since it closed on 2026-09-23 lose or misplace one: an id-less holding condition (PL-18BD), an off-list blocker read as a deferral (PL-D388), Gate 3's freeze dropping Gate 2's non-debt deferrals (PL-JV5Q), a non-debt entry's lane (PL-QWF8)
priority: P1
effort: M
status: ready
classes: defect
feature: gate-prerequisites
touches: docs/items, ROADMAP.md, subprojects/docket/src/docket/roadmap.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; recorded as a generator head by PL-74T0, 2026-10-11
added: 2026-10-11
payoff: every gate entry's disposition, frozen or not, debt or not, is read from one record, so a freeze or a report stops losing a deferral the prose held
verify: grep -q 'def test_a_frozen_entry_deferred_from_its_gate_is_deferred_not_clearable' subprojects/docket/tests/test_roadmap.py && grep -q 'def test_an_open_frozen_entry_waiting_outside_with_no_disposition_is_an_error' subprojects/docket/tests/test_checks.py
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

[superseded 2026-10-11: answered below - one record, `deferred-from:` on the item] **The decision this head carries.** Whether to reopen the ratified choice of a
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

## Design round, 2026-10-11

**What the answer reopens is `PL-18BD`'s, not `PL-0H5D`'s.** `PL-0H5D`
(2026-09-21, ratified, over a `blocked-on:` tree predicate) gave a holding
condition with no id an item to block on, so that `blocked-by` tells the
promote advisory and `next` the truth. That stands whatever this round
decides: `PL-TBMK`, `PL-4TWW`, `PL-2FZ9` and `PL-YRLM` stay the real blockers
of the entries naming them. `PL-18BD` (2026-09-27, ratified, over reading the
deferral group, a `deferred-to:` field and leaving `wave` alone) then made the
same holding item the way `wave` reads a *deferral*. Only that second use is in
question, so nothing filed under `PL-0H5D` is undone.

**`PL-18BD` named the evidence that would justify the general fix, and it has
arrived.** Its recommendation held the general fix "worth its M change only if
deferrals whose condition has no id keep arriving". Since then the `blocked-by`
reading has misfired in both directions on Gate 2's seven frozen deferrals:

- counted clearable though deferred: `PL-18BD`'s own four (2026-09-27), and
  `PL-5B1N` as `PL-YBFB` first briefed it, caught only by a message
  (2026-10-03, `PL-D388`);
- counted deferred though nobody deferred them: `PL-VV6N` and `PL-1RTM`, each
  behind an off-list blocker (2026-10-03, `PL-D388`).

And `bin/docket wave` prints the six still open inside "blocked outside the
gate", beside eleven entries waiting on v0.6.0's own Required scope
(`PL-W9BK`), so no reader can tell a deferral from a dependency without the
prose (`bin/docket wave --no-fetch` at `d9340516`, read 2026-10-11).

**Decision needed, second: where the one record lives**, if the first answer
is one record. The readers it must serve are `roadmap.gate_status` (`wave` and
the digest), `bin/docket check`, `bin/docket gate` with the freeze in
`.claude/skills/docket/modes/release.md`, and `tools/doc_check.py`'s group
checks. Three homes:

1. **`deferred-from:` on the item, extended to frozen entries.** The field
   already says what a frozen deferral says - this gate does not hold the item,
   a later freeze does - with the version naming the gate the item is excused
   from, as `PL-WD5Z` decided. 428 items carry it, and `checks`, `render`,
   `model` and `cli` read it. The build lifts `check`'s refusal of an item the
   current gate both places and defers; `gate_status` reads the field as a
   third carve-out beside `blocked_outside` and `self_cleared` rather than
   inferring a deferral from `blocked-by`; an open frozen entry blocked outside
   with neither a deferral nor Required scope is undecided, and `check`
   refuses it (`PL-D388`'s first direction, in docket rather than
   `doc_check`); and the freeze carries every open entry the previous list
   deferred, debt or not (`PL-JV5Q`). Six open entries are written. v0.6.0's
   three deferral groups become one pointer to `wave`, as `PL-WD5Z` did for the
   post-freeze deferrals, which leaves `PL-D388`'s second direction nothing to
   check. It adds no field.
2. **The deferral group headings, parsed by `docket.roadmap`** (`PL-18BD`'s
   option 2). It keeps the gate readable where the owner reads it, and
   `doc_check`'s `GATE_GROUP_RE` already parses those headings. But it leaves
   one disposition with two homes - a post-freeze deferral on the item, a
   frozen one in a heading - which is the second store `PL-WD5Z` removed
   (ratified, over structured lines in `ROADMAP.md`); and a deferral written
   there edits `ROADMAP.md`, so its commit claims the ids it leads with, where
   an item-only write is annotation (`vcs._annotates_only`, `PL-WD5Z`'s
   finding).
3. **A new `deferred-to:` field naming the target gate** (`PL-18BD`'s
   option 3). A second field for one disposition, naming the target `PL-WD5Z`
   decided against: "A target is what 'Declined to Gate 2' got wrong".

**Recommendation: home 1.** It is the only home that puts every gate deferral,
frozen or not, in one field every reader already parses. It answers
`PL-18BD`'s objection to a field - "a second copy of a decision beat 3 puts in
the section, and two copies drift" - by moving beat 3's record onto the item
rather than copying it, as `PL-WD5Z` moved § "Recording it". Home 2 is the
fallback if the frozen gate must stay readable in `ROADMAP.md` without running
`wave`, at the price of two homes held together by a check. What would make
home 1 wrong: the owner reading a gate's deferrals in `ROADMAP.md` rather than
in `wave`.

**The non-debt half needs no record of its own.** `PL-5B1N` and `PL-B396` are
frozen entries because they were debt when the list froze, and a frozen entry
stays one whatever its classes become. What loses them is a reader that walks
open debt instead of the list: the freeze (`PL-JV5Q`) and the lane report
(`PL-QWF8`). Home 1's build points both at the list. Whether `ROADMAP.md`'s lane
groups then keep restating `Item.lane` is `PL-Z64T`'s question, which this
answer unblocks.

**Cost of keeping the prose**, the first answer's alternative: `PL-D388`'s
two-direction check in `doc_check` (M), `PL-JV5Q`'s freeze sentence (S) and
`PL-QWF8`'s lane print (S), with the head left `live` for the next reader of a
heading or a `blocked-by` chain to file.

**Answered 2026-10-11: one record, and it is `deferred-from:` on the item,
extended to frozen entries** (project owner, 2026-10-11, ratified, over keeping
the prose with a check per reader, over parsing v0.6.0's deferral group
headings in `ROADMAP.md`, and over a new `deferred-to:` field). `PL-18BD`'s
reading of a deferral through a holding item is retired; `PL-0H5D`'s holding
items stay, as blockers. Status moved to `ready` with this answer, and the
Done-when below is rewritten to it. `PL-D388`, `PL-JV5Q` and `PL-QWF8` are set
`blocked` on this item in the same commit, because its build does what each
asks in the decided form and its closing commit leads with them; `PL-Z64T`
already waits here.

**Done when.** A frozen entry's deferral is its `deferred-from:` field, and
every reader of a gate entry's disposition reads it. `bin/docket check` accepts
the field on an entry the current gate places, and refuses an open frozen entry
that waits outside the list with neither the field nor a place in the
milestone's Required scope. `roadmap.gate_status` counts an open entry carrying
it as deferred, apart from `blocked_outside`, and `bin/docket wave` prints it
so. The freeze - `bin/docket gate` and the freeze mode in
`.claude/skills/docket/modes/release.md` - carries every open entry the
previous gate's list deferred, debt or not, and a report reads every frozen
entry's lane from a docket command. v0.6.0's six open deferrals carry the
field, and its three deferral groups are one pointer to `bin/docket wave`.
The closing commit leads with `PL-D388`, `PL-JV5Q` and `PL-QWF8`, which close
through the change, and with this item; `generator:` says spent; `make check`
is green.

**Generator check.** This is the head, recorded 2026-10-11 by `PL-74T0`: three
or more post-close instances of `PL-WD5Z`'s fact, which triage reads as a
generator whose fix did not hold. Its `misread:` is the family wording, and
`PL-J6HP`'s and `PL-WD5Z`'s were rewritten to it in the same commit so the
three sort together.
