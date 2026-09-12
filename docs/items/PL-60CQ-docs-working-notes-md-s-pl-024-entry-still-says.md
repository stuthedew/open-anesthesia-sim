---
id: PL-60CQ
title: docs/WORKING_NOTES.md's PL-024 entry still says the venous pool is 1.0 L and cited twice in reference_adult.json; both stopped being true when PL-8ZJQ adopted Davis and Mapleson's 1.222 L
priority: P2
effort: S
status: ready
classes: docs
feature: model-spec-accuracy
touches: docs/WORKING_NOTES.md
added: 2026-09-08
verify: python3 tools/doc_check.py check && ! grep -qF '1.0 L is the Gas Man reference value' docs/WORKING_NOTES.md
---

**Problem.** docs/WORKING_NOTES.md's PL-024 entry still says the venous pool is 1.0 L and cited twice in reference_adult.json; both stopped being true when PL-8ZJQ adopted Davis and Mapleson's 1.222 L (found while closing `PL-7HDS`, 2026-09-08).

The entry, under the heading naming `PL-024` (the venous pool's grip on the
first minute), reads in the present tense: "1.0 L is the Gas Man reference
value and is cited twice in `reference_adult.json`, so the number is the one
the reference implementation uses and its meaning is unstated", and closes
"Its mixing time constant is 60 - V/Q = 12 s at the reference 1.0 L".

Three things in that are now false:

1. **The stored value is 1.222 L**, not 1.0 L, since `PL-8ZJQ` adopted Davis
   and Mapleson 1981 on the project owner's decision of 2026-09-07.
2. **1.0 L was never a Gas Man reference value.** `PL-XTMB` read the Workbook
   at the source: its Model Parameters table's `Blood` row is 5.00 L and no
   1.0 L figure appears in it anywhere. `PL-3YZW` established that the value
   entered at v0.1.0 under a citation belonging to its neighbours - it is this
   project's own modelling choice, and the file now says so.
3. **The time constant is 14.7 s**, not 12 s, at the same 5.0 L/min.

**Why it matters.** `docs/WORKING_NOTES.md`'s own preamble says an entry
should be written so "a reader with no memory of the originating conversation
can act on it", and this one now teaches a reader three wrong facts about a
stored clinical parameter, including the one - "it is the Gas Man value" - that
`docs/MODEL.md`'s source hierarchy exists to stop anybody inferring. It carries
an "Amended 2026-09-03" parenthesis correcting an earlier version of the same
sentence, so the entry has already been maintained once and this is the second
correction it needs rather than a first pass.

**Approach.** The thread it describes is resolved - `PL-024` retired, the value
sourced, the meaning stated in `docs/MODEL.md` - so `CLAUDE.md`'s rule applies:
"When a thread here is fully resolved (implemented, tested, and merged), its
outcome belongs in `ROADMAP.md`/`docs/MODEL.md`/commit history as appropriate,
and its entry here should be deleted rather than left stale." Check that
nothing in the entry is unrecorded elsewhere - the v0.4.7 release row and
`reference_adult.json`'s Davis and Mapleson entry between them appear to carry
all of it - and delete the entry rather than amending it a second time.


**Done when.** The `PL-024` entry is deleted from `docs/WORKING_NOTES.md` per
`CLAUDE.md`'s rule for a resolved thread, after confirming that nothing in it is
unrecorded elsewhere - the v0.4.7 release row and `reference_adult.json`'s Davis
and Mapleson entry between them appear to carry all of it. Amending it a second
time is the outcome to avoid: the thread is resolved, so the entry has no reason
to exist whatever numbers it holds.
