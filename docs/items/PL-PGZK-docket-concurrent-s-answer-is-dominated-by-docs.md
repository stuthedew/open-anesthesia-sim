---
id: PL-PGZK
title: docket concurrent's answer is dominated by docs/MODEL.md, which nearly every item touches, so it rules out almost everything and cannot discriminate between real and nominal contention
status: needs-decision
added: 2026-09-03
priority: P2
effort: M
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, docs/items/
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

**Decision needed.** Which of the three options below to build. Recommended:
rank the collisions by how many items declare the shared path, so a hub file
reads as weak evidence and a rarely-touched source file as strong. It needs no
change to the `touches:` format, so no existing item has to be rewritten, and
it degrades gracefully - a path nothing else declares still reads as a hard
collision. Reject it only if a ranked answer turns out to be one a session
skims past, in which case the excluded-hub-set option is the fallback, since it
is the only one that changes what is *reported* rather than how it is ordered.

**Options, not yet decided.** Rank the collisions by how many items declare
the shared path, so a hub file reads as weak evidence and a rarely-touched
source file as strong; or let `touches:` name a section rather than a file for
documentation paths; or exclude a configured set of hub paths from the answer
and say so in the output. The first needs no format change and is the cheapest
to try.

**Found.** 2026-09-03, planning the `v0.4.0` implementation order. Not fixed
in that session.

**Done when.** `bin/docket concurrent` distinguishes contention on a hub path
from contention on a file few items touch, so a session planning a batch inside
one milestone gets an answer it can act on rather than a near-universal refusal.
Measured on the same two probes that produced this finding - `PL-ZRSP` returned
22 rule-outs of which 16 shared only `docs/MODEL.md`, and `PL-DR1Z` the same
shape - the reported set discriminates between those two kinds. The command's
contract is unchanged and restated in the output: it rules work out, it never
certifies it, so whatever it now reports as weak evidence is still reported
rather than silently dropped.

