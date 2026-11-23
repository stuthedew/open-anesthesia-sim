---
id: PL-33CG
title: The mutation check of a branch that changes core/ did not finish in an hour, because every core mutant also runs the 30 s generated-run test
priority: P2
effort: S
status: done
classes: session-cost
feature: tests-detect-wrong-values
touches: tools/diff_mutation.py, tests/unit/test_diff_mutation.py, docs/mutation-testing.md, .claude/skills/docket/modes/close-out.md
added: 2026-11-11
closed: 2026-11-23
pr: 2254
payoff: A branch that changes the simulation core can read its full mutation verdict before it closes, instead of checking only the mutants its session picks.
tests: tests/unit/test_diff_mutation.py::test_the_run_script_hands_the_fork_server_each_mutant_s_tests_fastest_first, tests/unit/test_diff_mutation.py::test_settle_leaves_out_the_deselected_tests_in_every_run, tests/unit/test_diff_mutation.py::test_a_rerun_leaves_out_the_tests_it_is_told_to_skip
---

**Problem.** The mutation check of a branch that changes core/ did not finish in an hour, because every core mutant also runs the 30 s generated-run test

**What happened.** On 2026-11-11 `make mutate` ran on the branch of `PL-GJ1W`
part (b), which adds `core/rounding.py` and changes the import of a constant
in nine other simulator modules. The run was stopped at a one-hour limit after
157 mutants, about 23 s for each. mutmut runs against a mutant the unit tests
that reach its function, and `tests/unit/test_generated_runs.py` reaches most
of `core/` and takes about 30 s. `.claude/skills/docket/modes/close-out.md`
gives five to eight minutes for a typical branch and 36 minutes for the
largest batch measured, 340 mutants on 2026-10-24, before that test existed.

**What it cost.** The session could not read the tool's verdict for the
branch. It read the 12 survivors recorded so far with `mutmut results`, fixed
the five in the new module, and ran mutmut on that module alone
(`mutmut run "anesthesia_sim.core.rounding.x_*"`, 35 mutants, all caught).
The mutants of the other changed functions were not run.

**Not decided here.** Whether the generated test is left out of mutation runs,
given a shorter form for them, or kept at this cost. Leaving it out loses the
only test that steps drawn runs. Found while building `PL-GJ1W` part (b).

**Checked 2026-11-22**, at `d4e8200c`. The cost is still there. `tests/unit/test_generated_runs.py` still sets `EXAMPLES = 100`, and the `--deselect` list in `pyproject.toml`'s `[tool.mutmut]` table does not name it, so every mutant of a function it reaches still runs it in full. The test was added on 2026-11-10 by #2100 (`PL-GJ1W`), after the measurements that `.claude/skills/docket/modes/close-out.md` gives.

**Why it matters.** Every branch that changes `core/` must read the mutation tool's verdict before it closes, and that verdict now takes longer than a session can wait. A session that cannot read it does what this one did: it checks only the mutants it chooses, and the rest of the changed code goes without the check that the tests detect a change to it. The cost is paid again on every such branch.

**Done when.** A mutation run of a branch that changes several `core/` modules finishes in about the time `close-out.md` gives for a typical branch, and the run's record says how the generated-run test takes part: left out with its reason, run in a shorter form, or kept with the measured cost. The choice is the session's, because it rests on a measurement of how many mutants the generated test kills that no other unit test kills.

**Generator check.** The misread fact is what a mutation run costs per mutant: mutmut runs every unit test that reaches a mutated function, so one slow unit test multiplies the run by the number of mutants it reaches. No head's `misread:` line states it. `PL-SGBT` (mutants rerun one at a time) and `PL-R8HY` (the slow first step) share the feature but not this mechanism, so this is a one-off.

**Done 2026-11-23.** The cause was the order in which mutmut ran each mutant's tests, more than the generated test itself. mutmut runs a mutant's tests with pytest's `-x`, so the run stops at the first test that fails. In its default `fork` mode, mutmut 3.8.0 sorts a mutant's tests by their measured duration before it runs them (`ForkRunner.submit` in `mutmut/workers/isolation.py`, under the comment "Run fast tests first"). In the `forkserver` mode that `pyproject.toml` chooses, `ForkServerRunner.submit` passes `list(tests)` on unsorted, which is the order of a Python set, and pytest runs node ids in the order it receives them (checked on 2026-11-23 with `-p no:randomly`, as mutmut runs it). So the generated-run test, 19.7 s in mutmut's measured durations, ran before a faster test that would have caught the mutant, on a share of every mutant whose function it reaches. mutmut 3.8.1, read from its wheel on PyPI, and mutmut's main branch on GitHub, read on 2026-11-23, have the same code.

The run script in `tools/diff_mutation.py` now sorts each mutant's tests by mutmut's measured durations, and equal durations by test id, before the fork server receives them. This is the prioritization of Just, Kapfhammer and Schweiggert, "Using Non-Redundant Mutation Operators and Test Suite Prioritization to Achieve Efficient and Scalable Mutation Analysis", ISSRE 2012, § IV.B, read in full from https://homes.cs.washington.edu/~rjust/publ/mutation_test_prio_issre_2012.pdf: the tests are sorted "to ensure that the long-running tests will be executed last". The same section checks that the new order does not break the suite, by running it unmutated in that order and in a random one. This project's unit tests already run in a random order on every run, through pytest-randomly.

**The generated test stays in mutation runs.** Four runs of the 253 mutants of `core/governing_equations.py` and `core/prediction.py`, on four cores, gave the same verdict for every mutant, 233 killed and 20 survived:

| Order of each mutant's tests | Generated test | Time |
| --- | --- | --- |
| As mutmut 3.8.0 passes them on | Kept | 1,037 s |
| As mutmut 3.8.0 passes them on | Left out | 820 s |
| Fastest first | Kept | 581 s |
| Fastest first | Left out | 457 s |

The Papadakis et al. survey defines test reduction as "removing test cases that are somehow redundant, i.e., test cases that when removed from the test suites do not change the mutation score" (§ 5.7 of "Mutation Testing Advances: An Analysis and Survey", read in full from https://mutationtesting.uni.lu/survey.pdf). On this sample, leaving the test out did not change the score. The run that would have counted the mutants only it catches, over all 3,155 mutants of `core/` without it, was stopped by the two-hour limit at 2,337. With the tests in order, keeping it costs 124 s on the sample, about a fifth of the run, because it now runs only on the 20 mutants that every faster test misses. It is also the only test that steps randomly drawn runs. The measurement therefore does not justify removing it.

**On the item's own change.** `make mutate` on `83541c3e` (#2121, the change that added `core/rounding.py`) against its parent, with the tests in order, ran the 232 mutants of its eight changed functions in 985 s. About 5.5 minutes of that was mutmut's first pass, which records which tests reach which function. On 2026-11-11 the same branch, before it merged, was stopped after an hour at 157 mutants. The branch changed before it merged, so the two runs did not hold the same mutants.

**Fixed in place.** When a mutant's pytest run raised, `settle` reran its test files whole, after one run of the same files with no mutant applied. Those runs kept the tests that `[tool.mutmut]` deselects, and each of those fails on mutmut's copy of the code. Run on 2026-11-23 in such a copy, `tests/unit/test_supported_range_edges.py::test_each_guard_admits_only_what_its_functions_compute` failed with no mutant, so on any branch whose raised mutants named that file every raised mutant would have been reported unsettled. Every rerun now passes the same `--deselect` list that mutmut's run uses. In that copy, a run with no mutant of `tests/unit/test_supported_range_edges.py`, `tests/unit/test_simulation_step.py` and `tests/unit/test_bare_numbers.py` exited 1 without the list and 0 with it.

**Not fixed, for whoever reruns this.** mutmut reruns every mutant that a name pattern matches, even one with a recorded result, so a stopped run cannot be resumed by naming the same patterns again. Name only the mutants whose exit code in the `.meta` files is still `null`.

**Docs checked.** `docs/mutation-testing.md` § "Pitfalls" has a new entry on the order of each mutant's tests, and its entry on timeouts now says the reruns leave out the deselected tests. Its count of what the tool decides went from four to five, as did the module docstring of `tools/diff_mutation.py`. § "Run it" keeps its dated timings, which are still true of their dates. `.claude/skills/docket/modes/close-out.md` gives this change's time beside its other measurements. The comments on `RUN_SCRIPT`, `settle` and `_pytest_in_mutants`, and the comment above `pytest_add_cli_args_test_selection` in `pyproject.toml`, were read against the new code. `tools/doc_check.py candidates` also named `docs/apparatus.md` (the line for `diff_mutation.py`, still true), `subprojects/docket/README.md` (the `--verdict` passage, still true), and three lines that use "submit" or "settle" for other things: `docs/apparatus.md` and `docs/maintainer.md` on `model_doc_review.py submit`, and `ROADMAP.md` on a simulation that settles.
