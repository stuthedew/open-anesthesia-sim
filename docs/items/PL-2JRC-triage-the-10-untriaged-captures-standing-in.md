---
id: PL-2JRC
title: Triage the 10 untriaged captures standing in the queue on 2026-09-21
priority: P2
effort: S
status: done
classes: housekeeping
touches: docs/items, ROADMAP.md
added: 2026-09-21
closed: 2026-09-21
pr: 880
payoff: the 10 captures standing in the queue stop being a second queue nobody reads, invisible to bin/docket next and uncounted by bin/docket gate
verify: ! grep -l '^status: untriaged' docs/items/PL-2JRC-*.md docs/items/PL-6SRZ-*.md docs/items/PL-H0CF-*.md docs/items/PL-M3X6-*.md docs/items/PL-M7W1-*.md docs/items/PL-P55F-*.md docs/items/PL-RFHH-*.md docs/items/PL-YZJD-*.md docs/items/PL-Z891-*.md
---

**Problem.** Triage the 10 untriaged captures standing in the queue on 2026-09-21
