---
id: PL-F5CF
title: vcs.landed_whole asks _superseded for an outstanding set nothing reads: _commits_by_landing's whole-commit verdict reads only the landed side, so each landed_whole call pays a git diff per ref, and since PL-F7Z6 a git show per removals-only path, for no answer; found building PL-F7Z6
priority: P3
effort: S
status: done
classes: perf
feature: friction-batch
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-05
closed: 2026-10-17
payoff: bin/docket branch and the session-start snapshot stop paying a git diff per ref and a git show pair per removals-only path for a set the landed-whole verdict never reads
verify: grep -q 'def test_landed_whole_reads_no_supersession' subprojects/docket/tests/test_vcs.py
---

**Problem.** vcs.landed_whole asks _superseded for an outstanding set nothing reads: _commits_by_landing's whole-commit verdict reads only the landed side, so each landed_whole call pays a git diff per ref, and since PL-F7Z6 a git show per removals-only path, for no answer; found building PL-F7Z6

**Reproduced 2026-10-11** on main at `16a20a4f`, in a scratch repository
whose branch has one commit the base took whole, one outstanding, and one path
the base extended: `landed_whole` answered `True` with `_superseded` as
written, patched to return nothing, and patched to return every path, and the
real call made seven git calls to the patched calls' four - a `git diff` and a
`git show` pair for the removals-only path. `_landing_split` puts each path in
exactly one of its two sets, so a commit wholly in `outstanding` is never
wholly in `landed`, and the branch that sets the verdict reads `landed` alone.

**Why it matters.** `landed_whole` runs in `bin/docket branch` and the
session-start snapshot whenever a branch reads as behind, so each call pays a
diff per ref and a `show` pair per removals-only path for a set it throws
away. Cost only, never a wrong answer, but a call nothing reads also misleads
the next reader into treating it as load-bearing.

**Generator check.** A one-off: `landed_whole` reused `orphaned`'s pipeline
whole, kept a step only the left-behind side reads, and answers correctly; no
head's fact is misread.

**Done when.** `landed_whole` reaches `_commits_by_landing`'s verdict without
calling `_superseded`, and a test drives a ref with a removals-only path,
asserting the verdict is unchanged and no `git show` runs.
