---
id: PL-WYDF
title: The mutation check's comparison of a changed test with its base version gives no answer when the base tests reach none of the mutated code, so verify refuses a branch that weakened nothing
status: done
feature: verify-false-reject
touches: tools/diff_mutation.py, tests/unit/test_diff_mutation.py
added: 2026-11-22
closed: 2026-11-22
pr: 2223
tests: tests/unit/test_diff_mutation.py::test_a_compare_run_whose_tests_reach_no_mutant_catches_none
---

**Problem.** `tools/diff_mutation.py`'s `compare_tests` runs mutmut on the base
version of each changed simulator unit test, to find mutants that the base
version catches and the branch's version misses. When the selected base tests
call none of the mutated code, mutmut stops before its first mutant with
"Stopping early, because we could not find any test case for any mutant" and
exits 1. `_compared_statuses` treats every non-zero exit as a failed run and
raises `Refusal`, so `bin/docket verify` reports "no answer" and rejects the
branch. The right answer is that the base tests catch no mutant, which
`compare_tests` already reports as a note ("catches no mutant of ..., so the
branch's version has nothing to keep catching").

**Found** on 2026-11-22 by `bin/docket verify --self PL-LBVN` (the change to
Mapleson's MAC at age 40): the base copy ran three selected tests, mutmut
mutated 24 files, and it stopped early with exit 1. `make check` passed.

**Done when.** `_compared_statuses` returns no statuses when mutmut stops early
because no selected test reaches a mutant, and still raises `Refusal` for any
other non-zero exit. A unit test in `tests/unit/test_diff_mutation.py` covers
both.

**Generator check.** The fact misread is what mutmut's exit status 1 means. It
means either a failed run or a run with nothing to test, and the tool read only
the first.

**Done 2026-11-22**, on the `PL-LBVN` branch. `_compared_statuses` returns no
statuses when mutmut's log says that no selected test reaches a mutant, and
still raises `Refusal` for any other non-zero exit. The new unit test checks
both, and it failed on the code before the fix. Docs checked:
`docs/mutation-testing.md` (says nothing about this exit, so nothing to
change) and the module docstring of `tools/diff_mutation.py`.
