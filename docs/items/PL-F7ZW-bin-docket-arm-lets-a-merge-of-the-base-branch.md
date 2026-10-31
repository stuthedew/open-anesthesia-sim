---
id: PL-F7ZW
title: bin/docket arm lets a merge of the base branch cancel a branch's Owner-read record but not its Owner-ask record, so a routine update from main makes an armed housekeeping pull request answer hold and tells the session to disarm it
priority: P2
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_arming.py
deferred-from: v0.7.0 - captured after the freeze; an arming defect in the workflow lane, not safety or science
added: 2026-10-27
payoff: a routine update from main no longer makes bin/docket arm tell a session to disarm a correctly armed pull request
verify: grep -q 'def test_owner_read_survives_a_merge_of_the_base' subprojects/docket/tests/test_arming.py
---

**Problem.** bin/docket arm lets a merge of the base branch cancel a branch's Owner-read record but not its Owner-ask record, so a routine update from main makes an armed housekeeping pull request answer hold and tells the session to disarm it

Found on 2026-10-27 while merging #1844 (`PL-ZR49`). `docket.arming._since_change` takes `merges`, and its docstring says that without merges "a merge does not count as a change, so bringing the base in, which the owner's *Update branch* does, leaves a record standing". `_owner_ask` passes `merges=False`, but `_owner_read` uses the default `merges=True`. So after `git merge origin/main`, which changed no line of the branch's own work, `bin/docket arm` answered "no Owner-read record on a commit since its newest change there says whether the owner must read it". The `Owner-ask` record still stood. For a `needed` record this costs a restated trailer. For a `not needed` record on an armed pull request, the same answer tells the session to disarm it before pushing a plain update from `main`. Decide whether the read record should survive a merge of the base, as the ask record does, or say why the two differ. Any fix keeps or adds the test that pins the answer.

**Checked 2026-10-31.** `_owner_ask` in `subprojects/docket/src/docket/arming.py` calls `_since_change` with `merges=False`. `_owner_read` calls it with the default, `merges=True`. Neither docstring says why they differ.

**Why it matters.** Bringing `main` into a branch is routine, and `update-armed.yml` does it automatically. After such a merge, `bin/docket arm` finds no Owner-read record and tells a session to disarm a housekeeping pull request that was correctly armed. Either the pull request then waits on the owner for nothing, or the session restates a trailer to get past an answer it has learned to distrust.

**Done when.** A merge of the base that brings in none of the branch's own work leaves the Owner-read record standing, exactly as it leaves the Owner-ask record. A test in `subprojects/docket/tests/test_arming.py` pins this. The ask docstring's reason is that a merge brings in no work of the branch's, and the same holds for a read. If the builder finds a case where the two records must differ, such as a conflict resolution inside the branch's own paths, the docstrings state that case, and the test pins it instead.

**Generator check.** A one-off. One predicate, whether a merge of the base counts as a change to the branch's work, is answered two ways by two callers of one function. No head's `misread:` states it.
