---
id: PL-8ZGY
title: workflow_paths places every path nobody listed on the simulator's side and nothing reports a tracked one, so apparatus files cross the lane boundary unnoticed - 22 items declare docs/resident-instructions.md beside apparatus alone
priority: P1
effort: M
status: ready
classes: defect, infra
feature: parallel-sessions
touches: docket.toml, tools/workflow_paths_check.py, tests/unit/test_workflow_paths_check.py, subprojects/docket/src/docket/trend.py, subprojects/docket/tests/test_trend.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-27
payoff: an apparatus item stops being held out of its lane by a file nobody thought to list, and a new file's side becomes a decision made once
not-delegable: the fix starts with a decision per unplaced path and a choice of which carrier is the source of truth, so no command can prove it before that design round
root-cause-of: PL-JBZK, PL-GVNS, PL-12P8, PL-W40L
generator: live - the store handed it a member today (PL-W40L), and every tracked path no decision places still defaults to the simulator's side with nothing reporting it, so the next unplaced apparatus path is found only when someone happens to notice
misread: Which lane, workflow or product, each tracked path is in
---

**Problem.** workflow_paths places every path nobody listed on the simulator's side and nothing reports a tracked one, so apparatus files cross the lane boundary unnoticed - 22 items declare docs/resident-instructions.md beside apparatus alone

**The mechanism.** `docket.toml`'s `workflow_paths` lists the apparatus side of
the partition `CLAUDE.md` § "Proactive expert review and domain best practices"
draws, and `Item.lane` reads every path it does not list as the simulator's. So
a path's side is a decision only where somebody made one. An apparatus file
nobody listed is on the simulator's side by default, and an item touching it
beside the apparatus it serves reads `crossing`: `docket next workflow` and
`docket next product` both leave it unranked, and the line listing it says it
reaches both halves - the wrong reason, stated as fact.

Decisions are made in two places. `tools/workflow_paths_check.py` decides a
test file under `tests/` by its imports (`PL-JBZK`), and `PL-12P8` held the
support modules there to the half their imports decide - but not all of them:
"a module importing no `anesthesia_sim` sits wherever `workflow_paths` puts it -
the simulator's unless listed", in the check's own docstring. Outside `tests/`,
`tests/unit/test_workflow_paths_check.py` pins single placements through
`Item.lane`: `test_a_tools_script_and_its_own_test_land_in_the_same_lane` (three
`tools/` scripts), `test_the_owners_own_notes_are_apparatus_like_the_workers`
(`docs/maintainer.md`, `docs/worker.md`) and
`test_the_root_conftest_lands_with_the_apparatus_it_configures` (the root
`conftest.py`). That file is the existing per-path decision record, and the fix
can extend it rather than add a `docket.toml` key, which would be one more
hand-kept carrier. Nothing reports a tracked path that neither place decides.

**A second reader of the same default.**
`subprojects/docket/src/docket/trend.py`'s `bucket()` ends in an unconditional
`return SIM_DOCS`, so `bin/docket trend` counts every unlisted path as a product
change: `docs/pr-bodies/` (264 files), `bin/docket` and
`docs/resident-instructions.md` among them. That skews `PL-04KR`'s
apparatus-convergence signal.

**The carriers.** The partition has more than one, each kept by hand:
`workflow_paths`, `.claude/rules/apparatus-standard.md`'s `paths:`, and the
prose lists in `CLAUDE.md` and `.claude/rules/expert-review.md`. No check
compares them against each other: `tools/rules_paths_check.py` checks only that
a rule's globs are anchored and point at something.

**Members** (project owner, 2026-09-27, ratified, over keeping all six members
under the partition-wide misread) - items that exist because a path's lane was
the default rather than a decision:

- `PL-JBZK` (2026-09-05): seven tools tests missing from `workflow_paths`.
- `PL-GVNS` (2026-09-05): `docs/maintainer.md` missing, so `PL-90CJ` ranked as
  product work.
- `PL-12P8` (2026-09-06): the check told `tests/conftest.py` to declare itself
  apparatus.
- `PL-W40L` (2026-09-27): the root `conftest.py` missing.

**Related, not members.**

- `PL-1KTV` (2026-09-06) and `PL-21RC` (2026-09-13, open): in both,
  `workflow_paths` had already placed the path correctly - `.github` and
  `docs/maintainer.md` - and what disagreed was the review-standard lists,
  `apparatus-standard.md`'s `paths:` and the prose in `CLAUDE.md` and
  `expert-review.md`. `PL-21RC` is also already a member of `PL-G424`.
- `PL-3YRT` (`apparatus-standard.md`'s `paths:` never load for the apparatus
  tests) and `PL-4NZ7` (triage asks the generator question only of
  workflow-lane items), both filed in #1203.
- `PL-NB45`, filed the same day as `PL-W40L`: a rule restating the apparatus
  test count is `PL-4FBP`'s and `PL-G424`'s fact, a document sentence and the
  tree fact it restates.

**Live, measured 2026-09-27** through `Item.lane` against the list as
`PL-W40L` leaves it, with the root `conftest.py` listed. Of the store's 337
`crossing` items, these declare no path under `src/` or `tests/` and none of
the list's four recorded absences (`ROADMAP.md`, `docs/releases/`,
`docs/ARCHITECTURE.md`, `README.md`), so each reads `crossing` through the
unplaced paths below and nothing else:

| Unplaced path | Items | Open among them |
| --- | --- | --- |
| `docs/resident-instructions.md` | 22 | `PL-NK5K` (blocked) |
| `docs/MODEL.md` | 11 | `PL-2M9N`, `PL-8LDF` |
| `docs/pr-bodies/` | 5 | none |
| `docs/references/` | 4 | `PL-0SCG`, `PL-Z3V5` |
| `pyproject.toml` | 4 | none |
| `.vscode/extensions.json`, `uv.lock`, `docs/stress-2026-09-25/`, `docs/consultant-brief.md`, `docs/machine-survey.md`, `docs/machine-abstraction.md` | 1 each | none |
| `bin/docket`, `.vscode/settings.json`, `docs/interface-provenance.md`, `.gitattributes`, `.python-version`, `CITATION.cff`, `LICENSE` | 0 | none |

The last row is unplaced too, and no item reads `crossing` through it yet.
`bin/docket` and `.vscode/settings.json` are declared by no item; the other five
are, but never beside apparatus alone.

**What the table counts is declarations, not items held out.** Item-file
history does not support reading its first row as twenty-two items set aside
from both lanes. Nineteen of the 22 closed the day they were added, and the
other three gained the path only in their closing or blocking commits:
`PL-JQVB` in 8df0978e, `PL-384P` in 087fdba7 and `PL-NK5K` in 1f7e8878. (28
items declare the path in all; the table counts the 22 with nothing but
apparatus beside it.) What a table path holds out of a lane today is the two
ready items on `docs/references/`, `PL-0SCG` and `PL-Z3V5`. `docs/MODEL.md` is
correctly the simulator's, per `CLAUDE.md`, and its eleven items reach both
halves on purpose - but it is missing from `docket.toml`'s block of deliberate
absences, so its side too is the default rather than a recorded decision. The
generator is live on `PL-W40L` and on that silent default, not on the size of
any row.

**Not decided here.** Some of those paths are genuinely both sides:
`pyproject.toml` and `uv.lock` define the simulator's package and configure the
tools, and `docs/references/` and the machine documents may be the simulator's.
So the fix is a decision per path, plus whatever stops the next path arriving
undecided. One shape: extend the per-path record in
`tests/unit/test_workflow_paths_check.py` - a placement for each unplaced path,
and an assertion that every tracked path outside `src/` and `tests/` is placed
by `workflow_paths`, a recorded absence or that record - rather than a new
`docket.toml` key.

**Why it matters.** The lane is how two parallel sessions stay off one item,
and under product focus a session given no work picks from one, so an item
neither lane ranks waits for a session that takes the whole queue or is handed
it by name, as `PL-0SCG` and `PL-Z3V5` do today. Nothing reports the
misplacement itself, so each new apparatus file outside what the check and the
pinned tests reach repeats the pattern until someone happens to notice, as
`PL-W40L`'s session did from the root `conftest.py`. And `bin/docket trend`
reads the same default, so the measure meant to show apparatus inflow settling
counts apparatus changes as product.

**Done when.** Every path in the table is placed by a recorded decision - listed
in `workflow_paths`, recorded as the simulator's with its reason as the list's
four deliberate absences are, or pinned in
`tests/unit/test_workflow_paths_check.py` - and a tracked path outside `src/`
and `tests/` that nothing places is reported by `make check`, naming the line
to add, rather than defaulting to the simulator's side in silence. `bin/docket
trend` no longer counts `docs/pr-bodies/`, `bin/docket`,
`docs/resident-instructions.md` or any other path no decision places as a
product change.
