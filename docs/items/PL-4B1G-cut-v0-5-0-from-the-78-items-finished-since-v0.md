---
id: PL-4B1G
title: Cut v0.5.0 from the 78 items finished since v0.4.35: the MVP release where a learner can branch a case and compare two runs on one axis, and freeze Gate 2 on the day it ships
priority: P2
effort: M
status: done
classes: housekeeping
feature: release-process
milestone: v0.5.1
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-21
closed: 2026-09-21
pr: 850
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

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.0 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> A case runs, a time bookmark or MAC target stops it on the step that crosses it, the run forks where it stopped, a setting is changed on the branch, and both runs are drawn on one time axis with every curve, readout, banner and legend entry attributable to the run that produced it - which is "The plan"'s MVP sentence, *a learner can run, branch, and compare a case*, satisfied. Seventy-eight items since v0.4.35, and twenty Required-scope ids, which are not the same set: fourteen of the twenty had already shipped along the `v0.4.x` track by the plan rather than by drift, and **six close here**. `PL-VKJW` is the entry the milestone was missing and that nothing made visible as missing - every part of a branch had shipped since v0.4.25 and none of it was reachable, because nothing in `src/` constructed a `BranchedCase` and `SimulationView` froze its run set at construction, so the milestone could have closed with every other entry `done` and a learner still unable to branch (`PL-XJ37`, project owner, 2026-09-20). A second fork is refused while a comparison is shown, and both agent selectors lock while two runs are drawn (`PL-QRD1`), because the shared MAC axis refuses a mismatched pair only after the controller has switched. **`PL-B8MK` takes the route that costs the trunk nothing**: the obvious way to make a bookmark forkable is to record a keyframe where the run halts, which moves the trunk's own later answers away from what the case would have said unmarked - marking a run would change the run - so the branch opens at the keyframe *before* the mark instead (`SimulationController.resumed_at_halt`, `BranchedCase.fork_at_halt`, `RunDefinition.segment_at`), propagating from the same keyframe its parent does with no keyframe recorded anywhere. `PL-TYWQ` exposes it as a separate transient control (project owner, 2026-09-21, ratified, over a single list that grows a row while the run is halted), which is the honest shape for a branch point that exists only while the run stands on the halt. `PL-Z3W6` discharges the milestone's central claim as a test rather than an argument - a branch reproduces its parent element-wise at every sampled point up to the branch point, at the arithmetic and at the columns both - and `PL-W7H9` states in `docs/MODEL.md` (+417/-14) and `docs/ARCHITECTURE.md` (+225/-57) what a comparison asserts and does not, since two runs on one axis invite a reader to attribute every visible difference to the change they made. `PL-49R8` is the same discipline pointed at the code: a path-scoped rule against re-introducing a sample store, the one change that would quietly restore `PL-011`'s unbounded growth debt. **Nothing computational moved**, by tree object: `src/anesthesia_sim/data/` resolves to `ab3499f` at both ends, so no parameter, constant or stored scientific value changed; `core/` moves `0c8e708` to `ca5a354` in exactly one file, `core/run_definition.py` (+37/-4, a `segment_at` query and three docstrings), touching no equation, coefficient, numerical method or solver step; `app/` moves `87baee9` to `01bc2d9`, eight files, +2,138/-220, and is where the release lives. **`tests/reference/` moves and no published expected value moves with it** - `5b43d4b` to `a184830`, the whole of it `test_canonical_evaluation.py` (+225/-20), `PL-Z3W6`'s assertion - so the v0.0.2 circuit, v0.1.0 sevoflurane and v0.2.0 multi-agent reference tests are unchanged by tree identity and passing at the same numbers. **Gate 1 ends at 184 cleared and one deferred**: `PL-WZVZ` goes to Gate 2 by `PL-S5Q9` on § "The cadence" beat 3's terms, which `PL-Y949` made legal rather than a fudge by giving a frozen-list entry a third disposition stated once in the cadence instead of in each milestone's own bullet, and `PL-0H5D` records its holding condition in a field rather than in prose `blocked-by` cannot express. Gate 2 is frozen under v0.6.0 with this release. Thirteen features complete, the rest of them apparatus: the cut now writes the pull request numbers its notes cite and the 128 bullets across 22 releases that shipped without one are repaired (`PL-W7WL`, `PL-WXX8`); `model.FIELD_RE`'s line-at-a-time front-matter read is the one regex behind three item-corruption defects, measured deleting nine of ten `reason` lines with exit 0 (`PL-9HD1`); `bin/docket stranded` learned to report a section appended to an item `main` already holds, recovering eight items and a ratified decision from five branches nobody would merge; and the 150k handoff budget is re-anchored to spend since baseline, read live from the session transcript (`PL-W80S`, `PL-BZVY`).
