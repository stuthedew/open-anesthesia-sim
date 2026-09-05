---
id: PL-SN5S
title: Triage the six captures from the 2026-09-05 sessions
priority: P2
effort: S
status: done
classes: planning
feature: planning-cadence
touches: docs/items
added: 2026-09-05
closed: 2026-09-05
pr: 332
not-delegable: a triage pass is proven by the store's state at the moment it ran, and that state moves - captures arrive untriaged by design - so no command run afterwards separates 'the pass happened' from 'nothing has been captured since'. `bin/docket check`, already on `make check`, is the standing proof that what the pass wrote is valid (same argument as PL-MPTN)
---

**Problem.** Six captures from the 2026-09-05 sessions reached the queue with
`status: untriaged` and no fields: `PL-2LHF`, `PL-D188`, `PL-GBBZ`, `PL-JBZK`,
`PL-KBD0` and `PL-ZQ35`. Capture deliberately skips `priority`, `effort`,
`classes`, `touches` and `feature` so that recording a finding costs one
command; this is the pass that supplies them.

**Why it matters.** `_startable` in `plan.py` drops an untriaged item, so a
capture is outside the ranking entirely until somebody triages it - it is not
low-priority work, it is invisible work. `untriaged_stale_days = 14` is this
store's own statement of how long that is tolerable, and the six here arrived
the same day.

**Where.** The six item files under `docs/items/`.

**Done when.** Each of the six carries `priority`, `effort`, `classes`,
`touches` and a `feature`; each sits at a status the checker will hold to its
brief; and `bin/docket check` reports no untriaged items.
