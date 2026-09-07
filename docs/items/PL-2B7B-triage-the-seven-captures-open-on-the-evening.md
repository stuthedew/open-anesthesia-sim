---
id: PL-2B7B
title: Triage the seven captures open on the evening of 2026-09-07
priority: P2
effort: S
status: done
classes: planning
feature: planning-cadence
touches: docs/items
added: 2026-09-07
closed: 2026-09-07
not-delegable: a triage pass is proven by the store's state at the moment it ran, and that state moves - captures arrive untriaged by design - so no command run afterwards separates 'the pass happened' from 'nothing has been captured since'. `bin/docket check`, already on `make check`, is the standing proof that what the pass wrote is valid (same argument as PL-Q2PX and PL-LYX2)
---

**Problem.** Seven captures reached the queue with `status: untriaged` and no
fields, from the 2026-09-07 sessions that closed `PL-D188` and `PL-JL2M` (the
capture template stranded above a later-written brief), `PL-GBBZ` (the
undeclared prose prerequisites) and `PL-T691` (hold the run as keyframes).
Capture deliberately skips `priority`, `effort`, `classes`, `touches` and
`feature` so that recording an idea costs one command; folding them into the
queue is a separate pass. One of the seven, `PL-QV5Y`, also arrived with three
required brief headings empty, which blocks any status past `untriaged`.

**Why it matters.** An untriaged item is invisible to `bin/docket next` and to
`bin/docket gate`, so a finding sits where no session would be offered it and
where the next gate's count cannot see it. Two of these seven were stale on
arrival and would otherwise have been handed to a session as live work:
`PL-KFWL`'s tag half was already resolved - `v0.4.8` is absent from
`git ls-remote --tags origin` and `python3 tools/doc_check.py check` reports 0
errors - leaving only its guard; and `PL-LLDB` asked for a repair to
`PL-T691`'s `verify:` field that `PL-T691` had already made before closing,
which `docket check` now refuses to rewrite because a closed item's command is
a record rather than a live specification.

The pass also promoted `PL-1JDD` (make the source tier machine-readable so
`doc_check` can decide it), whose two blockers `PL-6Q8N` and `PL-D6LX` have
both closed. Its premise was re-checked rather than assumed: all four data
files under `src/anesthesia_sim/data/` are still at `schema_version: 1` with no
`tier` key, and the item's own `verify:` command exits 1 today with both
healthy halves passing.

**Done when.** No item in `docs/items/` carries `status: untriaged`, and
`bin/docket check` reports no errors.
