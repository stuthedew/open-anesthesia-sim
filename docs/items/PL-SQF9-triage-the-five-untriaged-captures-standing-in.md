---
id: PL-SQF9
title: Triage the five untriaged captures standing in the queue on 2026-09-21: PL-DZM1, PL-NGBM, PL-T441, PL-TJTV, PL-X9WZ
priority: P2
effort: S
status: done
classes: housekeeping
feature: stranded-triage-sweep
milestone: v0.5.0
touches: docs/items
added: 2026-09-21
closed: 2026-09-21
pr: 837
payoff: the queue stops carrying five captures bin/docket next cannot rank, so what is actually next stops being understated
verify: ! grep -q "^status: untriaged" docs/items/PL-DZM1*.md docs/items/PL-NGBM*.md docs/items/PL-T441*.md docs/items/PL-TJTV*.md docs/items/PL-X9WZ*.md
---

**Problem.** Triage the five untriaged captures standing in the queue on 2026-09-21: PL-DZM1, PL-NGBM, PL-T441, PL-TJTV, PL-X9WZ
