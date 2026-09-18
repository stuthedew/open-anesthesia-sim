---
id: PL-S0MB
title: Catch-all feature names can never report completion: dev-tooling carries 174 items and queue-hygiene 29, so bin/docket feature <name> cannot answer 'yes, that is dealt with' for either, and 32 of 33 workflow features read as live
status: untriaged
feature: convergence-visibility
touches: docs/items, docket.toml
added: 2026-09-17
---

**Problem.** Catch-all feature names can never report completion: dev-tooling carries 174 items and queue-hygiene 29, so bin/docket feature <name> cannot answer 'yes, that is dealt with' for either, and 32 of 33 workflow features read as live

**Observed 2026-09-17.** `CLAUDE.md` requires a group be named for what
*completes*. Two of the workflow lane's largest are named for an area instead,
and an area never finishes.

| feature | items | open | filed prev 7d | filed last 7d |
| --- | --- | --- | --- | --- |
| dev-tooling | 174 | 44 | 58 | 28 |
| parallel-sessions | 71 | 19 | 33 | 17 |
| queue-hygiene | 29 | 18 | 0 | 29 |

Across the whole lane: **33 workflow features, of which 5 have no open items
and 1 meets the stricter test of no open items and nothing filed for 7+ days.**
So 32 of 33 read as live work.

**The cost is not tidiness.** `.claude/rules/instruction-writing.md` rule 14
sends a reader to `bin/docket feature <name>` so that "is that dealt with?" has
a command behind it rather than a memory. For `dev-tooling` that command cannot
ever answer yes: something was filed against it yesterday and something will be
tomorrow, because the name admits anything touching a tool. The reader asking
whether progress is being made is told, correctly and uselessly, that 44 items
are open. This is a measurable contributor to the lane reading as
whack-a-mole when its severity mix says otherwise — 0 open P1, 51% of the open
backlog P3.

`queue-hygiene` is the same failure forming in real time: 0 items filed in the
week to 09-10, 29 in the week to 09-17. It is becoming the next bucket.

**Counter-case to answer before splitting.** Some of these names may be doing
real work as lane or routing hints rather than as completion groups, and
splitting 174 items by hand is itself apparatus work of the kind `CLAUDE.md`
warns about becoming the project. The number that decides it: how many of
`dev-tooling`'s 44 open items fall into groups that *would* terminate. If the
answer is that they are genuinely unrelated one-offs with no completing group
among them, the remedy is not a split but dropping the feature field on them,
so the queue stops claiming a grouping it does not have.

**Do not resolve this by renaming alone.** A name that completes but still
carries unrelated items moves the problem rather than removing it.
