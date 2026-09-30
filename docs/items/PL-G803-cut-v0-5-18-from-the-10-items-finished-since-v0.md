---
id: PL-G803
title: Cut v0.5.18 from the 10 items finished since v0.5.17
status: done
resource: release-train
added: 2026-09-30
closed: 2026-09-30
pr: 1236
verify: grep -q "^version = \"0.5.18\"" pyproject.toml
---

**Problem.** Cut v0.5.18 from the 10 items finished since v0.5.17

**Done 2026-09-30.** `make release VERSION=0.5.18` stamped the ten items and
wrote `docs/releases/v0.5.18.md`; `ROADMAP.md` takes the row, the baseline
mark and the baseline section. No stored number moved (every numeric field
in `src/anesthesia_sim/data/` compared at both ends: only `schema_version`,
2 to 3), and 5,040 state vectors sampled once a minute over 60 minutes across
three agents, nine cardiac outputs and three fresh gas flows, plus each
agent's opening flow, hash identically on v0.5.17 and on this cut. Before
filing, `bin/docket flight` and `list_sessions` showed no other session
holding the release train or cutting, and none of the eight in-flight
branches edits any of the ten items. `make check` passed: 5,672 tests,
100% core coverage. The tag step is `PL-Y65G`.
