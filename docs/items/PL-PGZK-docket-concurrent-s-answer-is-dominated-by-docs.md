---
id: PL-PGZK
title: docket concurrent's answer is dominated by docs/MODEL.md, which nearly every item touches, so it rules out almost everything and cannot discriminate between real and nominal contention
status: untriaged
added: 2026-09-03
---

**Problem.** `docket concurrent <id>` reports contention from declared
`touches` overlap. `docs/MODEL.md` is declared by a large fraction of the
queue, so it dominates every answer: measured 2026-09-03, `bin/docket
concurrent PL-ZRSP` returned 22 items it "cannot run alongside", and 16 of
those shared `docs/MODEL.md` and nothing else. `PL-DR1Z` returned the same
shape. Two items that both append a paragraph to different sections of
`docs/MODEL.md` are reported identically to two items that both rewrite
`simulation_view.py`'s run loop.

**Why it matters.** The command's stated contract is to rule work out, never
to certify it (`.claude/skills/docket/SKILL.md`, "Mode: work several items at
once"), so a false *positive* is the one failure it has no defence against. At
this hit rate the answer stops discriminating: a session planning a batch
inside `v0.4.0` is told that nearly every pair collides, which is the same
information as being told nothing, and the cheap response is to stop running
it. That is `CLAUDE.md`'s retirement test — a check that fires every run
without changing a decision.

**Where.** `subprojects/docket/src/docket/` (whatever computes the overlap),
and the `touches:` convention itself.

**Options, not yet decided.** Rank the collisions by how many items declare
the shared path, so a hub file reads as weak evidence and a rarely-touched
source file as strong; or let `touches:` name a section rather than a file for
documentation paths; or exclude a configured set of hub paths from the answer
and say so in the output. The first needs no format change and is the cheapest
to try.

**Found.** 2026-09-03, planning the `v0.4.0` implementation order. Not fixed
in that session.
