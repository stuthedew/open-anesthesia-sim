---
id: PL-8M8H
title: docket branch tells a session whose pull request already merged to merge the base in, not to restart, so the push that loses work looks correct
priority: P2
effort: M
status: ready
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_branch_whose_work_the_base_already_holds_is_told_to_restart' subprojects/docket/tests/test_vcs.py
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

**Decision needed, part one.** Whether `disposition` gains a fifth state read
from the content split, or whether `format_branch` keeps the four and adds a
line beside them. The first makes every caller of `disposition` see it; the
second leaves the counts meaning what they have always meant.

**Decision needed, part two — ANSWERED 2026-09-12, see below.** *Which* reading of `_landing_split` this item adopts: the unqualified one
its own **Why it matters.** asserts - "a branch whose landed side is non-empty
has had work taken by a pull request" - or one carrying
`_commits_by_landing`'s narrowing at
`subprojects/docket/src/docket/vcs.py:2801`, `elif all(path in landed for path
in touched): took_one_whole = True`, the guard `PL-JHJ3` and `PL-5TRV` added
after `orphaned` fired falsely on its first live run.

This is not a detail. Two documented false-positive shapes satisfy "landed side
non-empty" - `PL-Y31G` (a branch forked before a history rewrite, its
pre-rewrite blobs duplicated on the base, nothing merged) and `PL-XLQ5` (the
base holds a superset of the branch's blobs). Where those shapes cost a spurious
line in `bin/docket stranded` today, the unqualified reading on *this* item's
path would tell a session whose pull request is still **open** to run the
restart recipe, which `.claude/skills/docket/SKILL.md:216` calls "These three
commands destroy a branch." The error direction inverts from noisy to lossy, so
the qualifier is a correctness question rather than a refinement.

**Done when.** `docket branch` tells a branch whose work the base already holds
to restart on the merged `main` and carry the commit forward - `CLAUDE.md`'s
merged-branch rule - rather than to merge the base in, and the reading it uses
is the content split rather than the commit counts.

## Part two, decided 2026-09-12 by the project owner: the qualifier is required

`disposition` may **not** adopt the unqualified `_landing_split` reading. Any
restart verdict this item produces must carry `_commits_by_landing`'s
`took_one_whole` narrowing - `subprojects/docket/src/docket/vcs.py:2801`, `elif
all(path in landed for path in touched): took_one_whole = True` - or an
equivalent that excludes the same shapes.

**The reasoning, so a later session does not reopen it as a performance or
simplicity question.** The unqualified reading admits two documented
false-positive shapes: `PL-Y31G` (a branch forked before a history rewrite,
whose pre-rewrite blobs are duplicated on the base, with nothing merged) and
`PL-XLQ5` (the base holds a superset of the branch's blobs). Where those shapes
today produce a spurious line in `bin/docket stranded`, on this item's path they
would drive the **restart** arm, telling a session whose pull request is still
open to run the three commands `.claude/skills/docket/SKILL.md:216` describes as
destroying a branch. The qualifier is therefore not a refinement of the answer;
it is what keeps a wrong answer non-destructive. `PL-JHJ3` and `PL-5TRV` added
that guard to `orphaned` after it fired falsely on its first live run, and the
lesson transfers unchanged.

**What this does not settle.** Part one is still open - whether `disposition`
gains a fifth state or `format_branch_state` keeps four and adds a line beside
them - so this item stays `needs-decision`. The qualifier constrains whichever
shape part one picks rather than choosing between them.

**A consequence worth carrying into the build.** A qualified reading is
strictly more conservative: it will decline to call some genuinely-merged
branches merged. For a verdict whose wrong answer destroys work, declining is
the right failure direction, and the four-state output already has somewhere to
put "cannot tell" without inventing one.

## Part one, decided 2026-09-13: a fifth state, and it reuses `orphaned`'s verdict

`disposition` gains a fifth state read from the content split. `format_branch_state`
does **not** keep four and add a line beside them.

**What decided it was the precedent already in the file, not the caller count.** The
brief frames part one as a trade between "every caller of `disposition` sees it" and
"the counts keep meaning what they have always meant". Measured, neither side is
worth much: `disposition` has exactly two non-test consumers, and one of them —
`subprojects/docket/src/docket/cli.py:1452`, `args.if_stale and state.disposition ==
CURRENT` — only asks whether the branch is current, so it is unaffected either way.
The other is `format_branch_state` itself. There is no third reader to inform and no
third reader to protect.

What does decide it is `REWRITTEN`. It is already a state decided from evidence other
than the counts — `RewriteReport`, built from a content walk — and it already
outranks `MERGE` for precisely this item's reason: merging would damage the branch.
`format_branch_state`'s own docstring states the principle to apply here verbatim:
"The rewritten case is the exception, and it *replaces* that advice rather than
adding to it."

This item's case is that case with a different detector. So the shape is settled by
consistency rather than by preference, and the alternative is actively bad: a line
beside `MERGE` would print `Merge main before your first edit, not at push time: git
merge main` **and** a line saying the work already landed, in one block, as advice on
one branch. The session that lost `#284`'s follow-up commit followed the merge line.
Adding a contradiction beside it leaves that reading available.

**Three things the build has to get right, each read off the code rather than
designed fresh.**

1. **Order it after `REWRITTEN`, before `MERGE`.** `PL-Y31G` — a branch forked before
   a history rewrite, its pre-rewrite blobs duplicated on the base, nothing merged —
   is one of the two false-positive shapes part two names, and the existing `if
   self.rewrite is not None: return REWRITTEN` already excludes it at no cost.
   `orphaned` reaches the same conclusion from the other end and says so at
   `subprojects/docket/src/docket/vcs.py:3263` onward: a rewritten history "reads
   exactly like a merge here, and the difference cannot be seen in the content".
   Slotting the new state below `REWRITTEN` inherits that for free.
2. **Reuse `orphaned`'s narrowed verdict; do not re-derive it.** Part two requires
   `_commits_by_landing`'s `took_one_whole` narrowing or an equivalent. The
   equivalent already exists as a pipeline: `_landing_split` for the split, then
   `_superseded` to drop paths the base's tip no longer needs — which is what
   excludes `PL-XLQ5`, the *other* false-positive shape part two names — then
   `_commits_by_landing` for `took_one_whole`, which also declines a commit whose
   whole diff is a queue annotation. Every guard part two asks for is written and
   tested. Re-deriving the reading is what would reopen the question.
3. **Keep `disposition` pure; populate the field in `branch_state`.** `disposition`
   is a property over cached fields and the landing verdict costs three git calls, so
   it is collected in `branch_state` the way `rewrite` is. Compute it **only where
   the counts would otherwise say `MERGE`** — `behind > 0`, `ahead > 0`, `rewrite is
   None` — which is the one arm whose advice this changes, so `CURRENT`, `PULL`,
   `RESTART` and `REWRITTEN` branches pay nothing. The session-start hook runs this
   on every session, so that is the difference between free and not.

**One render detail that would otherwise fail quietly.** `MERGE` is the `else`
fallthrough in `format_branch_state`, not a matched arm. A new state added without
its own arm therefore renders as "merge the base in" — the exact wrong advice, with
no error anywhere. The arm goes above the `else`, and the advice it prints is
`CLAUDE.md`'s merged-branch rule: restart on the merged `main` and carry the commit
forward.

**Sequencing.** `render.py` was being edited on `claude/gracious-noether-xjcvju`
(`PL-VFVW`, `PL-F4JS`) when this was decided, and those are smaller changes. They
land first; this resolves against them.
