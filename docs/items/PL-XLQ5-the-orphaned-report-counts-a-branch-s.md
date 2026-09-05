---
id: PL-XLQ5
title: The orphaned report counts a branch's superseded intermediate blob as work the squash left behind
priority: P2
effort: M
status: ready
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-05
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_branch_that_revised_its_own_file_before_merging_carries_nothing' subprojects/docket/tests/test_vcs.py
---

**Problem.** `bin/docket stranded`'s second half reports a branch whose pull
request took part of its work and left the rest - the case `PL-3D2M` built it
for, where a commit pushed after the merge is merged by nothing. It decides
that by blob: a blob a branch commit introduced and the default branch has
never held is work the base does not have.

A branch that *revised its own file* before merging trips this. The
intermediate blob was introduced by an early commit and superseded by a later
one on the same branch, so the squash carried only the final version and the
base has genuinely never held the intermediate. Nothing was left behind; the
branch simply changed its mind once.

**Observed 2026-09-05**, immediately after `PL-X3WZ` merged as #324. Its
branch renamed one function in a later commit than the one that introduced it,
which is enough:

```
1 branch carries work the default branch does not hold, having already taken the rest of it:
origin/claude/next-workflow-item-c2b07p  (4 files of its work already landed)
  419ef856d  PL-X3WZ: read a commit's diff, not only its subject, before calling it work
```

`git diff origin/main HEAD` was **empty** - the default branch held every byte
the branch had. The four files named were the four the first commit wrote and
a later commit rewrote.

**Why it matters.** It is the shape `CLAUDE.md` calls out as the worst kind of
check: one that fires routinely without changing a decision, in a report whose
*other* half is load-bearing. Disproving it took a two-dot `git diff` that the
report does not suggest and a reading of two closed items to confirm neither
covered it. A session that instead believes it will "recover" files that are
already on main, on a branch whose pull request is merged - which is the one
push `PL-3D2M` records as losing work.

**Not the same as `PL-JHJ3` or `PL-3D2M`, both closed.** `PL-JHJ3` fixed a
squash that merged *content* reading as unlanded, by comparing blobs the base
has ever held rather than commits. This is that comparison working exactly as
written and still answering wrongly, because the branch - not the merge - is
what the base never held the blob from.

**A second surface, observed but not fully diagnosed.** In the same checkout
and minute, `bin/docket flight` reported `PL-66FP` in flight on
`origin/claude/pl-66fp-duplicate-sessions-g4zi8d`, whose pull request had
merged as #323 - while `bin/docket stranded`, which reads the same
`_landing_split`, said that branch carried nothing left behind. Both answers
cannot be right. `_work_already_on_base` is what excludes a landed branch from
`flight`, and that branch had merged the default branch into itself before its
own squash, so its commits introduced intermediate blobs the base never held -
the same shape as above. Worth confirming as part of this rather than filed
separately: one reading produced both, and a fix to it should be checked
against both commands.

**Where.** `subprojects/docket/src/docket/vcs.py` - `orphaned`,
`_work_already_on_base` and the `_landing_split`/`_base_blobs` reading beneath
them; `render.py` for the wording.

**Possible readings, none decided.** Compare against the branch's *own tip*
rather than every blob its history introduced - a path whose final content
landed is not outstanding however many intermediate versions preceded it. That
is the shape the two-dot `git diff` used to disprove it, so it is likely both
cheaper and more correct than the historical walk. Failing that, say in the
report which blobs are superseded on the branch itself.

**Done when.** A branch that revised a file before merging, and whose content
the default branch then holds in full, is reported as carrying nothing; a
branch with a genuine post-merge commit is still reported.
