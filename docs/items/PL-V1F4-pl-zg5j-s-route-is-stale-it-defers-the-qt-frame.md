---
id: PL-V1F4
title: PL-ZG5J's route is stale: it defers the Qt frame-cost harness to 'build it once under PL-YCWZ', and PL-YCWZ closed with the port, so the item's first step points at a finished item
priority: P3
effort: S
status: done
classes: docs
feature: frame-cost-harness
touches: docs/items
added: 2026-09-16
closed: 2026-09-19
pr: 703
verify: grep -q 'The port is done, so the toolkit question is settled' docs/items/PL-ZG5J-*.md && ! grep -q 'rather than landing a Flet one now' docs/items/PL-ZG5J-*.md
---

**Problem.** PL-ZG5J's route is stale: it defers the Qt frame-cost harness to 'build it once under PL-YCWZ', and PL-YCWZ closed with the port, so the item's first step points at a finished item

**Why it matters.** `PL-ZG5J`'s first step tells whoever starts it to defer the
frame-cost harness to `PL-YCWZ`, and `PL-YCWZ` closed with the Qt port. A route
that points at a finished item reads as "this is blocked" to the next session,
which is a wrong answer in the direction nobody challenges; and the deferral's
whole premise - don't build a Flet harness that the port will throw away - has
been satisfied rather than refuted, so the work is now unblocked and the item
says the opposite.

**Done when** `PL-ZG5J`'s route names the port as done and says what building the
harness costs now that the toolkit question is settled, so its first step is
actionable rather than a pointer.
