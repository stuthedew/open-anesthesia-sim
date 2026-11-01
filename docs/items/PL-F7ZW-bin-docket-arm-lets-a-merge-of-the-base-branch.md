---
id: PL-F7ZW
title: bin/docket arm lets a merge of the base branch cancel a branch's Owner-read record but not its Owner-ask record, so a routine update from main makes an armed housekeeping pull request answer hold and tells the session to disarm it
priority: P2
effort: S
status: done
classes: defect
milestone: v0.6.11
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.7.0 - captured after the freeze; an arming defect in the workflow lane, not safety or science
added: 2026-10-27
closed: 2026-11-01
pr: 1906
payoff: a routine update from main no longer makes bin/docket arm tell a session to disarm a correctly armed pull request
verify: grep -q 'def test_arm_keeps_an_owner_read_record_through_a_merge_of_the_base' subprojects/docket/tests/test_cli.py && grep -q 'def _merge_keeps_the_work' subprojects/docket/src/docket/arming.py
---

**Problem.** bin/docket arm lets a merge of the base branch cancel a branch's Owner-read record but not its Owner-ask record, so a routine update from main makes an armed housekeeping pull request answer hold and tells the session to disarm it

Found on 2026-10-27 while merging #1844 (`PL-ZR49`). `docket.arming._since_change` takes `merges`, and its docstring says that without merges "a merge does not count as a change, so bringing the base in, which the owner's *Update branch* does, leaves a record standing". `_owner_ask` passes `merges=False`, but `_owner_read` uses the default `merges=True`. So after `git merge origin/main`, which changed no line of the branch's own work, `bin/docket arm` answered "no Owner-read record on a commit since its newest change there says whether the owner must read it". The `Owner-ask` record still stood. For a `needed` record this costs a restated trailer. For a `not needed` record on an armed pull request, the same answer tells the session to disarm it before pushing a plain update from `main`. Decide whether the read record should survive a merge of the base, as the ask record does, or say why the two differ. Any fix keeps or adds the test that pins the answer.

**Checked 2026-10-31.** `_owner_ask` in `subprojects/docket/src/docket/arming.py` calls `_since_change` with `merges=False`. `_owner_read` calls it with the default, `merges=True`. Neither docstring says why they differ.

**Why it matters.** Bringing `main` into a branch is routine, and `update-armed.yml` does it automatically. After such a merge, `bin/docket arm` finds no Owner-read record and tells a session to disarm a housekeeping pull request that was correctly armed. Either the pull request then waits on the owner for nothing, or the session restates a trailer to get past an answer it has learned to distrust.

**Done when.** A merge of the base that brings in none of the branch's own work leaves the Owner-read record standing, exactly as it leaves the Owner-ask record. A test in `subprojects/docket/tests/test_arming.py` pins this. The ask docstring's reason is that a merge brings in no work of the branch's, and the same holds for a read. If the builder finds a case where the two records must differ, such as a conflict resolution inside the branch's own paths, the docstrings state that case, and the test pins it instead.

**Generator check.** A one-off. One predicate, whether a merge of the base counts as a change to the branch's work, is answered two ways by two callers of one function. No head's `misread:` states it.

**Resolved 2026-11-01.** The two records do not need to differ, so both now read one rule. `_since_change` no longer takes `merges`. It walks the commits that changed the paths, newest first, and passes over a merge only where `_merge_keeps_the_work` finds the branch's own change unchanged by it: the first parent's diff against the fork point equals the merge's diff against the side brought in, with hunk line numbers ignored. So a clean merge of the base leaves both records standing. A merge that resolves a conflict by writing new lines counts as a change for both records, because that resolution is work nobody judged. Before this fix, the ask record skipped every merge with `--no-merges`, so a conflict resolution left it standing too. A git call that fails, or an octopus merge, counts as a change, so the answer errs toward holding.

The tests sit in `subprojects/docket/tests/test_cli.py`, not `test_arming.py`, because the `arm` repository fixtures live there and `test_arming.py`'s docstring sends branch-reading tests there. `test_arm_keeps_an_owner_read_record_through_a_merge_of_the_base` failed on the unfixed code and passes now. `test_arm_drops_an_owner_read_record_when_a_merge_resolves_a_conflict_in_new_lines` pins the conflict case. The commissioned `verify:` grepped for a test name in `test_arming.py` that the work never had a reason to create. It is rewritten to grep for the test and the new function, and it fails on `main`.
