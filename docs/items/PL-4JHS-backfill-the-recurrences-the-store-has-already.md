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
