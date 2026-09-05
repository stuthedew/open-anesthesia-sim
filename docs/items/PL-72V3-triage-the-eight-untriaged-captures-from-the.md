---
id: PL-72V3
title: Triage the eight untriaged captures from the 2026-09-05 sessions
priority: P2
effort: S
status: done
classes: planning
feature: planning-cadence
touches: docs/items
added: 2026-09-05
closed: 2026-09-05
not-delegable: a triage pass is proven by the store's state at the moment it ran, and that state moves - captures arrive untriaged by design - so no command run afterwards separates 'the pass happened' from 'nothing has been captured since'. `bin/docket check`, already on `make check`, is the standing proof that what the pass wrote is valid (same argument as PL-SN5S)
---

**Problem.** Nine items sat at `status: untriaged` with no fields. Eight are
triaged here: `PL-3VKZ`, `PL-JK0M`, `PL-JSRH`, `PL-Q4M4`, `PL-QM5P`, `PL-VP40`,
`PL-XXBD` and `PL-Z0G0`. The ninth, `PL-ZK9R` (widen the `core/` import
boundary to `secrets` and `uuid`), is marked `IN FLIGHT` on
`origin/claude/next-workflow-item-hqid0n` and is left alone: a second answer
here is a second resolution of the same file, and the merge keeps only one.

**Why it matters.** `_startable` in `plan.py` drops an untriaged item, so a
capture is outside the ranking entirely until somebody triages it - not
low-priority work but invisible work. `untriaged_stale_days = 14` is this
store's statement of how long that is tolerable.

Two of the eight carried a defect capture cannot catch. `PL-3VKZ` declared
`touches: docs` and `PL-XXBD` declared `touches: src`, and neither is *under*
a `protected_paths` entry - `is_under` compares path prefixes, so `src` does
not match `src/anesthesia_sim/core`. Both items therefore read as lying wholly
outside the protected tree while in fact covering all of it, which is what
`Item.delegability` consults. Naming the subtrees is part of triage, not
tidying.

**Where.** The eight item files under `docs/items/`.

**Done when.** Each of the eight carries `priority`, `effort`, `classes`,
`touches` and a `feature`; each sits at a status the checker will hold to its
brief, with a `verify:` command that was run and watched fail, or a
`not-delegable` reason; and `bin/docket check` reports no untriaged items
beyond the one in flight.
