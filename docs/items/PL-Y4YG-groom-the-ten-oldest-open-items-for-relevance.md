---
id: PL-Y4YG
title: Groom the ten oldest open items for relevance on 2026-09-22: drop what the tree has overtaken, bring the rest up to date
priority: P2
effort: S
status: done
classes: housekeeping
touches: docs/items
added: 2026-09-22
closed: 2026-09-22
pr: 914
payoff: the ten items that have waited longest stop describing a Flet interface, a 1.0 L venous pool and coverage numbers that no longer exist, so whoever picks one up starts from the tree as it is
verify: grep -q "^status: dropped" docs/items/PL-027-*.md && grep -q "^status: dropped" docs/items/PL-ZBR6-*.md && test -z "$(grep -L "Groomed 2026-09-22" docs/items/PL-024-*.md docs/items/PL-029-*.md docs/items/PL-038-*.md docs/items/PL-043-*.md docs/items/PL-NC2P-*.md docs/items/PL-41YP-*.md docs/items/PL-8LDF-*.md docs/items/PL-Z7LY-*.md)"
---

**Problem.** Groom the ten oldest open items for relevance on 2026-09-22: drop what the tree has overtaken, bring the rest up to date
