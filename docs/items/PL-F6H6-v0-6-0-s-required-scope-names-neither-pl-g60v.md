---
id: PL-F6H6
title: v0.6.0's Required scope names neither PL-G60V nor PL-5HSG, though PL-W9P6 and PL-2KXB wait on them since #1448, so bin/docket wave reads eight gate entries as blocked by two items no section places
priority: P2
effort: S
status: done
classes: housekeeping
touches: ROADMAP.md
added: 2026-10-12
closed: 2026-10-12
pr: 1462
payoff: v0.6.0's plan names every item its Required scope waits on, so wave and next read the two layout-model corrections as milestone work instead of work no section places
verify: grep -q 'PL-G60V' ROADMAP.md && grep -q 'PL-5HSG' ROADMAP.md
---

**Problem.** v0.6.0's Required scope names neither PL-G60V nor PL-5HSG, though PL-W9P6 and PL-2KXB wait on them since #1448, so bin/docket wave reads eight gate entries as blocked by two items no section places

Measured 2026-10-12 with `bin/docket wave --no-fetch`. On `main` before
`#1448` the beat read "11 blocked outside it by 5 open items the milestone's
Required scope names"; after it, "8 blocked outside it by 2 open items, and by
4 open items the milestone's Required scope names", and the gate line "what
they wait on: PL-5HSG, PL-G60V". `#1448` recorded the owner's answers to both
items, and its `blocked-by` edges put `PL-5HSG` ahead of `PL-W9P6` (the
adapter) and `PL-G60V` ahead of `PL-2KXB` (the operations a reader performs),
while no section of v0.6.0 places either, so `bin/docket show` ranks each "on
its band alone".

**Decided 2026-10-12, by the session that made the edges: name both in
Required-scope entry 1, the layout model.** Each changes an operation entry 1
lists, `PL-G60V` the `join` and `PL-5HSG` the `resize`. The owner's answer on
`PL-5HSG` already puts it before `PL-W9P6`, entry 2, so naming it records what
that answer implies rather than widening the milestone; `PL-G60V`'s place
before `PL-2KXB`, entry 14, is that session's sequencing, so a reader building
the join is never offered one that depends on which split came first. Chosen
over entries 2 and 14, whose items only wait on these two, and over the frozen
gate list, which holds debt where neither item is (`feature` and `ux`). The
ids go inside entry 1's `(queue items ...)` slot, the only place
`roadmap._declared_ids` reads (`PL-YVP7`). Undone by deleting the two ids.
