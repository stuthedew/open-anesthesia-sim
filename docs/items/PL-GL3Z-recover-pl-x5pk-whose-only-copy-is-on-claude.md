---
id: PL-GL3Z
title: Recover PL-X5PK, whose only copy is on claude/sharp-lamport-t545rs - a branch whose session is archived and whose pull request merged without it
priority: P2
effort: S
status: done
classes: housekeeping
feature: stranded-triage-sweep
touches: docs/items
added: 2026-09-21
closed: 2026-09-21
pr: 837
payoff: PL-X5PK's flight-detection observation stops living only on an archived session's branch, so the next session can read it from the store
verify: test -f docs/items/PL-X5PK-bin-docket-flight-reported-a-squash-merged.md
recurrences: 2026-09-21 PL-CZR6
---

**Problem.** Recover PL-X5PK, whose only copy is on claude/sharp-lamport-t545rs - a branch whose session is archived and whose pull request merged without it
