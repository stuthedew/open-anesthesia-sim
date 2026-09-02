---
id: PL-NB4D
title: '`docket verify` reports "1 commit(s)" when the work it just checked is entirely uncommitted'
priority: P2
effort: S
status: ready
classes: defect
feature: dev-tooling
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-02
verify: uv run pytest subprojects/docket/tests/test_verify.py -k uncommitted && grep -q 'def test_uncommitted_work_is_not_reported_as_a_commit' subprojects/docket/tests/test_verify.py
---

**Problem.** `subprojects/docket/src/docket/verify.py:355` formats the scope
check's detail as `f"{len(paths)} path(s) in {len(commits) or 1} commit(s)"`.
When the work is entirely uncommitted `commits` is empty, so `or 1` prints
"1 commit(s)" for a branch that carries none.

**Why it matters.** Small in size and specific in consequence: it is a check
asserting something false at the one moment it is wrong to. `docket verify`
is what a worker runs to prove its work stayed inside the item's commission,
and the container is ephemeral, so "have I committed this?" is the single
question a session most needs a truthful answer to before it ends. The line
answers it wrongly and confidently. Observed on PL-019, which reported
"7 path(s) in 1 commit(s)" against a clean `git log origin/main..HEAD`.

**Approach.** Say what is actually true - "7 path(s), uncommitted" when
`commits` is empty, the count otherwise. `changed_paths()` already documents
that it folds the working tree in on purpose, so the fix is the wording of
the detail line, not the check.

**Where.** `subprojects/docket/src/docket/verify.py`,
`subprojects/docket/tests/test_verify.py`. Note that
`test_uncommitted_work_is_counted` already covers the *counting* behavior and
should stay; what is missing is a test that the detail line does not claim a
commit that does not exist.

**Done when.** `docket verify` on a branch with no commits reports the paths
without asserting a commit count, and a test pins that wording so the `or 1`
cannot come back.
