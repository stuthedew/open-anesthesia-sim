---
id: PL-NZ0R
title: The mutation-copy CI job runs the tests in mutmut's copy without mutmut's own pytest plugin, so a fault in that plugin stops every mutation run while the job passes, as PL-LR03's did for a day
priority: P2
effort: S
status: done
classes: defect
feature: tests-detect-wrong-values
touches: .github/workflows/quality.yml, tools/diff_mutation.py, tests/unit/test_diff_mutation.py, tools/doc_check.py, docs/mutation-testing.md
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it: a broken mutation run stops a close-out with an error rather than passing it, and the release waits only on the owner's test drive (triage 2026-11-28)
added: 2026-11-28
closed: 2026-11-28
pr: 2366
filed-pr: 2346
payoff: a pytest or mutmut upgrade that breaks mutation runs fails the pull request that brings it, instead of stopping every close-out after it merges
tests: tests/unit/test_diff_mutation.py::test_sample_run_passes_when_a_mutant_of_the_function_is_killed, tests/unit/test_diff_mutation.py::test_sample_run_fails_when_mutmut_stops_as_it_did_under_a_broken_plugin, tests/unit/test_diff_mutation.py::test_sample_run_fails_when_no_mutant_of_the_function_was_killed, tests/unit/test_diff_mutation.py::test_sample_run_fails_when_the_results_list_no_mutant_of_the_function, tests/unit/test_diff_mutation.py::test_sample_run_refuses_a_function_that_is_not_in_its_file, tests/unit/test_diff_mutation.py::test_the_sample_function_is_in_its_file_and_its_tests_exist
---

**Problem.** The mutation-copy CI job runs the tests in mutmut's copy without mutmut's own pytest plugin, so a fault in that plugin stops every mutation run while the job passes, as PL-LR03's did for a day

**Why it matters.** `bin/docket verify --self` runs a mutation check at every close-out of simulator code, and it rejects a branch when the check gives no answer. On 2026-11-27 a pytest upgrade broke mutmut's own pytest plugin (`PL-LR03`). Every mutation run then stopped before its first mutant, and for about a day no close-out could pass. All that time the `mutation-copy` job, whose purpose is to catch a broken mutation run before it reaches `main`, passed on every pull request. The plugin is the part that a pytest or mutmut upgrade reaches, and it is the part the job leaves out.

**Reproduced 2026-11-28.** The `mutation-copy` job in `.github/workflows/quality.yml` runs only `uv run --locked --group mutation python tools/diff_mutation.py --first-step`. The docstring of `first_step` in `tools/diff_mutation.py` says that it leaves out mutmut's record of which functions each test calls, which took about 19 minutes on 2026-11-11, and that a fault in the plugin that keeps the record passes there.

**Approach.** In the same job, run the plugin's record over a small fixed set of tests, enough to pass through each of its hooks, such as `pytest_runtest_teardown`. One test file takes seconds, where the full record takes 19 minutes. Running the full record only on a pull request that changes pytest or mutmut in `uv.lock` was weighed and is weaker: it misses a plugin fault from any other cause, such as a change to `pyproject.toml`'s `[tool.mutmut]`.

**Done when.** The `mutation-copy` job runs mutmut's pytest plugin over at least one test, so that a fault like `PL-LR03`'s fails the job. The job takes no more than one minute longer than it did on 2026-11-28, and the run that shows both is written in this brief.

**Generator check.** A one-off. The job leaves the plugin out on purpose, to save time, and nothing else runs the plugin before a close-out does. No head's `misread:` names what a passing CI job proves about the step it stands in for.

**Route taken, 2026-11-28.** The job's new last step, `tools/diff_mutation.py --sample-run`, runs mutmut the whole way on one function, `exponential_approach_in_time_constants` in `core/exponential_approach.py`, against its own unit test file. It goes through the same `run` and `statuses` that `--verdict` uses, and fails unless at least one mutant is killed. That covers more than the plugin's record the approach above names: it also runs each mutant's tests and reads the results, which `--first-step` leaves out too. mutmut marks a mutant killed only when its plugin recorded a test calling the function, the mutant was applied, and the test failed on it, so one killed mutant shows every part worked. StrykerJS documents the same kind of check for CI, its `dryRunOnly` option: "Execute the initial test run only without doing actual mutation testing", which "can be used to test that StrykerJS can run your test setup. This can be useful, for example, in CI pipelines" (https://stryker-mutator.io/docs/stryker-js/configuration/, read 2026-11-28). A whole run on one function was chosen over a dry run because it costs a few seconds more and also checks the mutant runs.

**Done 2026-11-28.** Two CI runs on pull request #2366 show both halves of the Done-when.

1. Run 46137108523, head `314b54db`: the new step took 6 seconds on the `ubuntu-24.04-arm` runner and printed "12 killed, 1 survived". The whole `mutation-copy` job took 2 min 21 s, against 2 min 16 s for the same job in run 46134956311 on pull request #2365 that morning.
2. Run 46137889109, head `8c28fb54`, with mutmut 3.8.0 pinned again for that one run: the first step passed, 4,297 tests in mutmut's copy, and the new step failed with "mutmut exited 1 ... failed to collect stats. runner returned 1", the failure `PL-LR03` describes. The next commit put 3.8.1 back.

In this container the same fault, put into mutmut 3.8.1's plugin by hand as `item._nodeid`, made `make mutate ARGS=--sample-run` exit 1 the same way.

**Documents checked.** `docs/mutation-testing.md`, which now lists `--sample-run` beside `--first-step`; the comment above the `mutation-copy` job in `.github/workflows/quality.yml`; the module docstring and `first_step` docstring of `tools/diff_mutation.py`; the `tools/diff_mutation.py --first-step` entry in `tools/doc_check.py`, beside which the new mode's entry was added; and the `mutate` target's comment in `Makefile`, which still holds.
