---
id: PL-38HD
title: Cut v0.5.6 from the twelve items finished since v0.5.5: the in-flight guards stop reporting work as nobody's, and verify's assertion check reads parsed statements rather than lines, with nothing in the simulator moving
priority: P2
effort: S
status: ready
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-23
payoff: the twelve items finished since v0.5.5 ship under their own number and stop being re-offered in every session digest, and a release that moves nothing a learner can reach says so by tree identity rather than by assertion
verify: grep -q "^version = \"0.5.6\"" pyproject.toml
---

**Problem.** Cut v0.5.6 from the twelve items finished since v0.5.5: the in-flight guards stop reporting work as nobody's, and verify's assertion check reads parsed statements rather than lines, with nothing in the simulator moving
