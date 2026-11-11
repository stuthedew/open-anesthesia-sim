---
id: PL-QRDQ
title: No check runs the mutation run's first step, so a unit test that cannot run inside the mutation copy of the tree merges green: two did between 2026-11-09 and 2026-11-11 (PL-GP8G), and whether a check should run that step is undecided
status: untriaged
feature: mutation-run-first-step
added: 2026-11-11
---

**Problem.** No check runs the mutation run's first step, so a unit test that cannot run inside the mutation copy of the tree merges green: two did between 2026-11-09 and 2026-11-11 (PL-GP8G), and whether a check should run that step is undecided

**What happens.** mutmut starts each run by running the selected unit tests once inside `mutants/`, a copy of the tree that holds mutant copies of each function. A unit test that cannot run there stops every mutation run with `failed to collect stats. runner returned 1`. No check runs that step, so such a test merges green. The next session that runs `make mutate`, or the close-out audit's mutation check, finds it.

**Instances.** `tests/unit/test_readme_claims.py` (`PL-L9FC`, `#2075`, 2026-11-09) read `README.md`, which was not copied. `tests/unit/test_bare_numbers.py::test_every_bare_number_in_core_is_listed_with_its_reason` (`PL-LHCL`, `#2099`, 2026-11-11) lists the functions of `core/` and found the mutant copies. `PL-GP8G` fixed both on 2026-11-11. `PL-Y1PS` deselected `test_each_guard_admits_only_what_its_functions_compute` for the second reason when it built `make mutate`.

**Why it matters.** Each such test blocks the mutation check of every later branch that changes a mutated module, until someone traces the failure. `PL-RF2S`'s session lost its mutation run to the two tests above.

**What a check would cost.** The first step took about 19 minutes on a four-core container on 2026-11-11 (`PL-R8HY`), against 2 min 59 s for the same tests outside mutmut. A check that runs the step on every pull request would add that time, so `PL-R8HY` comes first. A cheaper form may exist: run the selected tests once under `MUTANT_UNDER_TEST=stats` in the copied tree, only when a pull request adds or changes a file under `tests/unit/`. Nobody has measured it.

**Checked 2026-11-11 (`PL-R8HY`).** The 19 minutes was two passes over the tests, and both paid for mutmut's wrapper around every function of every mutated file. With one little-called file mutated, the first pass took 3 min 41 s on four idle cores. So a check that runs the unit tests inside the mutation copy with one such file mutated would add about 4 minutes, not 19.

**Not built.** A check is a new workflow mechanism, and the generator pause in `CLAUDE.md` § "What this project is" holds one while a workflow-lane head is still generating. `PL-GP8G`'s generator check counts three instances in one item. A further test that lands this way makes this item the head of a generator.

**Done when.** Either a check refuses a pull request whose unit tests fail inside the mutation copy, or the item records a decision that the cost is not worth it, with the count of instances since 2026-11-11.

