# Mutation testing

A mutant is a copy of the simulator's code with one small fault in it, such as
`+` in place of `-` or `<` in place of `<=`. A test kills a mutant when the test
fails on it. A mutant that every test passes has survived, and it points at a
fault that the tests would not catch. This page records how the project runs
mutation testing, what can go wrong with it, and what it has measured.

Mutation testing here is a measurement and not a gate. The project owner chose
to run it on the functions that a pull request changes, rather than to set a
mutation score as a target (project owner, 2026-10-17, ratified, over keeping
the recipe as a one-off record and over a whole-tree score as a target,
`PL-Y1PS`).

A high mutation score does not show that the tests catch a wrong clinical
value. mutmut never changes the data files or the module-level constants, and a
mutant cannot show whether a test's expected value is right.
`.claude/rules/test-oracles.md` says where a simulator test's expected value
must come from, and that rule applies whatever the score.

## Run it

- `make mutate` mutates the functions that the branch changed, compared with
  the default branch, in the modules that mutmut mutates. It prints each
  changed function with the count of its mutants by status, the diff of each
  survivor, and the changed lines that mutmut cannot mutate. A run took about
  five minutes on a four-core container. Half of that time went on finding
  which tests reach which function.
- `make mutate ARGS=--all` mutates every function and prints the kill rate of
  each module. Use it to measure a new baseline.
- `make mutate ARGS="--base origin/main"` compares the branch with a named
  branch instead of the default branch.

`make mutate` runs `tools/diff_mutation.py` through `uv run --group mutation`.
mutmut is pinned to version 3.8.0 in the `mutation` dependency group, so
`uv sync` leaves it out and no test or check needs it. The tool's docstring
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
- **One test is left out.**
  `tests/unit/test_supported_range_edges.py::test_each_guard_admits_only_what_its_functions_compute`
  lists the functions of each module, so inside mutmut it would call mutmut's
  generated copies of them. It is deselected, which drops all 7 of its
  parametrized cases. A survivor in `core/supported_ranges.py`, or in a
  constructor that one of its guards checks, is therefore not evidence of a gap
  until the second tier has run.
- **`strict=` gives noise.** 11 of the 14 equivalent survivors in the
  matrix-exponential group change `strict=` on `zip` or `map`, where the
  lengths are equal by construction. A `# pragma: no mutate` comment on those
  lines would remove them from every later triage.

## Baselines

A kill rate below is killed / (killed + survived). Mutants that timed out or
that no test reaches are left out of it.

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
is then misleading, but no value is wrong.

Mutation testing was one of five methods the audit used. The others were
fault injection, stored-value perturbation, a review of where each test's
expected value came from, and a replay of regression tests against the code
before their fix. Those found the gaps that a mutant cannot show, and
`.claude/rules/test-oracles.md` records what they taught. Running mutation on
the functions that a change touches, and showing the survivors at review, is
how Google runs it (Petrović G, Ivanković M, Fraser G, Just R, "Practical
mutation testing at scale: a view from Google", IEEE Transactions on Software
Engineering 48(10):3900-3912, 2022, https://doi.org/10.1109/TSE.2021.3107634).
