---
id: PL-4JHS
title: Backfill the recurrences the store has already paid for onto the items that absorbed them, so the counter starts from the nine known duplicate pairs rather than from zero
priority: P3
effort: S
status: done
classes: infra
feature: recurrence-signal
touches: docs/items
blocked-by: PL-X5JR
added: 2026-09-20
closed: 2026-09-20
pr: 809
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

## What was written, 2026-09-20

Thirteen entries across nine anchors, every one a duplicate a session had
already confirmed by reading both briefs - `PL-JKML`'s nine same-finding rows,
the chain it names for `PL-W7WL`, and the drop reasons the store itself
carries. Written through `store.insert_field(..., append=...)`, so the diff is
nine added lines and no removals, which is what
`verify.sanctioned_queue_edit` classifies as a `recurrence`.

| anchor | status | filings recorded | count |
| --- | --- | --- | --- |
| `PL-W7WL` | ready | `PL-66X4` 09-13, `PL-2M5T` 09-14, `PL-3HMQ` 09-20 | 3 |
| `PL-STC4` | done | `PL-4FD2` 09-19, `PL-0KQP` 09-20 | 2 |
| `PL-LBR6` | done | `PL-5QLP` 09-19, `PL-QMC0` 09-19 | 2 |
| `PL-TZ7T` | done | `PL-TH7P` 08-30 | 1 |
| `PL-4HKS` | ready | `PL-5748` 09-07 | 1 |
| `PL-4RHP` | ready | `PL-HCTF` 09-19 | 1 |
| `PL-GXPP` | ready | `PL-R77L` 09-19 | 1 |
| `PL-KSCW` | ready | `PL-SH9Q` 09-16 | 1 |
| `PL-YRYR` | ready | `PL-W6NY` 09-05 | 1 |

**How many of these can surface anything: one.** `PL-W7WL` crosses
`MIN_RECURRENCES` at three filings and `bin/docket next` now names it under
"Filed more than once, and never promoted for it", beside `PL-SHTR`. Nothing
else can: `plan.recurring` names open items only, and the two anchors that
also reach the threshold - `PL-STC4` and `PL-LBR6` - are both closed. So the
`payoff:` line above overstates what landed, exactly as the paragraph before
this one predicted it would. The honest statement is that **the record is the
deliverable and one promotion candidate is the by-product**: five open anchors
now sit at one filing rather than zero, so the *next* re-filing of any of them
crosses instead of the third.

**Anchoring, and the two clusters that are already generators.** Entries went
onto one member per cluster rather than pair-by-pair, for the reason
`duplicates.anchor` exists - a five-item cluster spread over three items is a
cluster nothing surfaces. Two anchors carry a `root-cause-of:` already
(`PL-G21K` over the `verify-false-reject` cluster, `PL-TZ7T` over
`slug-rename-on-write`), so `plan.recurring` excludes them by construction and
the entries there are pure record. They were written anyway: this item's own
`verify:` command asks for a `recurrences:` line on `PL-STC4`, and
`MIN_RECURRENCES`'s docstring calibrates the threshold on the slug-rename
cluster "peaking at two" - which is now true in the store rather than only in
the comment.

**What was not written, and why.** No entry rests on a similarity score. The
sweep's complementary-halves rows are not duplicates and got none - two halves
of one feature are already recorded by `feature:`. The 131 dropped items whose
`reason:` names another id were not swept: most are "superseded", "premise
false" or "already fixed" rather than re-filings, and separating them is a
fresh judgment pass, which this item's brief forbids.

**Done when, checked.** Every confirmed duplicate pair the sweep left in the
store now carries a dated entry on its survivor, and the one anchor that both
crosses three filings and is still open is visible as a promotion candidate.
