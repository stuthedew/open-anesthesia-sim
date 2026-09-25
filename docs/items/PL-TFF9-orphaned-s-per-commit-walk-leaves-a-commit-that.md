---
id: PL-TFF9
title: orphaned's per-commit walk leaves a commit that deletes a file unclassified, since the deleted path is in neither of _landing_split's sets, so a left-behind commit that deletes one file and edits another is never reported as work left behind
priority: P2
effort: M
status: ready
classes: defect
feature: stranded-report-fidelity
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
payoff: a commit pushed after its pull request merged is reported as left behind even when it deletes a file, so bin/docket stranded stops calling lost work accounted for
verify: grep -q 'def test_orphaned_reports_a_left_behind_commit_that_also_deletes_a_file' subprojects/docket/tests/test_vcs.py
---

**Problem.** orphaned's per-commit walk leaves a commit that deletes a file unclassified, since the deleted path is in neither of _landing_split's sets, so a left-behind commit that deletes one file and edits another is never reported as work left behind

Found 2026-09-25 by PL-KR69's build, by reading rather than reproducing. `vcs._commits_by_landing` reports a commit as left behind only when every path its `git log --name-only` lists is in `_landing_split`'s outstanding set, and `_landing_split` classifies only the paths whose post-image blob is non-zero, so a deleted path is in neither set. A commit that deletes one file and edits another then fails both `all(...)` tests and is neither reported nor counted as taken whole. A rename git scores below 50% similarity lists as a deletion and an addition, and reads the same way. PL-KR69 kept this walk on git's rename detection for exactly that reason, and did not change its classification.

**Not a recurrence of PL-WNQT**, which `docket new` matched on title words. PL-WNQT is the same walk reporting too much (a later merge editing the file makes a landed commit read as left behind); this is it reporting too little, from a different mechanism.

**Reproduced 2026-09-25 against 46954a81**, since `vcs.py` has not changed on
`origin/main` since then. The scratch repository was set up as follows. A
fork `F` holds `old.txt` and `b.txt`. Branch `claude/work` adds `a.txt`, and
`main` takes that commit as a squash. The branch then gets a post-merge commit
`c2`. Where `c2` only edits `b.txt`, `vcs.orphaned` reports `claude/work` and
`origin/claude/work`, each with `c2` left behind. Where `c2` also deletes
`old.txt`, it reports nothing: `branches reported: []`, with no decline. That
is the fault.

**Why it matters.** `orphaned` is what `bin/docket stranded` and the
session-start digest print for work a merged pull request left behind. Where
`tools/left_behind_check.py` declines (offline, or a pull ref GitHub no longer
holds), it is the only such check. In this shape it reports every branch as
accounted for while a commit lands nowhere. That silence is the direction
`orphaned`'s own docstring calls this check's expensive one, and this shape
is not among the recall trades `_commits_by_landing` documents as taken on
purpose. `PL-CZR6`'s miss, in the same feature, is undiagnosed. This is one
mechanism that produces its symptom, though nothing shows it is that miss's
cause.

**Done when.** A path a commit deletes counts in the walk's classification.
So a left-behind commit that deletes one file and edits another is reported,
and a whole-taken commit that includes a deletion counts as taken whole. A
real-git test in `subprojects/docket/tests/test_vcs.py` drives the
delete-and-edit sequence above.

**Generator check.** An instance of `PL-GHHW`'s fact: whether the base already
holds a branch commit's change, by whatever route. It was filed after that
head closed on 2026-09-23. `_commits_by_landing` still decides the question
from `_landing_split`'s blob sets rather than from the change, and a deletion
has no blob, so the walk cannot answer for it. The head's fix did not move
this reader onto `vcs.change_landed`. `PL-8BR0` (`landed_whole`) was the first
post-close instance of that head and this is the second. A third would make
it a head whose fix did not hold. It is not `PL-PVW2`'s, although `PL-KR69`'s
build found it as it found that head's `PL-8HSX`. No one predicate is spelled
two ways here. The walk compares every path a commit touched against
`_landing_split`'s set of paths given content, which is deliberately narrower,
as though the two were the same set.
