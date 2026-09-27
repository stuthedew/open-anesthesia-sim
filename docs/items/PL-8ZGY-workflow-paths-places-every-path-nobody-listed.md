---
id: PL-8ZGY
title: workflow_paths places every path nobody listed on the simulator's side and nothing reports a tracked one, so apparatus files cross the lane boundary unnoticed - 22 items declare docs/resident-instructions.md beside apparatus alone
priority: P1
effort: M
status: done
classes: defect, infra
feature: parallel-sessions
touches: docket.toml, tools/workflow_paths_check.py, tests/unit/test_workflow_paths_check.py, subprojects/docket/src/docket/trend.py, subprojects/docket/tests/test_trend.py, subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/render.py, subprojects/docket/README.md, docs/ARCHITECTURE.md, docs/items/PL-21RC-docs-maintainer-md-is-apparatus-in-docket-toml.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-27
closed: 2026-09-27
pr: 1218
payoff: an apparatus item stops being held out of its lane by a file nobody thought to list, and a new file's side becomes a decision made once
not-delegable: the fix starts with a decision per unplaced path and a choice of which carrier is the source of truth, so no command can prove it before that design round
root-cause-of: PL-JBZK, PL-GVNS, PL-12P8, PL-W40L
generator: spent - since #1210, tools/workflow_paths_check.py refuses a tracked path neither workflow_paths nor product_paths places, so no tracked path reaches the default unreported; what stays open here, bin/docket trend's reading of paths no longer tracked, hands the store no members
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

**Decision needed.** Two, and both are answered by the section above: (1)
whether the simulator's side is recorded as a `product_paths` list in
`docket.toml`, as recommended, or as per-path pinning tests in
`tests/unit/test_workflow_paths_check.py`; (2) whether the table's placements
stand, in particular the three rows it names as contested - `.gitattributes`
to the workflow side, and `CITATION.cff` and the packaging trio
(`pyproject.toml`, `uv.lock`, `.python-version`) to the product side. An
answer to both starts the build on this branch.

**Decided 2026-09-27: the recommendation as written** (project owner,
2026-09-27, ratified, over recording the simulator's side as per-path pinning
tests in `tests/unit/test_workflow_paths_check.py`, and over the other side
for each of the three contested rows). Built on this branch: `product_paths`
in `docket.toml` with the table's entries and reasons, the six workflow
entries and `.mailmap` removed, the placement rule and its two entry refusals
in `tools/workflow_paths_check.py`, and the tests. `docs/ARCHITECTURE.md`'s
tree entry for the check was rewritten in the docs sweep, which also settles
`PL-93RN`'s sentence; that item's file is on `#1199`'s branch and closes once
it lands. `PL-21RC` carries the six rows the standard's carriers now lack.

**Re-checked against #1199's corrections, 2026-09-27.** The design round
above was argued on the brief as first filed: this branch's predecessor
recovered it from `claude/pl-w40l-kidkwe` (`0207afd7`) before the corrections
landed there (`9d71a82c`), and the merge that brought `#1199` in kept that
copy whole (`82f71f2a`), so `#1210` put the uncorrected brief on `main`.
Restored here as `#1199` filed it, the design round on top. Against each
correction:

- Four members, `PL-1KTV` and `PL-21RC` related: no change. The
  recommendation already left the review-standard carriers to `PL-21RC` as a
  separate question, and the six rows added there stand.
- The misread narrowed to the lane: no change. The recommendation and the
  build work on the lane alone.
- The table as re-measured: every path in it is placed by `#1210`, on the
  side the design round's table gives. `PL-0SCG` and `PL-Z3V5` stay
  `crossing` deliberately: each pairs `docs/references/` with apparatus
  paths, and the workflow side would make 8 product-only items cross to free 4.
- `tests/unit/test_workflow_paths_check.py` as the existing record: the
  recommendation stands. Its three pins guard placements `workflow_paths`
  already lists, so no simulator-side decision was recorded there to extend,
  and `trend.py`'s `bucket()` can read `docket.toml` through `docket.config`
  but not a test module. `product_paths` is the done-when's second form: the
  four deliberate absences, moved from prose to entries with their reasons.
- No pointer to `check_workflow_paths`: no change. `tools/doc_check.py`'s
  function of that name resolves the paths CI steps run; nothing here used it.
- `bucket()` as a second reader: it reads `workflow_paths`, so `#1210`'s six
  entries moved 14,768 changed lines of `bin/docket trend`'s history from
  product to apparatus, the three paths the done-when names among them. But
  it still ends in `return SIM_DOCS`, and with every tracked path placed, what
  reaches that default is the history of paths no longer tracked: 7,209
  lines, 1.3% of all churn (`docs/PUNCH_LIST.md` 3,374, `docs/inbox/` 235,
  `spikes/qt/` 3,590, `v002Gitstuff` 10), and since 2026-08-31 only
  `spikes/qt/`, 0.72%. It grows, since the placement rule's dead-entry refusal
  takes an entry out with its path. So the done-when's last clause is unmet,
  and the design round's cost - no change to `subprojects/docket/` - was wrong.

**Decided 2026-09-27: reopen and build `trend`'s unplaced bucket** (project
owner, 2026-09-27, ratified, over narrowing the done-when's last clause to
tracked paths and closing with the 1.3% recorded). The build:
`docket.config.Config` gains `product_paths`, read from `docket.toml`.
`bucket()` keeps its order, and where `product_paths` is declared returns
`SIM_DOCS` only for a path under it and a new `unplaced` bucket for a path
under neither list; with none declared it keeps today's default, as the
placement rule in `tools/workflow_paths_check.py` declines without one.
`bin/docket trend` says how many lines are unplaced and keeps them out of
both sides' share, as `Period.closed` keeps `crossing` items out of both.
Tests in `subprojects/docket/tests/test_trend.py`, and `docket.toml`'s
`product_paths` comment stops saying docket does not read it. `generator:` now
reads spent: the placement rule closed what handed this head members.

**Built 2026-09-27** (`claude/pl-8zgy-trend-unplaced`), as decided above, with
two choices the decision left open. The unplaced lines are a `+u` column inside
the churn columns, drawn only where `product_paths` is declared, and where it is
not the key says the product side is every path outside `workflow_paths`: a
product column silently counting paths nobody placed is the misread recorded
here. On this repository the column reads the 7,209 lines measured above, in
three periods, and each period's share now leaves them out.
`subprojects/docket/src/docket/render.py` and `subprojects/docket/README.md`
joined `touches`.
