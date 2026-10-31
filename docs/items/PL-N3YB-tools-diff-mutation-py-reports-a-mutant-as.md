---
id: PL-N3YB
title: tools/diff_mutation.py reports a mutant as undecided when it makes a test module raise during collection, because pytest exits 2 for that and RERUN_STATUS maps only 0 and 1, so the close-out audit refuses a branch whose test file builds a CaseInstant at import (found closing PL-756M and the rest of #1817, 2026-10-25)
status: done
milestone: v0.6.9
touches: tools/diff_mutation.py, tests/unit/test_diff_mutation.py
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-10-25
closed: 2026-10-25
pr: 1817
verify: grep -q 'def test_a_module_that_raises_while_it_is_collected_counts_as_a_kill' tests/unit/test_diff_mutation.py
---

**Problem.** tools/diff_mutation.py reports a mutant as undecided when it makes a test module raise during collection, because pytest exits 2 for that and RERUN_STATUS maps only 0 and 1, so the close-out audit refuses a branch whose test file builds a CaseInstant at import (found closing PL-756M and the rest of #1817, 2026-10-25)

**Reproduced 2026-10-25.** The close-out audit of #1817 refused four mutants
of `require_supported_case_instant`, each "caught by the base version,
unsettled, pytest exited 2 on this branch's version". Kept and logged, the
rerun in the branch tree printed `ERROR collecting
tests/unit/test_dashboard_frame.py`, raised from the module-level
`CaseInstant(45.35)` at its line 3295, and then `Interrupted: 1 error during
collection`. The same files exit 0 with no mutant applied.

**Why it matters.** `settle`'s docstring says that a raise while a test module
is imported "fails the collection, which is a kill". The comment above
`RERUN_STATUS` says such a run exits 1 under `-x`. It exits 2, which the table
leaves unsettled. So a branch whose changed unit test file builds a guarded
value at import is refused for mutants its tests catch.

**Done when.** A rerun whose pytest output reports a collection error counts
as a kill, and an exit 2 for any other reason, such as a real interrupt, stays
unsettled. The comment above `RERUN_STATUS` states what pytest does.

**Generator check.** A one-off. The fact misread is pytest's exit status for
a run stopped by a collection error, which the comment above `RERUN_STATUS`
stated as 1 without measuring it. No head's `misread:` names pytest's exit
statuses. `PL-VMMB` also turned on a pytest status, 5 for a run that collects
nothing, but in another mechanism and for another meaning.

**Fixed 2026-10-25.** `_pytest_in_mutants` returns 1 where pytest exited 2 and
printed `Interrupted: N error(s) during collection`, and leaves any other
exit 2 as it is.
`test_a_module_that_raises_while_it_is_collected_counts_as_a_kill` fails on
`origin/main`'s tool with `assert 2 == 1`. Run on the branch tree that the
#1817 audit built, the fixed helper settles all four refused mutants as kills.
