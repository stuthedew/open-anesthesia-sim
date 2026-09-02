---
id: PL-NB4D
title: `docket verify` reports "1 commit(s)" when the work it just checked is entirely uncommitted
status: untriaged
added: 2026-09-02
---

**Problem.** `docket verify` reports "1 commit(s)" when the work it just checked is entirely uncommitted

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `subprojects/docket/src/docket/verify.py:355` formats the scope
check's detail as `f"{len(paths)} path(s) in {len(commits) or 1} commit(s)"`.
When the work is entirely uncommitted `commits` is empty, so `or 1` prints
"1 commit(s)" for a branch that carries none.

**Why it matters.** Small, but it is a check asserting something false at the
one moment it is wrong to: a worker running `docket verify` before committing
reads a confirmation that a commit exists. Observed on PL-019, which reported
"7 path(s) in 1 commit(s)" against a clean `git log origin/main..HEAD`.

**Approach.** Say what is actually true - "7 path(s), uncommitted" when
`commits` is empty, the count otherwise. `changed_paths()` already documents
that it folds the working tree in on purpose, so the fix is the wording of
the detail line, not the check.

**Where.** `subprojects/docket/src/docket/verify.py`,
`subprojects/docket/tests/test_verify.py`.
