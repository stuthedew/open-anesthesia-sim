---
id: PL-HHCD
title: Cut v0.5.17 from the 20 items finished since v0.5.16
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items, docs/pr-bodies
resource: release-train
added: 2026-09-28
closed: 2026-09-28
pr: 1219
payoff: the 20 items finished since v0.5.16 ship under their own number and stop being re-offered in every session digest
verify: grep -q "^version = \"0.5.17\"" pyproject.toml
---

**Problem.** Cut v0.5.17 from the 20 items finished since v0.5.16

The project owner asked on 2026-09-27 for the release to be cut once another
in-flight session finished, and authorized the cut at the session's
compaction on 2026-09-28. The version is 0.5.17, a patch, on
`ROADMAP.md` § "Versioning decision"'s test: of the twenty items, six reach
the simulator's side (`PL-F08Y`, `PL-HNWX`, `PL-JQY1`, `PL-QW19`, `PL-HGB6`,
`PL-QRBB`) and none changes what a learner can reach, and v0.6.0 through
v0.8.0 are given to milestone sections.

**Cut 2026-09-28, at 20 items**, with `make release VERSION=0.5.17`, from
`main` at `2149e938` (`#1216`). `data/` resolves to `b8477a1` at both ends,
and `core/` moved (`4fd5842` to `0520984`), so the cut re-ran the claim that
every trajectory is bit-identical: 5,040 state vectors sampled once a minute
over 60 minutes at the 0.1 s step - the vaporizer closed at 30 minutes and
cardiac output, fresh gas flow and alveolar ventilation changed at 40 - across
the three agents, nine cardiac outputs and three fresh gas flows, plus one run
per agent from `AgentUptakeSystem.for_agent()` at the profile's own opening
flow, hash identically on the v0.5.16 tag and on this cut. The script was a
one-off and is not kept: it built each run with `_configured_system` from
`tests/reference/test_published_wash_in_and_elimination.py` and hashed the
`repr` of `state_vector()`.

The `ROADMAP.md` row, its `current baseline` mark and the baseline section
are written by hand. v0.5.16's notes take the pointer to `PL-G8TR` (`#1198`),
which merged inside the v0.5.16 tag. `tools/pr_body_check.py` found `#1210`'s
squash commit without its body, recovered into `docs/pr-bodies/1210.md`.
`bin/docket wave` puts Gate 2 at 109 of 191 cleared; v0.5.16 recorded 101 of
190, `PL-TBMX` joined after the freeze, and this release's seven gate entries
account for all but one of the difference, which was not traced. The tag is
the owner's to push from this environment.
