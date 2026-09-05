---
id: PL-2TCS
title: Triage the fourteen captures from the 2026-09-05 sessions
priority: P2
effort: S
status: done
classes: planning
feature: planning-cadence
touches: docs/items
added: 2026-09-05
closed: 2026-09-05
not-delegable: a triage pass is proven by the store's state at the moment it ran, and that state moves - captures arrive untriaged by design - so no command run afterwards separates 'the pass happened' from 'nothing has been captured since'. `bin/docket check`, already on `make check`, is the standing proof that what the pass wrote is valid (same argument as PL-SN5S and PL-MPTN)
---

**Problem.** Fourteen captures from the 2026-09-05 sessions reached the queue
with `status: untriaged` and no fields: `PL-0SHZ`, `PL-3BC5`, `PL-3V4N`,
`PL-BTSW`, `PL-GTW5`, `PL-GZPX`, `PL-HXKC`, `PL-KJ63`, `PL-MPZ0`, `PL-NT6G`,
`PL-QV1F`, `PL-T137`, `PL-TCD1` and `PL-XNHJ`. Capture deliberately skips
`priority`, `effort`, `classes`, `touches` and `feature` so that recording a
finding costs one command; this is the pass that supplies them.

**Why it matters.** An untriaged item is in no band, so `bin/docket next` cannot
offer it and `bin/docket gate` cannot count it as debt. Fourteen of them is a
second queue nobody reads. Nine of the fourteen carry a debt class or reach
`needs-decision`, so they are what the *next* milestone's gate will count -
v0.4.0's is already frozen and cleared, 21 of 21, and a finding made after a
freeze goes to the following gate.

It is also where a re-discovery is caught. Two of the fourteen turned out to
restate items already open - `PL-GTW5` restating `PL-4WQS` three days on, and
`PL-3BC5` restating `PL-J3BB` two days on - and both were reachable by ordinary
use rather than by looking, which is evidence about the defects as much as about
the queue.

**Where.** `docs/items/`, the fourteen files above.

**Done when.** Every one of the fourteen carries a band, an effort, a status and
the classes that place it; `bin/docket check` reports no errors; the two captured
as bare stubs and kept - `PL-0SHZ` and `PL-TCD1` - carry a brief a stranger can
start from; and each duplicate is `dropped` with a reason naming the item that
holds the work.
