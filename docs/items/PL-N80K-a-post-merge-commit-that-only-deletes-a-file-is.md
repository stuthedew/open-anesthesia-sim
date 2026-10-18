---
id: PL-N80K
title: A post-merge commit that only deletes a file is never reported as left behind: the branch's content split is all landed, so _unlanded_refs treats it as taken whole and orphaned never asks about it (found building PL-TFF9)
priority: P3
effort: S
status: ready
classes: defect
feature: stranded-report-fidelity
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-18 triage pass
added: 2026-10-18
payoff: a commit made after a merge that only deletes a file is reported as left behind, instead of the report reading as complete without it
verify: grep -q 'def test_orphaned_reports_a_post_merge_commit_that_only_deletes_a_file' subprojects/docket/tests/test_vcs.py
reenters: PL-927J
---

**Problem.** A post-merge commit that only deletes a file is never reported as left behind: the branch's content split is all landed, so _unlanded_refs treats it as taken whole and orphaned never asks about it (found building PL-TFF9)

**Why it matters.** `bin/docket stranded` and `left_behind_check` exist to
say which commits a merged branch still holds that `main` never took. A commit
made after the merge that only deletes a file is such a commit, and the report
says nothing about it, so the deletion is lost without a word. The report then
reads as complete when it is not, which the apparatus standard's rule against
partial answers refuses.

**Found 2026-10-18** while building `PL-TFF9` (#1588). `PL-TFF9` taught the
left-behind walk to classify deleted paths, but `_unlanded_refs` decides
earlier that a branch whose content split is all landed was taken whole. A
deletion is no content, so a delete-only commit leaves the split all landed and
`orphaned` never asks about the branch.

**Done when.** `vcs.orphaned` reports a commit made after the merge that only
deletes a file the base still holds, and a test in
`subprojects/docket/tests/test_vcs.py` pins it.

**Generator check.** An instance of `PL-927J`'s fact, "whether the base already
holds or has superseded a branch commit's change, by whatever route", filed
after that head closed. So `reenters: PL-927J` is set. `PL-TFF9` is not the
re-entered fix: this was found while it was being built and left outside its
scope.
