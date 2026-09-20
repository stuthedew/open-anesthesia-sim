---
id: PL-4JHS
title: Backfill the recurrences the store has already paid for onto the items that absorbed them, so the counter starts from the nine known duplicate pairs rather than from zero
status: blocked
feature: recurrence-signal
touches: docs/items
added: 2026-09-20
priority: P3
effort: S
classes: infra
blocked-by: PL-X5JR
payoff: starts the counter from what the store has already paid for, so the first promotion candidates appear at once rather than after three more defects have each been re-found
verify: grep -c 'recurrences:' docs/items/PL-STC4-docket-verify-s-suppression-check-reads-prose.md
---

**Problem.** Backfill the recurrences the store has already paid for onto the
items that absorbed them, so the counter starts from the nine known duplicate
pairs rather than from zero.

**Why it matters.** Until the counter holds what the store has already paid for,
the first promotion candidate is three *future* re-findings away - and those
three re-findings are the cost the mechanism exists to stop. The backfill is
what makes it useful on the day it lands rather than a quarter later.

**Why it is worth doing rather than letting the counter fill naturally.** An
empty counter takes three fresh re-findings of the *same* defect before it says
anything, and the whole point of the mechanism is that those three re-findings
are the cost being avoided. The store already holds the evidence for at least
two clusters that would cross the threshold on day one.

**What is known on 2026-09-20, before the sweep runs.**

- The suppression-check cluster: `PL-5MFL`, `PL-BHBZ`, `PL-STC4`, `PL-4FD2` and
  `PL-0KQP` - five captures, one defect, at least three sessions, two days.
- The slug-rename cluster: `PL-LBR6` with `PL-5QLP` and `PL-QMC0` filed as fresh
  discoveries, recorded in `PL-TZ7T`'s own brief.
- Two pairs confirmed by reading both briefs during the 2026-09-20 open-store
  sweep: `PL-4HKS` / `PL-5748` (`docs/WORKING_NOTES.md`'s playback-speed thread
  stating stale pre-`PL-010` frame costs as current, filed twelve days apart)
  and `PL-2M5T` / `PL-W7WL` (`docket release` writing notes before `docket
  record` backfills `pr:`, filed six days apart).

**Take the sweep's output as the input.** A separate session is reading the 21
ungrouped candidate pairs the 2026-09-20 sweep surfaced, and its confirmed pairs
are what this item writes down. Do not re-derive the list here, and do not write
a recurrence for a pair the sweep did not confirm by reading both briefs -
whether two items are one defect is judgment, and a backfill built from a
similarity score would seed the counter with exactly the error the surfacing
rule refuses to act on alone.

**Done when** every confirmed duplicate pair in the store has left a dated entry
on the item that survives it, and the items that cross three are visible as
promotion candidates.

**What actually holds it, 2026-09-20.** `PL-X5JR` closed, so the mechanism this
backfills into exists: `recurrences:` is a field, `bin/docket new` writes it,
`docket check` validates it, and `bin/docket next`, `show` and the digest surface
an item at three. `blocked-by:` named only that item and now resolves, so the
store reads this as promotable - it is not.

The remaining blocker is the input rather than the mechanism. This item's own
brief says to take the 2026-09-20 open-store sweep's confirmed pairs and to
write no recurrence for a pair the sweep did not confirm by reading both briefs.
That sweep is a separate session (`PL-JKML`, which exists on its branch and not
in this checkout, so `blocked-by:` cannot name it yet). Until its confirmed pairs
land, there is nothing to write, and building the list from a similarity score
instead would seed the counter with exactly the error the surfacing rule refuses
to act on alone.

Two things the mechanism now fixes about the plan here. There is no `docket set`
flag for the field, deliberately - its worth is that each entry was written by
the tool at the moment it matched a filing - so the backfill writes through
`store.insert_field(..., append=...)`, which is byte-faithful and is what `new`
itself uses. And the entries this backfill writes should anchor on one member per
cluster rather than pair-by-pair: `duplicates.anchor` is why the live counter
accumulates instead of fragmenting, and a backfill that spread a five-item
cluster over three items would reproduce the exact failure that measurement
found (see `PL-X5JR`).

**The inputs this brief names have mostly closed since it was written, checked
against `origin/main` on 2026-09-20 after `#783`.** Of the suppression cluster
it lists as its first input, `PL-5MFL` and `PL-BHBZ` are `done`, `PL-4FD2` and
`PL-0KQP` are `dropped`, and only `PL-STC4` is still open. The whole of the
slug-rename cluster - `PL-LBR6`, `PL-5QLP`, `PL-QMC0` - closed before that.

That is not a reason to drop this item, but it does change what it buys, and the
brief above overstates it. `plan.recurring` names open items only, deliberately:
a closed item's defect is fixed and the cluster is nobody's to pull. So a
backfill onto a closed anchor writes an accurate record and surfaces nothing,
and the claim that "the first promotion candidates appear at once" now holds
only for the pairs whose anchor is still open. Whoever works this should re-read
the sweep's confirmed pairs against `origin/main`'s statuses first and say, in
the close-out, how many of them can surface anything - the honest answer may be
that the value here is the record rather than the surfacing, which is a smaller
item than `payoff:` currently claims.

The record is still worth having on a closed item: `bin/docket show` prints the
filings whatever the status, so the next session to reopen or cite one of these
can see that the defect was found five times rather than once.
