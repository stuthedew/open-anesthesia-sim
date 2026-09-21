---
id: PL-TTKP
title: Triage the 20 untriaged captures standing in the queue on 2026-09-21
priority: P2
effort: S
status: done
classes: housekeeping
milestone: v0.5.1
touches: docs/items, ROADMAP.md
added: 2026-09-21
closed: 2026-09-21
pr: 851
payoff: the queue stops carrying twenty captures no session can rank, and the thirteen of them that are debt reach v0.6.0's gate where they can be counted
verify: test "$(grep -l '^status: untriaged' docs/items/*.md | wc -l)" -le 1
---

**Problem.** Triage the 20 untriaged captures standing in the queue on 2026-09-21
