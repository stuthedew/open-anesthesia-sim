---
id: PL-8M8H
title: docket branch tells a session whose pull request already merged to merge the base in, not to restart, so the push that loses work looks correct
priority: P2
effort: M
status: needs-decision
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py
added: 2026-09-04
---

**Problem.** `BranchState.disposition` picks between four states from the
*commit counts* `ahead` and `behind`. A branch whose pull request has already
merged and which then gains one commit reads as `ahead=1, behind=N`, which is
`MERGE` - "merge the base in". That is what the session that lost `#284`'s
follow-up commit was effectively told, and merging the base in is exactly what
it did (`7f87bf5`). Nothing said the thing that mattered: *this branch's work is
already on `main`; a push here is merged by nothing.*

**Why it matters.** `MERGE` is advice a session acts on: it merges the base
in and pushes, which is what `7f87bf5` did. On a squash-merged branch that push
is merged by nothing, so the commit is lost at the one moment recovering it is
still free - the session holding it is the session being told the wrong thing.

**Why the counts cannot say it.** A squash merge leaves the branch containing
none of the commits that landed its content, so `ahead` counts them all and
`behind` says nothing about whether they landed. `RESTART` fires only at
`ahead == 0`, which a squash-merged branch never reaches.

**The content question is now answered next door.** `vcs._landing_split`
(`PL-3D2M`) returns the paths a ref introduces that the base already holds and
the paths it does not. A branch whose landed side is non-empty has had work
taken by a pull request, whatever its commit counts say, and the advice for it
is `CLAUDE.md`'s merged-branch rule - restart on the merged `main` and carry the
commit forward - not `MERGE`.

**Why this is worth doing beside the detector it follows.** `PL-3D2M` detects
the loss in the next session. This would stop it happening: the session about to
push is the one holding the commit, and it is the last moment recovery is free.

**Decision needed.** Whether `disposition` gains a fifth state read from the
content split, or whether `format_branch` keeps the four and adds a line beside
them. The first makes every caller of `disposition` see it; the second leaves
the counts meaning what they have always meant.

**Done when.** `docket branch` tells a branch whose work the base already holds
to restart on the merged `main` and carry the commit forward - `CLAUDE.md`'s
merged-branch rule - rather than to merge the base in, and the reading it uses
is the content split rather than the commit counts.
