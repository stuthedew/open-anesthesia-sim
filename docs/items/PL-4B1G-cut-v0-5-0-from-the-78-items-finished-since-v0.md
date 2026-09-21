---
id: PL-4B1G
title: Cut v0.5.0 from the 78 items finished since v0.4.35: the MVP release where a learner can branch a case and compare two runs on one axis, and freeze Gate 2 on the day it ships
priority: P2
effort: M
status: done
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-21
closed: 2026-09-21
payoff: the MVP milestone ships under its own number, the 78 finished items stop being re-offered in every session digest, and Gate 2 is frozen on the day the timeline says rather than by whoever next opens the section
verify: grep -q "^version = \"0.5.0\"" pyproject.toml
---

**Problem.** Cut v0.5.0 from the 78 items finished since v0.4.35: the MVP release where a learner can branch a case and compare two runs on one axis, and freeze Gate 2 on the day it ships

**78 items, 20 Required-scope ids, and those are not the same set.** The notes
in `docs/releases/v0.5.0.md` hold the 78 items finished since `v0.4.35`. The
milestone's own scope is 20 ids, 14 of which had already shipped along the
`v0.4.x` track by the plan rather than by drift - `PL-Y5WR` in v0.4.7,
`PL-T691` and `PL-P1Z3` in v0.4.8, `PL-TCD1` and `PL-1XPX` in v0.4.19,
`PL-1PSX` in v0.4.24, `PL-B9PY`, `PL-J2TD` and `PL-TFX5` in v0.4.25, `PL-RD3B`
and `PL-8PSW` in v0.4.26, `PL-MN4J` in v0.4.28, `PL-LPLD` in v0.4.33 and
`PL-CTD7` in v0.4.35. The six closing here are `PL-VKJW`, `PL-B8MK`,
`PL-TYWQ`, `PL-Z3W6`, `PL-49R8` and `PL-W7H9`.

**`0.5.0` is the number, and both halves of § "Versioning decision"'s test
carry it** - unlike the five patch cuts before it, which said so. The
capability boundary is the milestone's own Goal sentence: a learner can take a
branch and compare two runs on one axis, which "The plan" has called MVP since
the project began and which no release before this one satisfied. The number
is also the one `ROADMAP.md` already gave this milestone, so nothing is
reserved past it that this cut spends: `bin/docket wave`'s `Reserved` line
reads `0.6.0, 0.7.0, 0.8.0, 0.9.0` after the bump, unchanged but for `0.5.0`
leaving it.

**The gate the milestone had to clear ends at 184 of 185.** `PL-WZVZ` is
deferred to Gate 2 by `PL-S5Q9` on § "The cadence" beat 3's terms, which
`PL-Y949` made a legal disposition rather than a fudge; `bin/docket wave`
reported `0 this gate can clear` before the cut, so nothing was left that
working the gate could have closed.

**Gate 2 is frozen in the same commit, which is what the timeline says rather
than an extension of scope.** v0.6.0 was scoped out of turn on 2026-09-16, so
beat 1 of the cadence did not freeze its list; § "The cadence" dates the freeze
to the day the preceding milestone ships, and v0.6.0's own section names the
heading the list goes under. It is recorded at the 170 open debt items the
store held on the day, in five groups: 12 cleared by v0.6.0 itself (the ids its
`Required scope` names), 1 deferred to Gate 3 (`PL-Y04W`, the break-out build
item that "The timeline" gives to v0.7.0, with its hazard recorded as not live
against the tree), and 42 / 103 / 12 in the product lane, the workflow lane and
neither.

**Two entries the `interface-areas` feature and `Required scope` disagree
about.** `bin/docket gate --feature` splits by feature; § "Debt inside the
milestone's own scope" makes `Required scope` the test. `PL-Y04W` and
`PL-NDKC` carry the feature and are not in the scope list, so the feature split
would have put both under "cleared by the milestone itself" and been wrong
about both. They are placed by the scope test instead, and the section says so.

**Outstanding after the merge:** the `v0.5.0` tag. `bin/docket release` refuses
to cut the next release while the previous one is untagged, and no check in the
tree reports the gap.
