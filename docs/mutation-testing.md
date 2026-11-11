# Mutation testing

A mutant is a copy of the simulator's code with one small fault in it, such as
`+` in place of `-` or `<` in place of `<=`. A test kills a mutant when the test
fails on it. A mutant that every test passes has survived, and it points at a
fault that the tests would not catch. This page records how the project runs
mutation testing, what can go wrong with it, and what it has measured.

Mutation testing here is a measurement with one gate. The project owner chose
to run it on the functions that a pull request changes, rather than to set a
mutation score as a target (project owner, 2026-10-17, ratified, over keeping
the recipe as a one-off record and over a whole-tree score as a target,
`PL-Y1PS`). The gate is narrower than a score: `bin/docket verify` refuses a
branch while a mutant of a line it changed survives the unit tests (project
owner, 2026-10-19, ratified, `PL-CZXN`). A survivor on a line the branch did
not change is reported and not counted.

The same check also refuses a branch that weakens a test of what the interface
displays (project owner, 2026-10-24, ratified, `PL-7FPD`). A mutant of the code
cannot show that, because the test is what changed. So for each simulator unit
test file that the branch changes, the check runs the mutants of the display
modules twice: once against the base version of the tests that the branch
changed, and once against the branch's version of the changed files. A mutant
that the base version catches and the branch's version misses refuses the
branch. The display modules are the modules under `app/` that mutmut mutates,
by the rule in § "Which modules are mutated".

The same two runs also take the mutants of each mutated module outside `app/`
that the changed test file imports by name, so a branch that loosens a core
unit test, such as a wider tolerance on a concentration, is refused the same
way (project owner, 2026-10-24, ratified, over leaving core unit tests
unmeasured and over comparing every mutant a changed test reaches, `PL-H57W`).
A module counts when either version of the file imports it with `from
anesthesia_sim.core.x import ...`, `from anesthesia_sim.core import x` or
`import anesthesia_sim.core.x`, inside a function or not. The modules under
`layout/` and the two at the top of the package are compared the same way
(`PL-19M4`).

A high mutation score does not show that the tests catch a wrong clinical
value. mutmut never changes the data files or the module-level constants, and a
mutant cannot show whether a test's expected value is right.
`.claude/rules/test-oracles.md` says where a simulator test's expected value
must come from, and that rule applies whatever the score.

## Which modules are mutated

mutmut mutates every module under `src/`, with two exceptions.

1. **A module that imports Qt**, which means `PySide6` or `pyqtgraph`. It is
   widget code, and its tests are integration tests that mutmut does not run.
2. **A module left out for a stated reason.** `pyproject.toml` gives the
   reason, by the module's path, in `[tool.diff_mutation.left_out]`. The one
   entry on 2026-11-11 is `app/display_units.py`, which mutmut 3.8.0 cannot
   wrap.

No list of the mutated modules is kept, so a new module that imports no Qt is
mutated with no edit to any file. mutmut reads only `[tool.mutmut]`, so that
table's `do_not_mutate` names each module of both kinds. `rule_disagreements`
in `tools/diff_mutation.py` reads every module's imports and compares them
with the table. The tool refuses to run on a table that departs from the rule,
and a unit test fails on one, so a new Qt module that the table does not name
fails `make check`.

Until 2026-11-11 the table listed the mutated modules by hand: `core/` and
eight modules of `app/`. All of `layout/`, 17 modules of `app/` that import no
Qt, and the two modules at the top of the package were outside the run, so a
change to one of them passed the gate with nothing measured (`PL-19M4`). The
rule took the run from 5,486 mutants to 11,702.

## Run it

- `make mutate` mutates the functions that the branch changed, compared with
  the default branch, in the modules that mutmut mutates. It prints each
  changed function with the count of its mutants by status, the diff of each
  survivor, and the changed lines that mutmut cannot mutate. A run took about
  five minutes on a four-core container. Half of that time went on finding
  which tests reach which function.
- `make mutate ARGS=--all` mutates every function and prints the kill rate of
  each module. Use it to measure a new baseline. It is slow: on 2026-10-17 it
  reached 1,058 of 2,498 mutants in about 75 minutes on a four-core container,
  because a mutant that makes a test loop run long holds a worker until its
  time limit.
- `make mutate ARGS="--base origin/main"` compares the branch with a named
  branch instead of the default branch.
- `make mutate ARGS=--first-step` builds mutmut's copy of the tree, runs the
  simulator's unit tests in it with no mutant applied, and stops. It reports
  the test that would stop every mutation run at its first step, and took
  2 min 25 s on a four-core container on 2026-11-11. CI's `mutation-copy` job
  runs it on every pull request that changes more than item files
  (`PL-PG0S`).
- `bin/docket verify` runs the same tool with `--verdict`, which prints the run
  as JSON for its check `the unit tests catch a mutation of each changed line`.
  `docket.toml`'s `mutation_command` names it. A survivor on a changed line
  refuses the audit. Write the test that kills it, or, where no input can tell
  the mutant from the original, mark its line `# pragma: no mutate`, which the
  check prints.
- `--verdict` runs only the mutants that can change it (`PL-88HC`). Before
  mutmut runs, the tool lists the changed functions' mutants and places each
  on its line. A mutant that changes only lines the branch did not change is
  left out, and a note counts it. One that cannot be placed still runs. A
  plain `make mutate` still runs every mutant of each changed function, so a
  reviewer still sees the survivors on the lines the branch left alone.
  Neither shortens the coverage collection at the start of a run.

### What the check of a changed test leaves unmeasured

- **A fault in a module outside `app/` that the test does not import by
  name.** A test that builds a run reaches most of `core/` through the run,
  and all of those mutants would take 9 to 16 minutes for each version of a
  changed test (`PL-7FPD` has the measurements). So only the modules the file
  names run, and a fault the test catches only through another module is not
  measured (`PL-H57W` has the scoped cost). The same applies to a module under
  `layout/`.
- **The Qt widget modules and the integration tests.** mutmut does not mutate
  the Qt modules, such as `simulation_view.py`, and the check runs no
  integration test.
- **The apparatus tests**, which import no simulator code (`PL-LBNN`).
- **A changed fixture or helper outside a test file**, such as a
  `conftest.py`. The base copy holds its base version, but only the changed
  test files are selected, so a branch that changes only a helper compares
  nothing.
- **A fault that a test in an unchanged file still catches.** The branch's run
  takes only the changed test files, so a branch that deletes a test because
  another file already catches the same faults is refused. Running every unit
  test on the branch's side would pass it, at the cost of mutmut's coverage
  pass over the whole unit suite, about five more minutes. Make that change in
  `compare_tests` if the refusal is ever wrong in practice.
- **A test that a new import changes.** The selection treats an import as
  binding a name. So a module whose import changed what an unrelated test in
  the file does would leave that test unselected.
- **A base test that fails on the branch's source** with no mutant applied.
  The branch changed what the test checks, so the check names the file in a
  note and does not compare it.

A changed test selects that test of the base version. So does a changed
helper, constant or import that the test reaches, directly, through another
helper, through a decorator or through the rest of its class. A fixture or a
module-level statement such as a call can reach any test, so a change to one
selects every test. A docstring, a comment, a blank line, a new import or a new
helper selects nothing. The whole file is selected where the file reads its own
names without naming them, as `globals()` does, holds a star import, binds one
name twice, or holds a test class that inherits. A branch that only adds tests
has nothing to compare. The branch run tries the mutants that the base run
caught against the tests the branch changed or added first, and runs only the
ones those miss against the whole files (`PL-D59R`).

Before `PL-D59R`, any changed line outside a test, such as an import or a
helper, selected the whole file. That happened for 187 of the 247 changed
simulator unit-test files in the 200 merges before 2026-10-31, and with the new
rule it happens for 2. On 2026-10-24 the two runs for one changed function in
`tests/unit/test_dashboard_frame.py` took 197 s together, on four otherwise idle
cores, with the display modules' mutants alone. On 2026-10-25, with the core
modules that file imports added, the same kind of change took 911 s, most of it
in the branch run over the whole file (`PL-H57W`). Only `--verdict` makes them, so `make mutate ARGS=--verdict` reproduces
what `bin/docket verify` saw.

On 2026-10-31, with the new rule and on four otherwise idle cores, the whole
`--verdict` run took 498 s on `PL-ZR49`'s merge, where nothing was left to
compare, and 1,699 s on #1864's merge, where the comparison took 12 minutes of
it. A change to a helper that 59 of the 161 tests in
`tests/unit/test_dashboard_frame.py` reach took 2,186 s, all of it the
comparison. Before the new rule, `PL-ZR49`'s branch spent 66 minutes on the
base run alone, and #1864's run stopped at `bin/docket verify`'s 2-hour limit
(`PL-D59R` has both). A change that reaches every test of that file would still
cost about what the whole-file comparison did and could pass the limit, so the
audit would then have no answer. No change to that file in the 200 merges
before 2026-10-31 reached half of its tests.

The rule in § "Which modules are mutated" added 16 modules of `app/` to this
comparison, and `app/controller.py` holds most of their mutants that a display
test reaches: 892 of the 1,040 that the tests of
`tests/unit/test_dashboard_frame.py` reach. On 2026-11-11 the same one-line
change to that helper, which 60 tests now reach, took 2,510 s under the rule.
The base run took 23 minutes and the branch run 19, where they had taken 19.7
and 16.7, and the run compared 1,646 mutants where it had compared 1,322. The
copy editor and three short test runs shared the four cores with it. That is
about a third of the 2-hour limit, so the controller's mutants stay in the comparison
(`PL-19M4`).

`make mutate` runs `tools/diff_mutation.py` through `uv run --group mutation`.
mutmut is pinned to version 3.8.0 in the `mutation` dependency group, so
`uv sync` leaves it out and no test needs it. The tool's docstring
explains the three things that it decides and mutmut's settings cannot: which
tests run, which functions changed, and what a "timeout" really was.
`pyproject.toml`'s `[tool.mutmut]` table says why each mutmut setting is there.

mutmut works in a copy of the tree called `mutants/`, which git ignores. Its
progress goes to `mutants/diff_mutation.log`.

## Read a survivor

Sort each survivor into one of four kinds before you write a test for it. The
279 survivors of the 2026-10-17 audit are the worked example.

1. **Message only.** The mutant changes only the text of an error message or a
   label. 174 of the 279 were this kind. `PL-79PK` holds the tests that pin
   those messages.
2. **Equivalent.** No input can tell the mutant from the original. For example,
   mutmut drops `strict=True` from a `zip` whose inputs have equal lengths by
   construction. 38 were this kind.
3. **Unreachable.** No caller can reach the mutated line. 13 were this kind.
4. **A real gap.** A test could tell the mutant from the original, and none
   does. 54 were this kind. Write the test that kills the mutant. If the gap is
   not in the change under review, file an item for it.

Before you call a survivor a real gap, run it against the whole suite, as the
next section says.

## Second tier: run a survivor against the whole suite

`make mutate` runs only the simulator's unit tests, because the integration and
reference tests run 24-hour simulations. One of those slower tests may still
kill a survivor. In the audit, 8 of the 36 real gaps that were checked this way
were caught outside the unit tests. To check one survivor:

1. Commit your own changes, so that `git status --short` prints nothing under
   `src/`. Step 4 discards every uncommitted change under `src/`.
2. Write the mutant into the source with
   `uv run --group mutation mutmut apply NAME`, where `NAME` is the survivor's
   name from the report. mutmut rewrites the file under `src/` in place.
3. Run the whole suite with
   `set -o pipefail; uv run pytest -q -x -n 2 -p no:cacheprovider tests/unit tests/integration tests/reference`.
4. Put the source back with `git restore src/`.

A failure in step 3 means that a slower test catches the mutant. A pass means
that the mutant survives all three test trees.

## Pitfalls

Each of these was measured on 2026-10-17.

- **mutmut's default fork mode gives false kills.** In fork mode, mutmut runs
  the tests once in a parent process and then forks a child for each mutant.
  Each test module is therefore imported once, before any mutant is applied.
  A test whose expected value was computed at import time from simulator code
  can then kill a mutant that the same real fault would pass. The audit
  reproduced this for two tests in `tests/unit/test_governing_equations.py`,
  whose expected value is the module-level `DELIVERED_FRACTION`. A 1% fault
  present before the import passes them, and the same fault applied after the
  import fails them. About 29 call sites in 13 of the selected test files
  reach simulator code at import time. The `forkserver` settings in
  `[tool.mutmut]` avoid this. mutmut's default warm-up, `collect`, imports the
  test modules before any mutant is applied and brings the problem back, so
  the warm-up is set to `none`.
- **What mutmut calls a timeout often is not one.** mutmut runs a mutant's
  tests by their test ids. When a mutant raises while a test module is being
  imported, or changes a test's parameters and so its id, pytest cannot
  collect the test and stops with exit status 4. mutmut's worker turns that
  into exit status 255, which mutmut reports as a timeout. `make mutate` runs
  the test files of each such mutant again, whole, and reports what they say.
  In a trial on 2026-10-17, all 5 of the mutants that mutmut reported as
  timeouts were killed when their test files ran whole. The audit counted
  about 49 mutants that fork mode killed and forkserver mode reported as
  timeouts, with exit status -24 or 255, and put them down to slow imports.
  Status -24 is a real limit on processor time, but status 255 is the case
  above. So the audit's advice to raise `timeout_constant` is not followed.
- **mutmut keeps old verdicts.** mutmut keeps each verdict until the source of
  the mutated function changes. A test added since the last run would never
  run against a mutant that it now kills, and the old "survived" verdict would
  be reported again. `make mutate` therefore deletes `mutants/` at the start of
  every run.
- **Some code is never mutated.** mutmut 3.8.0 does not mutate the JSON data
  files, module-level constants, dataclass field defaults, type annotations,
  or calls to `len` and `isinstance`. It mutates no decorated function, such as
  a `@property`, except a `@staticmethod` or a `@classmethod`, and it never
  mutates `__new__`, `__setattr__` or `__getattribute__`. Its number operator
  only adds 1, and it has no operator that deletes a statement. Stored values
  and constants need stored-value perturbation instead, which `PL-0Z0F`
  proposes for `core/supported_ranges.py`. `make mutate` says when a changed
  function had no mutants, and it counts the changed lines outside any
  function.
- **"Killed" includes exceptions.** A mutant that only makes the code raise
  counts as killed, even when no assertion checked a value.
- **The whole suite cannot be the first tier.** Finding which tests reach
  which function took 81 minutes for 2,024 tests in one process over the whole
  suite. `tests/unit/test_doc_check.py` also has a test that fails inside
  `mutants/`, because the copy is not a clean git repository. So `make mutate`
  runs only the unit test files that import the simulator, and the slower test
  trees are the second tier.
- **Four tests are left out**, because each fails on mutmut's copy of the code
  with no mutant applied, and mutmut stops when a test does. `[tool.mutmut]
  pytest_add_cli_args_test_selection` deselects them. The first two list the
  functions in the modules of `core/`, and inside mutmut the list also holds
  mutmut's generated copies.
  `tests/unit/test_supported_range_edges.py::test_each_guard_admits_only_what_its_functions_compute`
  would call those copies. It is deselected, which drops all 7 of its
  parametrized cases. A survivor in `core/supported_ranges.py`, or in a
  constructor that one of its guards checks, is therefore not evidence of a gap
  until the second tier has run.
  `tests/unit/test_bare_numbers.py::test_every_bare_number_in_core_is_listed_with_its_reason`
  would find the copies' numbers, which its list does not name. It reads the
  source text, which is the same whichever mutant is running, so it could
  never kill a mutant and leaving it out hides no survivor (`PL-GP8G`).
  `tests/unit/test_layout_serialization.py::test_whether_a_document_reads_does_not_depend_on_where_its_caller_stands`
  reads a layout from 150 frames short of the recursion limit. mutmut's
  wrapper adds two frames to every call of a mutated function, so the reader
  runs out of stack there. A survivor in the depth limit of
  `layout/serialization.py` is therefore not evidence of a gap until the
  second tier has run.
  `tests/unit/test_stylesheets.py::test_the_module_imports_nothing_but_the_theme_and_the_standard_library`
  lists what `app/stylesheets.py` imports, and mutmut's copy of the module
  also imports mutmut's wrapper. It reads the source text too, so leaving it
  out hides no survivor (`PL-19M4`).
- **mutmut cannot wrap an `Enum` that defines `__init__`.** `Enum` calls
  `__init__` for each member while the class is still being built, before the
  table of mutants that mutmut's wrapper reads exists. Every import of the
  module then raises `KeyError: '_mutmut_orig'`, and mutmut stops with `failed
  to collect stats. runner returned 2`. `app/display_units.py` is left out of
  the run for this reason (`PL-19M4`).
- **A unit test that reads a file needs that file in the copy.** mutmut copies
  only what `[tool.mutmut] also_copy` in `pyproject.toml` names. A test that
  reads any other file fails inside `mutants/`, and mutmut then stops with
  `failed to collect stats. runner returned 1` before it runs a mutant.
  `README.md` was added for `tests/unit/test_readme_claims.py` (`PL-GP8G`).
  CI's `mutation-copy` job now fails the pull request that adds such a test,
  so the next session's mutation run does not find it first (`PL-PG0S`).
- **`strict=` gives noise.** 11 of the 14 equivalent survivors in the
  matrix-exponential group change `strict=` on `zip` or `map`, where the
  lengths are equal by construction. A `# pragma: no mutate` comment on those
  lines would remove them from every later triage.

## Baselines

A kill rate below is killed / (killed + survived). Mutants that timed out or
that no test reaches are left out of it.

### 2026-10-18 whole tree, forkserver mode, at `d7c1d74c`

This run is the one `make mutate ARGS=--all` makes: mutmut 3.8.0 in
forkserver mode with no warm-up imports, against the 45 simulator unit test
files that `tools/diff_mutation.py` selects by import (`PL-5N95`). It had 2,489
mutants and tested all of them. 2,237 were killed, 235 survived, 15 timed out
and 2 were killed by a signal, so about 90% were killed. 225 of the kills are
mutants whose test modules failed while importing. `diff_mutation.py` ran
their test files again as whole files, with no mutant applied first, and
counted each as killed only after that run. The run took about three and a
half hours on four cores. A container restart stopped it at 2,435 mutants,
and `mutmut run` in the same `mutants/` directory finished the last 54, since
mutmut keeps each recorded result.

| Module | Killed / (killed + survived) | Rate | Fork mode, 2026-10-17 |
| --- | --- | --- | --- |
| `app/run_series.py` | 12 / 19 | 63% | 63% |
| `core/circuit.py` | 122 / 144 | 85% | 86% |
| `core/agent_simulation_validation.py` | 67 / 79 | 85% | 76% |
| `core/simulation_step.py` | 28 / 33 | 85% | 85% |
| `core/parameters.py` | 299 / 352 | 85% | 88% |
| `core/matrix_exponential.py` | 217 / 243 | 89% | 89% |
| `app/formatting.py` | 202 / 221 (1 killed by a signal) | 91% | 88% |
| `core/concentration.py` | 66 / 72 | 92% | 85% |
| `core/supported_ranges.py` | 143 / 156 (6 timeouts) | 92% | 91% |
| `core/run_definition.py` | 338 / 368 (7 timeouts) | 92% | 92% |
| `core/uptake_system.py` | 204 / 222 | 92% | 91% |
| `core/checked_number.py` | 27 / 29 | 93% | 82% |
| `core/exponential_approach.py` | 14 / 15 | 93% | 93% |
| `core/simulation.py` | 29 / 31 | 94% | 94% |
| `app/chart_time_base.py` | 62 / 66 (2 timeouts, 1 killed by a signal) | 94% | 94% |
| `core/blood.py` | 52 / 55 | 95% | 73% |
| `core/tissue.py` | 53 / 56 | 95% | 78% |
| `core/governing_equations.py` | 141 / 148 | 95% | 95% |
| `core/validation.py` | 39 / 40 | 98% | 100% |
| `core/patient.py` | 81 / 82 | 99% | 92% |
| `app/wash_in.py` | 21 / 21 | 100% | 100% |
| `core/alveolar.py` | 20 / 20 | 100% | 96% |

It differs from the fork-mode table in three ways, so compare the two with
care:

- **The process mode differs.** Fork mode counted some survivors as kills
  (§ "Pitfalls"), so a module's rate can fall in forkserver mode without any
  test getting weaker.
- **The test selection differs.** The audit listed 33 test files by hand. This
  run takes the 45 under `tests/unit/` that import the simulator, so a module
  can gain kills from tests the audit did not run.
- **The code differs.** `b9b3c812` and `d7c1d74c` are a day apart, and the
  mutant counts changed with the code: 2,619 then, 2,489 now. The audit also
  left 180 mutants unchecked, 76 of them in `core/parameters.py` and 35 in
  `core/validation.py`. This run checked every mutant, so those two modules'
  rates now cover mutants that the audit's rates did not.

`core/blood.py` (73% to 95%) and `core/tissue.py` (78% to 95%) moved most.
This run does not measure which of the three causes moved them. Compare a
later whole-tree run with this table, not with the fork-mode one.

### 2026-10-17 audit, fork mode, at `b9b3c812`

The audit ran mutmut 3.8.0 in fork mode over `core/` and the four presentation
modules, against 33 simulator unit test files listed by hand. It had 2,619
mutants. 2,439 were tested and 180 were not checked. Of those tested, 2,147
were killed, 13 timed out and 279 survived, so about 88% were killed.

| Module | Killed / (killed + survived) | Rate |
| --- | --- | --- |
| `app/run_series.py` | 12 / 19 | 63% |
| `core/blood.py` | 52 / 71 | 73% |
| `core/agent_simulation_validation.py` | 78 / 103 | 76% |
| `core/tissue.py` | 67 / 86 | 78% |
| `core/checked_number.py` | 9 / 11 (18 not checked) | 82% |
| `core/simulation_step.py` | 28 / 33 | 85% |
| `core/concentration.py` | 34 / 40 (32 not checked) | 85% |
| `core/circuit.py` | 156 / 181 | 86% |
| `app/formatting.py` | 191 / 216 | 88% |
| `core/parameters.py` | 244 / 276 (76 not checked) | 88% |
| `core/matrix_exponential.py` | 217 / 243 | 89% |
| `core/supported_ranges.py` | 125 / 138 (19 not checked, 5 timeouts) | 91% |
| `core/uptake_system.py` | 200 / 220 | 91% |
| `core/run_definition.py` | 338 / 369 (6 timeouts) | 92% |
| `core/patient.py` | 101 / 110 | 92% |
| `core/exponential_approach.py` | 14 / 15 | 93% |
| `core/simulation.py` | 29 / 31 | 94% |
| `app/chart_time_base.py` | 63 / 67 (2 timeouts) | 94% |
| `core/governing_equations.py` | 141 / 148 | 95% |
| `core/alveolar.py` | 25 / 26 | 96% |
| `app/wash_in.py` | 21 / 21 | 100% |
| `core/validation.py` | 2 / 2 (35 not checked) | 100% |

Of the 54 real gaps, one was a safety gap, `record_change__mutmut_13`, filed as
`PL-ZH1F`. One was of medium consequence, `_propagator_for__mutmut_2`, filed
as `PL-4H4T`. 41 were of low consequence and 11 had none. In the second tier,
36 of the 54 ran against the whole suite. 28 survived all 5,734 tests, and 8
were caught outside the 33 unit test files: 5 by reference tests, 2 only by
constants computed at import time, and 1 by a test added after the run. The
other 18 were not run in the time the audit had. One low gap can be reached
today: `fit_to_run__mutmut_13` widens the fitted time axis from 24 hours to 48
hours on the last step of a run that reaches the 86,400 s limit. The caption
is then misleading, but no value is wrong. A test added on 2026-10-24 now
catches it (`PL-9DF9`).

Mutation testing was one of five methods the audit used. The others were
fault injection, stored-value perturbation, a review of where each test's
expected value came from, and a replay of regression tests against the code
before their fix. Those found the gaps that a mutant cannot show, and
`.claude/rules/test-oracles.md` records what they taught. Running mutation on
the functions that a change touches, and showing the survivors at review, is
how Google runs it (Petrović G, Ivanković M, Fraser G, Just R, "Practical
mutation testing at scale: a view from Google", IEEE Transactions on Software
Engineering 48(10):3900-3912, 2022, https://doi.org/10.1109/TSE.2021.3107634).
