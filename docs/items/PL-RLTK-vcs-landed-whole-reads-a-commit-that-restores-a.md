---
id: PL-RLTK
title: vcs.landed_whole reads a commit that restores a file to content the default branch held earlier in its history as a commit the base took whole, because _base_blobs collects every blob the base's history ever held rather than its tip's: bin/docket branch told #1118's session its open pull request had merged, not to merge and push, and to restart the branch on origin/main, since c69bad17 put pr-title.yml back to the blob #1056 wrote and #1068 replaced
priority: P2
effort: S
status: ready
classes: defect
feature: pre-fork-content
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
payoff: bin/docket branch stops telling a session whose pull request is still open that it merged and should restart, whenever the branch restores a file to an earlier version
verify: grep -q 'def test_a_restore_to_content_main_held_before_the_fork_is_not_landed' subprojects/docket/tests/test_vcs.py
---

**Problem.** vcs.landed_whole reads a commit that restores a file to content the default branch held earlier in its history as a commit the base took whole, because _base_blobs collects every blob the base's history ever held rather than its tip's: bin/docket branch told #1118's session its open pull request had merged, not to merge and push, and to restart the branch on origin/main, since c69bad17 put pr-title.yml back to the blob #1056 wrote and #1068 replaced

**Observed 2026-09-26 on `claude/pr-body-storage-cnnpme`, `#1118` open.** Found
by running `landed_whole`'s own pieces against the branch: `_landing_split`
put `.github/workflows/pr-title.yml` and
`.claude/skills/docket/modes/close-out.md` in `landed`, though neither file had
changed on `origin/main` since the fork point. Each had been put back,
byte for byte, to its content from before `#1068`
(`git log --find-object` on the branch's `pr-title.yml` blob names `#1056`,
which wrote it, and `#1068`, which replaced it). `c69bad17` touched
`pr-title.yml` alone, so `_commits_by_landing` counted it as taken whole, and
`format_branch_state` printed the merged verdict and the restart recipe. The
session-start digest's `left_behind_check.py` line contradicted it ("#1118 is
open on it ... this ref comparison wins"), but `bin/docket branch` run on its
own prints no second opinion. Any branch that reverts a file to an earlier
version of itself is exposed: retiring a feature is the common case.

A lead, not a decision: a squash merge of this branch writes its blobs onto
the base *after* the fork point, so asking only for blobs the base gained
since then (`rev-list --objects <fork>..<base>`) would exclude a restored
earlier blob. Whether that costs `orphaned`, which shares `_base_blobs`, any
recall is the fixer's to measure.

**Reproduced 2026-09-26.** With `#1118`'s head fetched from
`refs/pull/1118/head`, and main as it stood before that pull request's squash
(`3902e0fe^`), `landed_whole` answers `True` for `b25089a0` and for
`33e82344`, both commits made while the pull request was open.

**Why it matters.** `bin/docket branch` turns `True` into `LANDED`, which tells
a session holding an open pull request that it merged, not to merge and push,
and to restart the branch on `origin/main`: the recipe for abandoning live
work. `orphaned` reads the same split, so it can report such a branch as a
merged one with work left behind. Retiring a feature restores files to earlier
versions, so the shape recurs.

**The evidence of a merge is content the base wrote after the fork** (the
session that built it, 2026-09-26). A squash of this branch lands after its
fork point, and content the base held only before it cannot have come from the
branch. The lead's `rev-list --objects <fork>..<base>` would also drop a blob
the fork's tree holds at another path, a rename or copy the branch made,
because that walk marks the fork's whole tree uninteresting. Reading what the
base's commits since the fork *wrote* (`git log --raw --no-renames ^<fork>
<base>`) keeps those. Measured here: 0.135 s for all 13 unmerged refs, whose
forks sit 0-6 commits behind; one walk of the whole history is 0.23 s. It is
applied to the split that `landed_whole` and `_unlanded_refs` share, and
through it to `orphaned`, never to one reader alone. `claims._landed_through`
keeps the ever-held set, because it splits an older commit against the tip's
fork and relies on that set below a grafted horizon (`PL-W1LN`). Its instance
of the same misread is filed as its own item under this feature.

**Done when.** `landed_whole` answers `False` for a branch whose only work
restores a file to content the default branch held before the fork, and still
answers `True` for a squash-merged branch. A regression test in
`subprojects/docket/tests/test_vcs.py` builds that restore on a scratch
repository, and every caller of `_landing_split` in `vcs.py` passes the blobs
the base wrote since that ref's fork.

**Generator check.** The fact is `PL-GHHW`'s `misread:` (drained 2026-09-23;
`PL-R808` and `PL-BHVM` state it too): whether the base already holds or has
superseded a branch commit's change, by whatever route. This is an instance
filed after those heads closed. A second is filed beside it for
`claims._landed_through`, the same misread by another reader. That makes two
post-close instances, one short of the three that would make this a generator
whose fix did not hold.
