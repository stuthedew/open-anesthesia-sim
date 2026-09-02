---
id: PL-3QGR
title: The queue's storage layer, not its information model, is what blocks concurrent work
status: done
classes: session-cost
feature: dev-tooling
milestone: v0.2.3
added: 2026-08-24
closed: 2026-08-24
commit: f5ffae0
pr: 27
---

**Problem.** `docs/PUNCH_LIST.md` was simultaneously the data store, the
human-readable view and the coordination point. That conflation caused three
things the information model itself did not: every capture and close-out wrote
the same regions of one file, so any two concurrent sessions contended; ids
were allocated by reading the file, so two branches allocated the same one
(observed 2026-08-24, PL-042 twice); and there was no in-progress state, so
nothing stopped two sessions starting the same item.

**Why it matters.** It made deliberate concurrent work impossible to reason
about. The entry format, the cold-start brief, the mechanical validation, the
disposal ledger and the model routing were all sound — the defect was where
the data lived, not what it said.

**Resolution.** One file per item in `docs/items/`, read and written by the
`docket` package in `subprojects/`. Adding work adds a file, so writers do not
contend; ids are random, so none is allocated from shared state; in-flight
state is derived from branch names, so it cannot go stale. `touches` on each
item feeds a conflict graph, which is what makes "can these two run together?"
answerable at all.

**Done when.** Met: the queue is one file per item, `docket concurrent` answers
the concurrency question, and no id is allocated by reading shared state.
