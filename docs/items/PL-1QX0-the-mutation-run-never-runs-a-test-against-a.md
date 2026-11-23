---
id: PL-1QX0
title: The mutation run never runs a test against a mutant of a function that runs while the test module is imported, such as a decorator, so it reports such mutants as survivors: six in app/halt_gate.py were killed by an existing unit test run in a fresh process
status: untriaged
feature: tests-detect-wrong-values
added: 2026-11-23
filed-pr: 2281
---

**Problem.** The mutation run never runs a test against a mutant of a function that runs while the test module is imported, such as a decorator, so it reports such mutants as survivors: six in app/halt_gate.py were killed by an existing unit test run in a fresh process

**What happens.** mutmut decides which tests to run against a mutant from its stats pass, which records the tests that call each mutated function while they run. A call made while pytest imports a test module belongs to no test, so a function that only runs then, such as a decorator applied to a test module's class, is tied only to the tests that also call it at run time. On the 2026-11-23 whole run at `0117c839` (`PL-00Y5`), `mutants/mutmut-stats.json` tied `x_halt_gate` and `x__positional_capacity` in `app/halt_gate.py` to two tests each: `tests/unit/test_halt_gate.py::test_a_function_that_takes_no_view_is_refused` and `tests/unit/test_agent_cost.py::test_the_test_s_own_factor_agrees_with_gas_man_s_published_constants`. Six mutants of the two functions survived (`halt_gate` 6 and 10, `_positional_capacity` 7, 8, 11 and 12). Each fails `tests/unit/test_halt_gate.py` when that file runs whole in a fresh process with `MUTANT_UNDER_TEST` set, because `test_passes_halt_gate_tells_a_gated_method_from_an_ungated_one` and `test_a_gated_slot_is_handed_only_as_many_arguments_as_it_takes` check what the decorator did to the module's class.

**Why it matters.** A survivor on a changed line refuses `bin/docket verify`'s mutation check. A branch that changes a decorator, or a function that builds a module-level constant, is then asked for a test that already exists, or for a `# pragma: no mutate` on a line that is tested. The kill rates in `docs/mutation-testing.md` § "Baselines" also count these as survivors.

**What to do.** Run each survivor's test files whole in a fresh process, as `settle` in `tools/diff_mutation.py` already does for a mutant whose run raised, and count a failure as a kill once the same files pass with no mutant. In the branch check a run has few survivors, so the cost is small. Check first whether the files that mutmut tied to the function always include the file whose test kills the mutant; here they did, because one test of `tests/unit/test_halt_gate.py` calls `halt_gate` at run time. A decorator whose every call happens at import would be tied to no test at all, and mutmut would report its mutants as having no tests.
