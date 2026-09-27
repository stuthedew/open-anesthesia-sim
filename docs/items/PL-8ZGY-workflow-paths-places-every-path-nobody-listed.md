---
id: PL-8ZGY
title: workflow_paths places every path nobody listed on the simulator's side and only tests/ is checked, so apparatus files cross the lane boundary unnoticed - 22 items were set aside from both lanes by docs/resident-instructions.md alone
priority: P1
effort: M
status: ready
classes: defect, infra
feature: parallel-sessions
touches: docket.toml, tools/workflow_paths_check.py, tests/unit/test_workflow_paths_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-27
payoff: an apparatus item stops being held out of its lane by a file nobody thought to list, and a new file's side becomes a decision made once
not-delegable: the fix starts with a decision per unplaced path and a choice of which carrier is the source of truth, so no command can prove it before that design round
root-cause-of: PL-JBZK, PL-GVNS, PL-12P8, PL-1KTV, PL-21RC, PL-W40L
generator: live - the store handed it a member today (PL-W40L), and docs/resident-instructions.md set 22 items aside from both lanes with none ever filed, so the next unplaced apparatus path is found only when someone happens to notice
misread: Which half, apparatus or simulator, a path is in where no carrier of the partition has placed it
---

**Problem.** workflow_paths places every path nobody listed on the simulator's side and only tests/ is checked, so apparatus files cross the lane boundary unnoticed - 22 items were set aside from both lanes by docs/resident-instructions.md alone

**The mechanism.** `docket.toml`'s `workflow_paths` lists the apparatus side of
the partition `CLAUDE.md` § "Proactive expert review and domain best practices"
draws, and `Item.lane` reads every path it does not list as the simulator's. So
a path's side is a decision only where somebody made one. An apparatus file
nobody listed is on the simulator's side by default, and an item touching it
beside the apparatus it serves reads `crossing`: `docket next workflow` and
`docket next product` both leave it unranked, and the line listing it says it
reaches both halves - the wrong reason, stated as fact.
`tools/workflow_paths_check.py` closed this for test files under `tests/`,
whose imports decide their side (`PL-JBZK`), and `PL-12P8` for the support
modules there. Nothing asks the question of any other path. The partition also
has more than one carrier, each kept by hand: `workflow_paths`,
`.claude/rules/apparatus-standard.md`'s `paths:`, and the prose lists in
`CLAUDE.md` and `.claude/rules/expert-review.md`.

**Members** - items that exist because a carrier put a path on the wrong side:

- `PL-JBZK` (2026-09-05): seven tools tests missing from `workflow_paths`.
- `PL-GVNS` (2026-09-05): `docs/maintainer.md` missing, so `PL-90CJ` ranked as
  product work.
- `PL-12P8` (2026-09-06): the check told `tests/conftest.py` to declare itself
  apparatus.
- `PL-1KTV` (2026-09-06): `.github` in `workflow_paths` but not in
  `apparatus-standard.md`'s `paths:`.
- `PL-21RC` (2026-09-13, open): `docs/maintainer.md` in `workflow_paths` but in
  none of the other carriers.
- `PL-W40L` (2026-09-27): the root `conftest.py` missing.

`PL-NB45`, filed the same day as `PL-W40L`, is not one: a rule restating the
apparatus test count is `PL-4FBP`'s and `PL-G424`'s fact, a document sentence
and the tree fact it restates.

**Live, measured 2026-09-27** through `Item.lane` against the list as
`PL-12P8` leaves it. Of the store's 337 `crossing` items, these cross only
because of a path outside `src/`, `tests/` and the list's four recorded
absences - no simulator file in them at all:

| Unplaced path | Items | Open among them |
| --- | --- | --- |
| `docs/resident-instructions.md` | 22 | `PL-NK5K` (blocked) |
| `docs/pr-bodies/` | 6 | none |
| `docs/references/` | 4 | `PL-0SCG`, `PL-Z3V5` |
| `pyproject.toml` | 4 | none |
| `conftest.py` | 2 | none; `PL-W40L` lists it |
| `.vscode/`, `uv.lock`, `spikes/qt/`, `docs/stress-2026-09-25/`, `docs/consultant-brief.md`, `docs/machine-survey.md`, `docs/machine-abstraction.md` | 1 or 2 each | none |

No item was ever filed for `docs/resident-instructions.md`, which is addressed
to a participant in the build as `docs/worker.md` and `docs/maintainer.md` are.
Twenty-two items were set aside from both lanes by it and nothing said so. That
silence is the defect, more than any one missing entry.

**Not decided here.** Some of those paths are genuinely both sides:
`pyproject.toml` and `uv.lock` define the simulator's package and configure the
tools, and `docs/references/` and the `spikes/` and machine documents may be the
simulator's. So the fix is a decision per path, plus whatever stops the next
path arriving undecided. One shape: declare the simulator's non-`src/`,
non-`tests/` paths beside `workflow_paths`, and have `make check` refuse a
tracked path under neither, printing the line to add, as
`tools/workflow_paths_check.py` already does for tests. Check first what
`tools/rules_paths_check.py` and `tools/doc_check.py`'s `check_workflow_paths`
already compare, so the fix extends a carrier's check rather than adding a
fourth carrier.

**Why it matters.** The lane is how two parallel sessions stay off one item,
and under product focus a session given no work picks from one, so an item
neither lane ranks waits for a session that takes the whole queue or is handed
it by name. Nothing reports the misplacement itself: the list's check reads
`tests/` alone, so each new apparatus file outside it repeats the pattern until
someone happens to notice, as `PL-W40L`'s session did from the root
`conftest.py`. The table is that silence counted.

**Done when.** Every path in the table is placed by a recorded decision - listed
in `workflow_paths`, or recorded as the simulator's with its reason, as the
list's four deliberate absences already are - and a tracked path outside
`src/` and `tests/` that nothing places is reported by `make check`, naming the
line to add, rather than defaulting to the simulator's side in silence.
