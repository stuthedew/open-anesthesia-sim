---
id: PL-QB26
title: Record the owner's 2026-09-23 'fix it right once' direction beside the open decision on each live generator head, PL-5MYR and PL-K046
priority: P2
effort: S
status: done
classes: housekeeping
feature: generator-identification
milestone: v0.5.9
touches: docs/items
added: 2026-09-23
closed: 2026-09-23
pr: 972
payoff: Every session that opens a live head's design round reads the owner's durable-route direction on the item, not in a reply that is gone when this session is archived
verify: grep -l 'fix it right once' docs/items/PL-B8HZ-*.md docs/items/PL-QHCW-*.md docs/items/PL-HMZZ-*.md docs/items/PL-MB2W-*.md docs/items/PL-GHHW-*.md docs/items/PL-5MYR-*.md docs/items/PL-K046-*.md | wc -l | grep -qx 7
---

**Problem.** Record the owner's 2026-09-23 'fix it right once' direction beside the open decision on each live generator head, PL-5MYR and PL-K046
