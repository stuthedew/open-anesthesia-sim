---
id: PL-8D1M
title: Promote PL-5XG1 and PL-ZYHX to ready: every recorded blocker has closed and both verify commands still fail
priority: P3
effort: S
status: done
classes: housekeeping
feature: blocked-means-blocked
milestone: v0.5.23
touches: docs/items/PL-5XG1-roadmap-md-s-development-pathway-still-says.md, docs/items/PL-ZYHX-the-resident-instruction-set-is-75-kb-72.md
added: 2026-10-11
closed: 2026-10-11
pr: 1426
payoff: the two items reach bin/docket next instead of sitting behind blockers that closed 15 and 8 days ago
verify: grep -q '^status: ready' docs/items/PL-5XG1-roadmap-md-s-development-pathway-still-says.md && grep -q '^status: ready' docs/items/PL-ZYHX-the-resident-instruction-set-is-75-kb-72.md
---

**Problem.** Promote PL-5XG1 and PL-ZYHX to ready: every recorded blocker has closed and both verify commands still fail

**Generator check.** A member of the mechanism `PL-2349` names (a released item
left `blocked` because the store offers no exit short of `ready`), which reads
`PL-6T44`'s fact from the writer's side; `PL-2349` carries the count and why it
is not recorded as a live head.
