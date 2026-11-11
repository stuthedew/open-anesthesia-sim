---
id: PL-GP8G
title: make mutate stops at its first step on main: two unit tests that landed 2026-11-09 and 2026-11-11 fail inside the mutation copy of the tree
priority: P2
effort: S
status: done
classes: defect
touches: pyproject.toml, docs/mutation-testing.md
added: 2026-11-11
closed: 2026-11-11
pr: 2124
payoff: a session that changes a function in core/ or a mutated display module learns which of its mutants the unit tests miss, where the run now stops before it tests any
verify: grep -qF 'tests/unit/test_bare_numbers.py::test_every_bare_number_in_core_is_listed_with_its_reason' pyproject.toml && grep -qF '"docs/", "README.md"]' pyproject.toml
---

**Problem.** make mutate stops at its first step on main: two unit tests that landed 2026-11-09 and 2026-11-11 fail inside the mutation copy of the tree

**What happens.** `make mutate` prints `failed to collect stats. runner returned 1` and exits before it tests any mutant, on any branch that holds `origin/main` at `e084968ac`. Found on 2026-11-11 while building `PL-RF2S`. Close-out step 7 needs this run for every item that changes a mutated module, so no such item can list its survivors until this is fixed.

**Cause, two tests.** mutmut first runs the selected unit tests once inside `mutants/`, a copy of the tree that holds mutant copies of each function. Two tests fail there and pass everywhere else:

1. `tests/unit/test_readme_claims.py` reads `README.md` when it is imported (`PL-L9FC`, `#2075`, 2026-11-09). `[tool.mutmut] also_copy` in `pyproject.toml` copies `tools/`, `subprojects/docket/src/` and `docs/`, and not `README.md`, so the import raises `FileNotFoundError`.
2. `tests/unit/test_bare_numbers.py::test_every_bare_number_in_core_is_listed_with_its_reason` lists the functions in `core/` (`PL-LHCL`, `#2099`, 2026-11-11). Under mutmut it also lists the mutant copies, such as `xǁAgentSimulationValidatorǁcheck_agent_accounting__mutmut_1`, and fails on them. `test_each_guard_admits_only_what_its_functions_compute` fails the same way and is already deselected for that reason.

**Checked.** With `README.md` copied into `mutants/` by hand, the first step ran 3,594 tests and only the second test failed. Command, from `mutants/`: `MUTANT_UNDER_TEST=stats PYTHONPATH=src QT_QPA_PLATFORM=offscreen ../.venv/bin/python -m pytest --rootdir=. -q -p no:cacheprovider @selected-tests.txt --deselect tests/unit/test_supported_range_edges.py::test_each_guard_admits_only_what_its_functions_compute -n 8`.

**Suggested fix.** Add `"README.md"` to `also_copy`, and add a `--deselect` for the second test beside the first, with the same comment. Then run `make mutate` to its end on a branch that changes a mutated module.

**Why it landed unseen, to decide in triage.** No check runs the mutation run's first step, so a unit test that cannot run inside `mutants/` merges green. Two did in three days. Whether a check should run that step is a new workflow mechanism, which the generator pause holds, so this item records the question and does not build one.

**Why it matters.** Until this is fixed, no item that changes a module in `core/` or a mutated display module can run its mutation check. The close-out audit therefore has no answer for whether the unit tests catch a mutant of each changed line, and the audit never treats a missing answer as a pass.

**Triage decision on the question above, 2026-11-11.** The question is now `PL-QRDQ` (no check runs the mutation run's first step), in the feature `mutation-run-first-step`. This item does not build a check. The generator pause holds a new workflow mechanism, and the first step took about 19 minutes in this item's run (`PL-R8HY`), which is too long for a check on every pull request as it stands.

**Generator check.** The fact misread is which unit tests can run inside `mutants/`. Nothing records it: a test reads a file from the repository root, or lists the functions of `core/`, and nothing says the mutation copy lacks that file or holds extra functions. No head's `misread:` states this fact (`bin/docket generators --misread`, 2026-11-11). The instances are the two tests in this item and the guard test that `PL-Y1PS` deselected when it built `make mutate`. They make one item, so this is a one-off for now. A third test that lands the same way makes `PL-QRDQ` the head.

**Done when.** `make mutate` runs to its end on `origin/main` plus a change to a mutated module, and reports that change's mutants.

**Done, 2026-11-11.** `pyproject.toml`'s `[tool.mutmut]` table now copies `README.md` and deselects the second test. Both runs used one trial comment line inside `is_wash_in` in `src/anesthesia_sim/app/wash_in.py`, which was reverted afterwards, and the command `make mutate`:

- Before the fix, on `origin/main` at `798b96dd`: `failed to collect stats. runner returned 1`, and `make` exited 2 with no mutant tested.
- After the fix, on the same base: `anesthesia_sim.app.wash_in.is_wash_in: 2 mutants - 2 killed. All: 2 mutants - 2 killed.`, exit 0.

`tests/unit/test_diff_mutation.py` passed against the changed table (104 tests). `docs/mutation-testing.md` § "Pitfalls" now names both tests that are left out, and says that a unit test which reads a file needs that file in `also_copy`. The first step of the second run took about 19 minutes, which is filed as `PL-R8HY`.
