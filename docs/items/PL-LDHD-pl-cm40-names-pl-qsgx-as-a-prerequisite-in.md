---
id: PL-LDHD
title: PL-CM40 names PL-QSGX as a prerequisite in prose without declaring it, so docket check has advised on every run since 2026-09-19
priority: P3
effort: S
status: done
classes: housekeeping
touches: docs/items
added: 2026-09-20
closed: 2026-09-20
pr: 781
payoff: clears the prose-prerequisite advisory docket check has printed on every run for two days, so the next one that fires is read rather than skimmed past
verify: grep -q '^blocked-by: PL-QSGX' docs/items/PL-CM40-no-single-command-prints-the-refreshed-picture.md
---

**Problem.** PL-CM40 names PL-QSGX as a prerequisite in prose without declaring it, so docket check has advised on every run since 2026-09-19
