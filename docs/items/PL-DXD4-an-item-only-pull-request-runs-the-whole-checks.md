---
id: PL-DXD4
title: An item-only pull request runs the whole checks job, about 11 minutes with pytest at 9, though only the steps that read the store can change its answer: skip the rest behind docket's own item-only predicate, after auditing the tests that read the real store
priority: P2
effort: M
status: done
classes: infra
feature: ci-cost
touches: .github/workflows/quality.yml, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, conftest.py, docket.toml, tests/unit/test_item_store_guard.py, tests/unit/test_quality_step_order.py, tests/unit/test_main_ci_status.py, tools/main_ci_status.py, tests/unit/test_dead_ends.py, tests/unit/test_doc_check.py, tests/unit/test_docket_gate.py, tests/unit/test_inline_reference.py, tests/unit/test_contrast_check.py, subprojects/docket/tests/test_grep.py, subprojects/docket/tests/test_markdown_reference.py, tools/doc_check.py, docs/apparatus.md
added: 2026-10-17
closed: 2026-10-17
pr: 1511
payoff: an item-only pull request skips the eight-minute test suite, ruff and mypy and runs only the tests that read the store, so a capture reaches main sooner and holds a runner for a fraction of the time, while main's own run stays whole
verify: grep -q 'def test_ci_scope_answers_full_for_a_diff_reaching_past_the_store' subprojects/docket/tests/test_cli.py && grep -q 'def test_a_push_to_main_runs_every_step_it_ran_before' tests/unit/test_quality_step_order.py
---

**Problem.** An item-only pull request runs the whole checks job, about 11 minutes with pytest at 9, though only the steps that read the store can change its answer: skip the rest behind docket's own item-only predicate, after auditing the tests that read the real store

**Measured 2026-10-17.** On `main`, 8 of 58 merges in ISO week 41 and 10 of 55
so far in week 42 changed only `docs/items/` (`git diff-tree` per first-parent
commit). Each such pull request runs the whole `checks` job, about 11 minutes,
of which pytest is about 9 (`PL-H9KW`). Skipping the steps that cannot change
the answer would save roughly 9 minutes per run, on the order of 500
run-minutes a month at current volume: about 9% of `quality`'s minutes. Nobody
waits on these pull requests, since they arm auto-merge, so the gain is minutes
rather than anyone's time. `PL-H9KW` is the larger lever and goes first.

**Reproduced 2026-10-17.** `#1507` changed one item file, and its `checks` run
39062070913 took 10m23s. The pytest step took 8m33s of that. Every other step
the run took is under 30 s, and the slowest of those are the two `doc_check`
runs at 26 s and 21 s.

**Why it matters.** Minutes are free on a public repository, so the cost is
time and runner slots. A capture reaches `main` only when its run ends. If
`main` moves first, `update-armed.yml` merges it into the branch and the whole
job runs again. Each run also holds one of the account's concurrent job slots,
which is what slows parallel sessions once minutes stop being the limit
(`quality.yml`'s note on its floor section).

**Why it is not a few lines of YAML.**

1. **Some tests read the real store.** `tests/unit/test_docket_gate.py` reads
   every item and asserts the current debt gate's dispositions, so a capture
   can fail it. `bin/docket check` enforces the same rule and would keep
   running, so that one is covered, but the blanket premise is false: 36 test
   files open the real checkout, and each must be cleared or kept (a marker
   run in the fast path) before any step is skipped.
2. **A miss turns `main` red, not the pull request.** The `push` run on `main`
   would still run everything, so a wrongly skipped step fails after the
   merge, and red `main` stops every session. Keep `main`'s run whole; that
   roughly halves the saving and is the backstop.
3. [superseded 2026-10-17: `arming.py` holds no item-only predicate; see
   "Point 3, checked at triage" below] **The predicate already exists.** Which branches carry only item files is
   decided in `subprojects/docket/src/docket/arming.py`, where it already
   decides what merges without review. The workflow step asks that code; it
   does not spell `docs/items/` again (`CLAUDE.md` § "A shared fact has one
   source of truth").
4. **Skip steps, not the workflow.** `checks` is the required check. Step-level
   `if:` conditions keep it reporting; a workflow-level `paths` filter leaves a
   required check pending forever (GitHub Docs, "Troubleshooting required
   status checks" § "Handling skipped but required checks"; `PL-NWSK`).

**Point 3, checked at triage 2026-10-17.** `arming.py` decides whether a
branch may arm from `READ_PATHS`. Its `outside_the_store` names the paths a
merge lands outside the store, the tooling and the pull-request records, so it
is a different set from "item files alone". No module answers that question
yet. Two facts it needs are already docket's: the store's directory, from
`docket.toml` (`config.items_dir`), and the paths a branch changed, from
`verify.changed_paths`, which the scoped replay already reads. So the work adds
a `bin/docket` command that reads those two, and the workflow asks the command
rather than spelling `docs/items/`. `arming.py` is not changed.

**The audit, 2026-10-17.** A throwaway pytest plugin put an audit hook on
`open`, directory listings and globs during a full run. It recorded 28 tests in
7 files that read the real store in-process: `test_grep.py`'s
`test_globs_and_recursion_read_the_files_grep_reads`, both markdown-it-py
comparisons (`test_markdown_reference.py` and `test_inline_reference.py`),
`test_contrast_check.py`'s `test_every_known_shortfall_names_an_item_that_exists`,
19 tests in `test_dead_ends.py` (through `dead_ends.known_ids`), three
whole-repository tests and one parametrized case in `test_doc_check.py`, and
`test_docket_gate.py`'s disposition test. Then a scratch clone with every item
file replaced by one unparseable line ran the whole suite. Only
`test_this_repository_is_clean` failed, and 8,582 passed. So no test that
reaches the store through a subprocess changed its result. The 28 are kept
rather than cleared one at a time. A test like the gate-disposition one passes
on an unreadable store and fails on a valid new item, so the corrupted run
cannot clear it.

**Decided at triage.** A first step runs `bin/docket ci-scope --base
origin/<base>` on a pull request and writes `scope=items` or `scope=full` as a
step output. Every step that no item file can change runs unless the answer is
`items`, so a push to `main`, where that step does not run, keeps every step.
On `items` the job skips ruff, mypy, `ignore_check`, the full suite and the
checks whose input holds no item file, and runs those tests through a
`reads_item_store` marker instead. A hook in the root `conftest.py` fails a
test that reads the store without the marker, so the marked set cannot fall
behind the tests.

**Built 2026-10-17.** `bin/docket ci-scope --base REF` answers `items` when
every path the branch changed, committed or not, is under the store, and
`full` otherwise. It reads `verify.changed_paths`, which the scoped replay
reads too. It answers `full` wherever it cannot show item files alone: an empty
diff, a diff it could not read, `--no-git`, or a store outside the repository.

`PL-T9X9` merged while this was built. It split the suite into two jobs,
`checks-part-1` and `checks-part-2`, and made the required `checks` job the
gate over them. So each part asks `ci-scope` before any project command and
passes its answer on as a job output. On `items`, the first part skips ruff,
mypy, `ignore_check.py`, its half of the suite and its coverage upload. The
second part skips its half and its upload, and runs `pytest -n auto -m
reads_item_store` instead. `checks` skips combining and reporting coverage,
but only where both parts answered `items`. A push to `main` runs no scope
step, so it runs every step. `tests/unit/test_quality_step_order.py` evaluates
each step's condition for a push, a `full` answer, no answer, an `items` answer
and parts that disagree. Each of nine altered copies of the workflow failed it.

Every other tool step still runs on `items`, which is less than triage
decided to skip. An in-process audit of each tool step on 2026-10-17 found
which ones read the store. The rest took about 9 seconds together on run
39062070913, and skipping them would rest on that one measurement rather than
on anything about what they are. `fixture_id_check.py` is one of them: its
docstring says `docs/items` "is not scanned", and it stays all the same. The
done-when below is restated to name what is skipped.

The root `conftest.py` registers `reads_item_store` and fails a test, or a
module's collection, that reads the store without it. A read is opening,
listing or globbing under the store, or starting a subprocess whose arguments
name a path in it. The guard's own census of a full run found the same 28
tests as the audit. `test_dead_ends.py` is marked as a whole module, so its
tests that only parse an entry are marked too. A run of the unmarked tests
alone found one more reader, `test_doc_check.py`'s
`test_this_repository_measures_its_own_skill_on_demand`. It reads the store
through `_this_repository()`'s cached analysis whenever it is the first of
that analysis's three tests in its process, and `--part` can make it so. A
second run of the unmarked tests alone, with it marked, passed whole: 8,597
tests. In this container the 40 marked tests took 71 s with `-n auto`, as the
fast path runs them, collection included.

Two runs in a scratch clone checked for tests that reach the store through a
subprocess the guard cannot see. With every item file replaced by one
unparseable line, only `test_this_repository_is_clean` failed, and 8,582 tests
passed. With every item file removed, only the unmarked tests ran. One test in
each of `test_workflow_paths_check.py` and `test_rules_paths_check.py` failed
because the store's directory was gone, and both passed with one item
restored. That run also showed that `tests/unit/test_item_store_guard.py` was
missing from `docket.toml`'s `workflow_paths`, which
`tools/workflow_paths_check.py` cannot see until the file is tracked.

**Where.** `.github/workflows/quality.yml`; `subprojects/docket/src/docket/cli.py`
for the predicate's command; the root `conftest.py` for the marker and its
guard; `tools/doc_check.py`'s `GATE_ONLY` for the step `make check` does not
run.

**Done when.** On a pull request whose diff is only item files, the required
`checks` job reports success while ruff, mypy, `ignore_check.py`, both halves
of the suite and the coverage they feed are skipped. Every other step runs,
including the store-reading ones (`bin/docket check`, `doc_check`,
`dead_ends`, `fixture_id_check` and the scoped verify replay), and the tests
marked `reads_item_store` run in the suite's place. `main`'s `push` run is
unchanged, and a test shows that a diff touching anything outside the store
runs every step. (Restated at the build, because `PL-T9X9` split `checks` into
two parts and a gate, and the build skips fewer steps than triage decided.)

**Generator check.** A one-off: work the owner asked for under `ci-cost`
(2026-10-17), with no misread fact behind it. The job runs every step because
nothing told it which steps an item-only diff can change, and no head's
`misread:` line concerns which steps CI runs (`bin/docket generators
--misread`, 2026-10-17).
