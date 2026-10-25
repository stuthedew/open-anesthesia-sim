---
id: PL-YL5R
title: bin/docket check read PL-JS6P, PL-WM5P and PL-VWXL, all status ready with blocked-by: v0.6.0 after v0.6.0 shipped, as Gate 3 entries waiting on work nothing schedules, so a shipped milestone in blocked-by is not read as cleared and nothing had flagged the stale edge before the freeze
priority: P2
effort: S
status: done
classes: defect
milestone: v0.6.7
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_roadmap.py, subprojects/docket/tests/test_checks.py, subprojects/docket/README.md
added: 2026-10-25
closed: 2026-10-25
pr: 1802
payoff: a blocked-by naming a milestone that has shipped no longer makes a gate entry read as waiting on unscheduled work, and docket check names the stale edge
verify: uv run pytest -q subprojects/docket/tests/test_roadmap.py subprojects/docket/tests/test_checks.py -k shipped
reenters: PL-8QMD
---

**Problem.** bin/docket check read PL-JS6P, PL-WM5P and PL-VWXL, all status ready with blocked-by: v0.6.0 after v0.6.0 shipped, as Gate 3 entries waiting on work nothing schedules, so a shipped milestone in blocked-by is not read as cleared and nothing had flagged the stale edge before the freeze

**Why it matters.** `roadmap.gate_status` walks each gate entry's `blocked-by`
and passes over an item that has closed, but it read a milestone version as
open work outside the gate, even after the version table marked it Completed.
So a stale `blocked-by: v0.6.0` turned three ready entries into "waits on work
nothing schedules", which `docket check` refuses until someone defers the
entry or admits the work. Nothing reported the stale edge itself. The
"ready to promote" advisory reads only `blocked` items, and these were
`ready`.

**Done when.** `gate_status` passes over a milestone the release train records
as shipped, as it passes over a closed item, and `docket check` advises on any
open item whose `blocked-by` still names a shipped milestone, unless the
"ready to promote" advisory already names it. `test_roadmap.py` and
`test_checks.py` each cover the case, with an unshipped milestone as the
contrast.

**Generator check.** An instance of the fact `PL-8QMD`'s head states, a gate
entry's disposition, read through `blocked-by` after that head closed on
2026-10-12. Recorded as `reenters: PL-8QMD`. The one reading of which
milestones shipped is `ReleaseTrain.released`, and both readers now take the
`vX.Y.Z` form from `roadmap.as_blockers`.
