---
id: PL-19M4
title: Mutation testing covers eight display modules that pyproject.toml names by hand, and no Qt-free module added or left out since: app/agent_cost.py, app/compartment_schematic.py, app/bookmarks.py, app/playback.py and app/controller.py build values a learner sees and are in no mutation run, and a hand probe of 14 one-line changes on 2026-11-11 left three uncaught
priority: P1
effort: M
status: ready
classes: defect, safety, test
feature: one-source-of-truth
touches: pyproject.toml, tools/diff_mutation.py, tests/unit/test_diff_mutation.py, docs/mutation-testing.md, tests/unit/test_bookmarks.py, tests/unit/test_chart_frame.py, docs/apparatus.md, ROADMAP.md, .claude/skills/docket/modes/close-out.md, subprojects/docket/README.md
added: 2026-11-11
payoff: a change to any display module that imports no Qt is measured by the mutation check when its item closes, and a new such module is covered without anyone adding it to a list
verify: grep -q 'def test_every_module_outside_the_mutation_run_imports_qt_or_is_named_with_its_reason' tests/unit/test_diff_mutation.py && grep -q 'first step under the rule' docs/mutation-testing.md
---

**Problem.** Mutation testing covers eight display modules that pyproject.toml names by hand, and no Qt-free module added or left out since: app/agent_cost.py, app/compartment_schematic.py, app/bookmarks.py, app/playback.py and app/controller.py build values a learner sees and are in no mutation run, and a hand probe of 14 one-line changes on 2026-11-11 left three uncaught

**What happens.** `[tool.mutmut] only_mutate` in `pyproject.toml` lists `core/*` and eight files under `app/`. `docs/mutation-testing.md` calls those eight "the display modules" and says the mutation run leaves out the Qt widget modules. These modules import no Qt, build a value or a state that a learner sees, and are not in the list: `app/agent_cost.py` (added 2026-11-02), `app/compartment_schematic.py` (added 2026-11-01), `app/bookmarks.py`, `app/playback.py`, `app/controller.py`, `app/display_units.py`, `app/unconditional_set.py`, `app/control_record.py`, `app/compartment_selection.py`, `app/view_registry.py` and every module under `layout/`. A branch that changes one of them passes `bin/docket verify`'s mutation check with nothing measured.

**Evidence, 2026-11-11, at `e084968ac`.** A hand probe made 14 one-line changes, one at a time, and ran the test files that import the changed module with `uv run pytest -q -x -n 4`. Eleven failed a test. Three passed every test:

1. `app/bookmarks.py`, `MacTarget._side_of`: `if reading < height - band:` changed to `<=`. Tests run: `tests/unit/test_bookmarks.py`, `tests/integration/test_controller.py`, `tests/unit/test_chart_frame.py` (453 passed). The docstring says the band includes its edges, and no test places a reading exactly on the lower edge.
2. The same function: `if reading > height + band:` changed to `>=` (453 passed). No test places a reading exactly on the upper edge.
3. `app/controller.py`: `if horizon_s <= reached_s:` changed to `<`, in the method that returns an empty `DrawnWindow`. Tests run: `tests/integration/test_controller.py`, `tests/integration/test_sevo_controller.py`, `tests/unit/test_chart_frame.py`, `tests/unit/test_wash_in.py`, `tests/integration/test_qt_chart.py` (415 passed). This one may make no observable difference; check it against the whole suite before writing a test.

The probe ran neither the whole suite nor mutmut, so it is a sample and not a kill rate.

**Recommendation.** State the rule once and derive the list from it: every module under `app/` and `layout/` that imports neither `PySide6` nor `pyqtgraph` is mutated, and a test fails when a module that meets the rule is missing from `only_mutate`. `app/controller.py`'s tests are in `tests/integration/`, which the mutation run does not use, so decide for that module whether to move its Qt-free tests to `tests/unit/` or to leave it out by name with the reason.

**Why it matters.** `bin/docket verify` refuses a branch while a mutant of a line it changed survives the unit tests, but only in a module that `only_mutate` names. A change to `app/bookmarks.py` or `app/agent_cost.py` therefore closes with that check passing and nothing measured. Both build what a learner reads: which side of a MAC target a reading is on, and what an agent cost. The safety-critical standard asks for boundary tests of such values, and probes 1 and 2 show two boundaries with none.

**Checked 2026-11-11, at `3c57c43b0`.** A script parsed every module under `src/anesthesia_sim/app/` and `layout/` and listed the ones that import neither `PySide6` nor `pyqtgraph`, against `only_mutate`. The fault is as the item says, and wider:

- `app/` holds 37 modules. 12 import Qt. 8 are in `only_mutate`. The other 17 import no Qt and are outside the run: `agent_cost`, `bookmarks`, `compartment_schematic`, `compartment_selection`, `control_record`, `controller`, `currency_code`, `display_units`, `halt_gate`, `playback`, `preferences`, `stylesheets`, `unconditional_set`, `view_contract`, `view_registry`, and two that hold no function, `__init__` and `theme`.
- `layout/` holds 11 modules. None imports Qt, and none is in the run.
- The 15 and 10 modules that hold a function hold 239 and 201 `def` statements. The 8 covered modules hold 176. mutmut mutates fewer than every `def`, so these are upper bounds.
- `app_metadata.py` and `user_files.py`, at the top of the package, were not parsed. The rule below covers them, so check them in the build.
- `app/controller.py` holds 101 of the 239. 13 test files under `tests/unit/` import it by name, and 19 under `tests/integration/`.

**What `PL-R8HY` found, and why it matters here.** `PL-R8HY`, on `origin/claude/keen-carson-mh4oj7`, records why the mutation run's first step is slow. mutmut wraps every function in the files `only_mutate` names. Each call through the wrapper costs about 3.5 microseconds while the first step records it, and the selected unit tests make 218 million such calls, so the step takes about 17 minutes. Each module added to the run adds its calls to that step. So the cost of this item is a number of calls, and it has not been counted yet.

**Design, 2026-11-11.** § "Built and measured" below says what of this plan is built, and § "Left to do" what is not.

1. **Measure before choosing what to name out.** Three counts, all from one ordinary run of the selected unit tests with a `sys.monitoring` call counter, and one listing of mutants:
   - the mutants each added module yields, from the steps mutmut takes before its first test (`LIST_SCRIPT` in `tools/diff_mutation.py` calls them);
   - the calls the selected unit tests make into the added modules, which at 3.5 microseconds each is the time added to the first step;
   - for each unit test file, the functions under `app/` that its tests reach, before and after. The check of a changed test runs every mutant of `anesthesia_sim.app.*` that the changed tests reach, against two versions of the test. Its worst measured case already took 2,186 s, and `bin/docket verify` stops at 2 hours.
2. **State the rule where mutmut reads it.** `only_mutate` becomes globs for `core/`, `app/` and `layout/`, and `do_not_mutate` names each module that imports Qt. A new module that imports no Qt is then covered with no edit. A function in `tools/diff_mutation.py` reads each module's imports and returns the modules whose place in the table disagrees with the rule: a module left out that imports no Qt and has no stated reason, or a module that imports Qt and is not left out. A unit test fails on any, and the tool refuses to run on any, so the gate cannot run on a list that has drifted. The imports are the one home of the fact.
3. **Name a module out only on a measured cost, with the reason beside its name.** `app/controller.py` is the one to decide. Its tests are in `tests/integration/`, which the run leaves out, so every changed line of it would need a unit test that repeats an integration test, or a move of its tests. Decide from the counts: how many of its functions the unit tests reach, and what its calls add to the first step. If it is named out, the reason says what would bring it in, and `PL-1FPR`, which splits `tests/integration/test_controller.py`, is where that would happen.
4. **Keep the check of a changed test affordable.** If the third count shows that the added modules take that check past its limit, compare the added modules as `core/` is compared: only the modules that the changed test file imports by name. Keep the eight modules it covers now as they are, so the change removes nothing that is measured today.
5. **Close the three probes.** Add a test with a reading exactly on each edge of the MAC target band in `tests/unit/test_bookmarks.py`. Run probe 3 against the whole suite, and add a test or record why none can tell the two apart.
6. **File the first whole run over the added modules as its own item**, with `sweep:`, because it takes hours and files what it finds. The gate applies only to changed lines, so the added modules' existing survivors refuse no branch.
7. **Bring `docs/mutation-testing.md` up to date**: "the eight files" in its second section, the rule, what the check of a changed test covers, and the measured first-step time.

`PL-R8HY`'s branch changes `tools/diff_mutation.py`, `docs/mutation-testing.md` and `tests/unit/test_diff_mutation.py` too. Expect to resolve against it, and land the smaller change first.

**Built and measured, 2026-11-11.** On `claude/awesome-mendel-rgje5y`, draft pull request #2129.

- **The rule (steps 2 and 3), commit `bf333d2a0`.** `[tool.mutmut]` keeps no `only_mutate`. `do_not_mutate` names the 12 modules of `app/` that import Qt, and `app/display_units.py`, whose reason is in `[tool.diff_mutation.left_out]`. `rule_disagreements` in `tools/diff_mutation.py` reads each module's imports through `docket.python.imports`, takes the toolkit packages from `tools/import_boundary_check.py`'s entries for `layout/`, and names each departure. `main` refuses on any, and `test_every_module_outside_the_mutation_run_imports_qt_or_is_named_with_its_reason` fails on any.
- **Mutants.** 5,486 before, 11,702 after: `core/` 2,875, `app/` 4,985 (2,611 in the eight modules covered before, 1,074 in `app/controller.py`), `layout/` 3,781, `app_metadata.py` and `user_files.py` 61.
- **Calls, which decide the first step.** One run of the 65 selected test files with a `sys.monitoring` counter: 6.5 million calls into the added `app/` functions (5.5 million into `app/controller.py`), 0.26 million into `layout/`, 1.2 million into the eight covered before. At `PL-R8HY`'s 3.5 microseconds a call, the added modules add about 24 s to a first step of about 17 minutes. So the first step is no reason to leave any module out.
- **`app/controller.py` stays in the run.** The selected unit tests reach 71 of its 77 mutated functions, which hold 1,034 of its 1,074 mutants, so a unit test can be written for a changed line. The brief's claim that its tests are all integration tests was wrong: 13 unit test files import it.
- **`app/display_units.py` is left out.** mutmut 3.8.0 wraps `DisplayUnit.__init__`, `Enum` calls it while the class is being built, and every import of the module raises `KeyError: '_mutmut_orig'`. It holds 3 mutants.
- **Two more tests are deselected**, because each fails on mutmut's copy with no mutant applied: `tests/unit/test_layout_serialization.py::test_whether_a_document_reads_does_not_depend_on_where_its_caller_stands` (the wrapper adds two frames a call) and `tests/unit/test_stylesheets.py::test_the_module_imports_nothing_but_the_theme_and_the_standard_library` (the copy imports the wrapper). With them deselected the other 3,599 selected tests pass with every added module wrapped.
- **The check of a changed test (step 4), same commit.** `named_modules` replaces `core_imports`, so a mutated module outside `app/` is compared where the changed test imports it by name. A changed `layout/` test was not measured before and is now.
- **The three probes (step 5), commit `27c6aedbd`.** Two tests in `tests/unit/test_bookmarks.py` place a reading exactly on each edge of the band. Probe 3 is observable: with `<`, an axis that ends exactly at the reach gets a one-point prediction where `preview_window` promises an empty one. `test_a_preview_on_an_axis_that_ends_at_the_reach_predicts_nothing` in `tests/unit/test_chart_frame.py` fails on it. Each test was run against its fault and fails there.
- **The whole run (step 6)** is `PL-00Y5`, commit `84b5510c5`.
- **Documents (step 7), in part.** `docs/mutation-testing.md` has a new § "Which modules are mutated", the wider by-name comparison and two new pitfalls. `.claude/skills/docket/modes/close-out.md` step 7 and `docs/apparatus.md` name the rule.

**Closing out, 2026-11-11, second sitting.** Commits `89dc27129` to `ffa7613b5` on the same branch.

- **`app/controller.py`'s mutants stay in the check of a changed test (step 1, decided).** The deciding run repeated `PL-D59R`'s heaviest case under the rule: one line added to `_snapshot` in `tests/unit/test_dashboard_frame.py`, at `a3bcc07d9`, with `--verdict --base HEAD` in a scratch worktree. It took 2,510 s against 2,186 s before the rule: 23 minutes for the base run and 19 for the branch run, 60 selected tests, 1,646 mutants compared against 1,322, verdict accept. The copy editor and three short test runs shared the four cores. That is about a third of `bin/docket verify`'s 2-hour limit, so no constant leaves the controller out. `docs/mutation-testing.md` § "What the check of a changed test leaves unmeasured" records it. An earlier run of every `app/` mutant against the whole file was stopped after 22 minutes with 599 of 4,982 mutants left, because no change produces that case. mutmut's own record in it gave the file's tests 892 mutants of `app/controller.py` and 148 of the other added modules.
- **`origin/main` came in twice more.** `6daea3688` (#2103) added no Qt-free module that the table had to name, and the rule's tests passed on it. `b3f44da98` (#2131, `PL-PG0S`) added `--first-step` and CI's `mutation-copy` job, which runs the selected unit tests in mutmut's copy on every pull request that changes more than item files. Two conflicts: the roadmap's count is 162, and in `main` the refusal of a table that departs from the rule comes before `--first-step`.
- **Blind review, one pass, three findings.** F1, should-fix: the check of a changed test grew and nobody had measured it. Fixed by the run above and the paragraph that records it. F2, should-fix: no recorded run shows the first step passing under the rule. See "Left to do". F3, optional: the refusal of a mutated module that imports Qt told the author only to name it in `do_not_mutate`. Fixed in `0711b6564`: it now says to keep the import in a widget module first.
- **Copy editor**, commit `a3bcc07d9`: read 12 passages, rewrote 6, none reverted. Its query was right that the roadmap paragraph said in the present tense what this branch makes false, so the paragraph now speaks of the tree at the freeze.
- **Documents swept so far.** `tools/diff_mutation.py`'s module docstring and `subprojects/docket/README.md` § on `mutation_command` still described the hand list, and are corrected in `89dc27129`. `docs/ARCHITECTURE.md`, `docs/maintainer.md`, `docs/WORKING_NOTES.md`, `README.md` and `docs/MODEL.md` name `pyproject.toml` or the test files for other reasons and need no change.
- **Quality suite so far.** `ruff format --check`, `ruff check` and `mypy` passed before the second merge. The full `pytest` run has not run in this sitting.

**Left to do.**

1. **Record the first step's time.** A run of `anesthesia_sim.app_metadata.*` against all 65 simulator test files started at 06:34 UTC on the tree of `a3bcc07d9`, as `scratchpad/count/first_step.py`, with `first_step.log`, `first_step.err` and `phases.log` beside it. Put its time in `docs/mutation-testing.md` § "Run it", in a sentence that holds the words "first step under the rule", and replace "A run took about five minutes" there. If the container restarted, run `uv run --group mutation python tools/diff_mutation.py --first-step` on the merged tree and record that time; it is the same proof CI's `mutation-copy` job gives.
2. **Close out.** Full `pytest`. `bin/docket set PL-19M4 --status done --closed 2026-11-11`, in one commit with the work, whose last paragraph holds `Blind-review: pass 1: should-fix fixed, should-fix fixed, optional fixed` and `Owner-read: not needed - <why>`: the branch adds three tests and changes no value a learner sees. `bin/docket verify --self PL-19M4`. Write the pull request's title and body, send them through the copy editor (`tools/new_prose.py --draft FILE --kind "pull request"`, then `tools/copy_edit.py`), publish, read them back, ask `bin/docket arm`, mark #2129 ready and arm it. Remove the scratch worktrees `scratchpad/wt` and `scratchpad/wt2` with `git worktree remove --force`, and delete the fallback check-in `trig_01TkfEskdtBP3eEXG5ThtHHq`.

**Done when.**

1. One rule decides which modules the mutation run covers: every module under `src/anesthesia_sim/` is mutated unless it imports `PySide6` or `pyqtgraph`, or is named out with its reason. A unit test fails when `[tool.mutmut]` disagrees with the rule.
2. Each module named out has its reason beside its name, with the count that decided it.
3. A test places a reading exactly on each edge of the MAC target band, and probe 3 has a test or a recorded reason.
4. `docs/mutation-testing.md` states the rule, what the check of a changed test covers, and the measured cost of the first step.
5. An item holds the first whole run over the added modules.

**Generator check.** A one-off under `CLAUDE.md`'s rule that a shared fact has one source of truth. The fact is which modules import no Qt. The import statements hold it, and `only_mutate` copied it by hand. No head's `misread:` line states it: `bin/docket generators --misread`, searched on 2026-11-11 for "list", "module", "import", "hand" and "covers", has no such line.
