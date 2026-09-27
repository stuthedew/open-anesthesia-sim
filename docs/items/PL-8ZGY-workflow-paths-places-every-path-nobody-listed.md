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
| `docs/pr-bodies/` | 5 | none |
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

**Design round, 2026-09-27, awaiting the project owner** (branch
`claude/cool-meitner-pjnueb`, `#1210` as a draft). Two decisions; the second
is a table. Both were counted before they were argued: a script ran every
item's `touches` through `Item.lane` against `workflow_paths` as `#1199` leaves
it, once as it stands and once with the path in question listed, and recorded
what the item's *other* paths say - all apparatus (w), all product (p), mixed,
or nothing else declared.

**1. Which carrier records the simulator's side.**

**Recommendation: a `product_paths` list in `docket.toml` beside
`workflow_paths`, each entry with its reason as a comment, and the pinning
tests kept as the end-to-end guard rather than made the record.** A pinning
test can guard a placement - assert through `Item.lane` that an item touching
only that path lands where the decision put it - but it cannot enumerate the
placed set, and "unplaced" is a question about the set. The moment the tests
hold a tuple to enumerate, that tuple is the record, and the only question left
is which file holds it: the file that defines the boundary and already carries
the four deliberate absences as prose, or a test module nobody opens to ask
which side a path is on. The check is also a standard-library tool that runs
from a bare checkout and a hook and already parses `docket.toml`; a record in
a test module reaches it only through pytest. Cost: one key in `docket.toml`
the docket package does not read. `docket.config.load` reads keys by name and
ignores the rest, probed 2026-09-27 with the key present, so no change to
`subprojects/docket/` and the comment says who reads it. `Item.lane` is
unchanged: a path not yet in the tree stays product by default until it lands,
and the check names it then. Under the pause on new mechanisms this is
generator work - `PL-8ZGY` is the live head - so it needs no lift.

**The check**, one rule added to `tools/workflow_paths_check.py`, which `make
check` already runs: for every tracked file (`git ls-files`) outside `tests/`,
whose files the import rule and `PL-12P8`'s support-module rule already decide,
the shortest ancestor no entry of either list reaches into must itself be an
entry of one list. Otherwise refuse, naming the path and both lines that would
place it, since which list is the author's judgment and the tool decides only
that nobody made it. Two more refusals of the same kind: an entry both lists
cover, and an entry that resolves to nothing in the tree - which `.mailmap` in
`workflow_paths` is today; no file of that name has ever been tracked. One
parametrized test asserts through `Item.lane`, for every entry of both lists,
that an item touching only that entry lands on its side; the three existing
pins stay. `tests` is deliberately in neither list, and the rule says so where
it exempts it.

**2. A decision per unplaced path.** Every tracked path outside `src/` and
`tests/` that no entry covers, with the count. `bin/docket` and
`docs/resident-instructions.md` go to the workflow side; `docs/MODEL.md` to
the product side, where `CLAUDE.md` already puts it in words.

| Path | Side | Why | items / open / w / p |
| --- | --- | --- | --- |
| `docs/resident-instructions.md` | workflow | the ledger of the resident set, addressed to sessions as `docs/worker.md` is; 27 of 28 items cross today and 22 become `workflow` | 28 / 2 / 21 / 0 |
| `docs/pr-bodies` | workflow | the pull-request record `tools/pr_body_check.py` writes; 7 of 10 become `workflow` | 10 / 1 / 5 / 0 |
| `bin` | workflow | the docket launcher; no item has ever declared it | 0 / 0 / 0 / 0 |
| `.vscode` | workflow | editor settings for working the repository | 1 / 0 / 1 / 0 |
| `.gitattributes` | workflow | git plumbing beside `.gitignore`, which is listed; its one item (`PL-JX2T`) concerned a stray branch and pairs it with product paths, so kind decides over that one closed count | 1 / 0 / 0 / 1 |
| `docs/stress-2026-09-25` | workflow | `PL-P0FP`'s apparatus stress-test evidence | 1 / 0 / 1 / 0 |
| `.mailmap` | remove | listed, never in the tree | - |
| `src`, `docs/MODEL.md`, `README.md` | product | `CLAUDE.md`'s own enumeration of the simulator, recorded as data | 247 / 42 / 11 / 156 for MODEL.md; 41 / 7 / 4 / 12 for README |
| `ROADMAP.md`, `docs/releases`, `docs/ARCHITECTURE.md` | product | the recorded absences, moved from prose to entries with their reasons kept; the apparatus-only counts (90, 4, 40) are `PL-KRGY`'s question, not this item's | 244 / 23 / 90 / 37; 57 / 1 / 4 / 7; 120 / 18 / 40 / 26 |
| `docs/references` | product | the source register behind `docs/MODEL.md`'s provenance, which `citing-sources.md` scopes with it; the 4 apparatus-paired items stay `crossing`, honestly | 22 / 8 / 4 / 8 |
| `docs/consultant-brief.md`, `docs/interface-provenance.md`, `docs/machine-abstraction.md`, `docs/machine-survey.md` | product | the simulator's design records; every item pairing one with a side pairs it with product | 3 / 1; 7 / 1; 8 / 4; 8 / 2 - w 0 in all four |
| `LICENSE`, `CITATION.cff` | product | for a reader or citer of the simulator, as `README.md` is; both `CITATION.cff` items were about making the simulator citable | 1 / 0 / 0 / 1; 2 / 0 / 0 / 0 |
| `pyproject.toml`, `uv.lock`, `.python-version` | product | genuinely both, so the count decides: 8 items pair `pyproject.toml` only with product paths against 3 only with apparatus, and `uv.lock` 6 against 0. The cost is that a tool's configuration inside `pyproject.toml` reads `product`; `PL-M3YJ` (mypy's `warn_unused_configs`) is the one open instance | 72 / 1 / 3 / 8; 55 / 0 / 0 / 6; 1 / 0 / mixed |

The three rows the count and the kind do not settle the same way, or where
the count is thin, are `.gitattributes`, `CITATION.cff` and the packaging
trio; the rest are uncontested. Placing a document on the workflow side is a
lane fact only: whether `.claude/rules/apparatus-standard.md`'s `paths:` and
`CLAUDE.md`'s enumeration follow is `PL-21RC`'s question, per `PL-1KTV`'s
settled distinction, and that item's table gains these rows when this one is
built. Paths items name that are not in the tree - `spikes/`, `assets/`,
`docs/workflow.md`, `docs/ci-failures.csv` - are untouched by the check until
they land.
