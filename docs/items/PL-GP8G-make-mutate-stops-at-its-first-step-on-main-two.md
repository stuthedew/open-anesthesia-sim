---
id: PL-GP8G
title: make mutate stops at its first step on main: two unit tests that landed 2026-11-09 and 2026-11-11 fail inside the mutation copy of the tree
status: untriaged
added: 2026-11-11
---

**Problem.** make mutate stops at its first step on main: two unit tests that landed 2026-11-09 and 2026-11-11 fail inside the mutation copy of the tree

**What happens.** `make mutate` prints `failed to collect stats. runner returned 1` and exits before it tests any mutant, on any branch that holds `origin/main` at `e084968ac`. Found on 2026-11-11 while building `PL-RF2S`. Close-out step 7 needs this run for every item that changes a mutated module, so no such item can list its survivors until this is fixed.

**Cause, two tests.** mutmut first runs the selected unit tests once inside `mutants/`, a copy of the tree that holds mutant copies of each function. Two tests fail there and pass everywhere else:

1. `tests/unit/test_readme_claims.py` reads `README.md` when it is imported (`PL-L9FC`, `#2075`, 2026-11-09). `[tool.mutmut] also_copy` in `pyproject.toml` copies `tools/`, `subprojects/docket/src/` and `docs/`, and not `README.md`, so the import raises `FileNotFoundError`.
2. `tests/unit/test_bare_numbers.py::test_every_bare_number_in_core_is_listed_with_its_reason` lists the functions in `core/` (`PL-LHCL`, `#2099`, 2026-11-11). Under mutmut it also lists the mutant copies, such as `xǁAgentSimulationValidatorǁcheck_agent_accounting__mutmut_1`, and fails on them. `test_each_guard_admits_only_what_its_functions_compute` fails the same way and is already deselected for that reason.

**Checked.** With `README.md` copied into `mutants/` by hand, the first step ran 3,594 tests and only the second test failed. Command, from `mutants/`: `MUTANT_UNDER_TEST=stats PYTHONPATH=src QT_QPA_PLATFORM=offscreen ../.venv/bin/python -m pytest --rootdir=. -q -p no:cacheprovider @selected-tests.txt --deselect tests/unit/test_supported_range_edges.py::test_each_guard_admits_only_what_its_functions_compute -n 8`.

**Suggested fix.** Add `"README.md"` to `also_copy`, and add a `--deselect` for the second test beside the first, with the same comment. Then run `make mutate` to its end on a branch that changes a mutated module.

**Why it landed unseen, to decide in triage.** No check runs the mutation run's first step, so a unit test that cannot run inside `mutants/` merges green. Two did in three days. Whether a check should run that step is a new workflow mechanism, which the generator pause holds, so this item records the question and does not build one.

**Done when.** `make mutate` runs to its end on `origin/main` plus a change to a mutated module, and reports that change's mutants.

