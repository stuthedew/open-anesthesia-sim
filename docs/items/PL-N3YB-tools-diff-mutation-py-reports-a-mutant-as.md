---
id: PL-N3YB
title: tools/diff_mutation.py reports a mutant as undecided when it makes a test module raise during collection, because pytest exits 2 for that and RERUN_STATUS maps only 0 and 1, so the close-out audit refuses a branch whose test file builds a CaseInstant at import (found closing PL-756M and the rest of #1817, 2026-10-25)
status: untriaged
touches: tools/diff_mutation.py, tests/unit/test_diff_mutation.py
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-10-25
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
