---
id: PL-1QX0
title: The mutation run never runs a test against a mutant of a function that runs while the test module is imported, such as a decorator, so it reports such mutants as survivors: six in app/halt_gate.py were killed by an existing unit test run in a fresh process
priority: P3
effort: S
status: done
classes: defect
feature: tests-detect-wrong-values
milestone: v0.6.24
touches: tools/diff_mutation.py, tests/unit/test_diff_mutation.py, docs/mutation-testing.md, docs/apparatus.md
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-11-23
closed: 2026-11-23
pr: 2293
filed-pr: 2281
payoff: a branch that changes a decorator is not refused for mutants that an existing test already catches
tests: tests/unit/test_diff_mutation.py::test_settle_reruns_each_survivor_whole_when_asked, tests/unit/test_diff_mutation.py::test_settle_keeps_a_survivor_whose_files_fail_with_no_mutant, tests/unit/test_diff_mutation.py::test_only_the_run_on_the_changed_functions_reruns_its_survivors_whole
---

**Problem.** The mutation run never runs a test against a mutant of a function that runs while the test module is imported, such as a decorator, so it reports such mutants as survivors: six in app/halt_gate.py were killed by an existing unit test run in a fresh process

**What happens.** mutmut decides which tests to run against a mutant from its stats pass, which records the tests that call each mutated function while they run. A call made while pytest imports a test module belongs to no test, so a function that only runs then, such as a decorator applied to a test module's class, is tied only to the tests that also call it at run time. On the 2026-11-23 whole run at `0117c839` (`PL-00Y5`), `mutants/mutmut-stats.json` tied `x_halt_gate` and `x__positional_capacity` in `app/halt_gate.py` to two tests each: `tests/unit/test_halt_gate.py::test_a_function_that_takes_no_view_is_refused` and `tests/unit/test_agent_cost.py::test_the_test_s_own_factor_agrees_with_gas_man_s_published_constants`. Six mutants of the two functions survived (`halt_gate` 6 and 10, `_positional_capacity` 7, 8, 11 and 12). Each fails `tests/unit/test_halt_gate.py` when that file runs whole in a fresh process with `MUTANT_UNDER_TEST` set, because `test_passes_halt_gate_tells_a_gated_method_from_an_ungated_one` and `test_a_gated_slot_is_handed_only_as_many_arguments_as_it_takes` check what the decorator did to the module's class.

**Why it matters.** A survivor on a changed line refuses `bin/docket verify`'s mutation check. A branch that changes a decorator, or a function that builds a module-level constant, is then asked for a test that already exists, or for a `# pragma: no mutate` on a line that is tested. The kill rates in `docs/mutation-testing.md` § "Baselines" also count these as survivors.

**What to do.** Run each survivor's test files whole in a fresh process, as `settle` in `tools/diff_mutation.py` already does for a mutant whose run raised, and count a failure as a kill once the same files pass with no mutant. In the branch check a run has few survivors, so the cost is small. Check first whether the files that mutmut tied to the function always include the file whose test kills the mutant; here they did, because one test of `tests/unit/test_halt_gate.py` calls `halt_gate` at run time. A decorator whose every call happens at import would be tied to no test at all, and mutmut would report its mutants as having no tests.

**Done when.** `make mutate` on a branch runs each survivor's test files whole in a fresh process with the mutant applied, after the same files pass with no mutant, and counts a failure as a kill. A survivor whose files fail with no mutant applied, or for which mutmut names no test, keeps its status. `docs/mutation-testing.md` § "Read a survivor" says which run does this.

**Generator check.** A one-off. The fact misread is which tests observe a mutated function: mutmut's stats pass records only the calls made while a test runs, and nothing in `tools/diff_mutation.py` stated that an import-time call goes unrecorded. No head's `misread:` names mutmut's test selection. `PL-N3YB`, closed 2026-10-25, also reran test files whole, but its fault was pytest's exit status for a collection error, a different fact.

**Done 2026-11-23.** `settle` in `tools/diff_mutation.py` now takes `survivors`, and the run on a branch's changed functions passes it, so each survivor's test files run whole under the mutant after the same files pass with no mutant applied. `--all` does not pass it: on 2026-11-23 its 788 survivors would have added about 33 minutes to a 63-minute run, by the test durations that mutmut recorded, and the sort of 1,037 survivors and untested mutants found 6 of this kind. The comparison of a changed test with its base version is left as it is, because the gap hides a kill from the base and the branch tests alike. Run on the saved whole run of `c66be832` (`PL-00Y5`'s head), the new `settle` turned all six survivors that this brief names into kills in 38 s, and a seventh, `halt_gate` 3, which that sort had counted as caught by an integration test. `passes_halt_gate` 3, which the sort found equivalent, stayed a survivor. A function that runs only while test modules are imported is tied to no test, so its mutants are reported as having no tests and no file can be rerun for them. None of the 1,037 was of that kind, so no item was filed for it, and `docs/mutation-testing.md` § "Read a survivor" says so. Documents checked: `docs/mutation-testing.md` (§ "Read a survivor", § "Run it" and § "Pitfalls"), `docs/apparatus.md`, `.claude/skills/docket/modes/close-out.md`, `subprojects/docket/README.md`, and the `[tool.mutmut]` comments in `pyproject.toml`. The first two now describe the rerun, and the others say nothing that it changes.
