---
id: PL-KNWP
title: Cut v0.5.7 from the seventeen items finished since v0.5.6: a git call that fails stops reading as an empty answer, and a brief's prose is held to its own status, with nothing in the simulator moving
priority: P2
effort: S
status: ready
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-23
payoff: the seventeen items finished since v0.5.6 ship under their own number and stop being re-offered in every session digest, and brief-state-agreement ships complete
verify: grep -q "^version = \"0.5.7\"" pyproject.toml
---

**Problem.** Cut v0.5.7 from the seventeen items finished since v0.5.6: a git call that fails stops reading as an empty answer, and a brief's prose is held to its own status, with nothing in the simulator moving

Seventeen items have closed since v0.5.6 and are re-offered in every session
digest, and `bin/docket release --dry-run` reports that they complete
`brief-state-agreement`. The project owner asked for the cut by number
(2026-09-23), which is also the dry run's mechanical guess.
