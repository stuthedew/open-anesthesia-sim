---
id: PL-DRRG
title: Cut v0.5.11 from the 16 items finished since v0.5.10
priority: P2
effort: S
status: ready
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
resource: release-train
added: 2026-09-25
payoff: the 16 items finished since v0.5.10 ship under their own number and stop being re-offered in every session digest
verify: grep -q "^version = \"0.5.11\"" pyproject.toml
---

**Problem.** Cut v0.5.11 from the 16 items finished since v0.5.10
