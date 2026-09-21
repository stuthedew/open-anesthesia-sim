---
id: PL-MBTZ
title: bin/docket stranded offers to recover PL-THPB from origin/claude/next-version-release-o2zzaf, where the branch's copy is older than main's: the recover line would overwrite a done item with an untriaged one
priority: P2
effort: M
status: done
classes: defect
feature: stranded-ahead-or-behind
milestone: v0.5.0
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, .claude/skills/docket/modes/capture.md
added: 2026-09-14
closed: 2026-09-21
pr: 825
verify: uv run pytest -q subprojects/docket/tests/test_cli.py -k stranded && grep -q 'def test_stranded_does_not_offer_to_restore_a_copy_the_base_has_closed_since' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket stranded offers to recover PL-THPB from origin/claude/next-version-release-o2zzaf, where the branch's copy is older than main's: the recover line would overwrite a done item with an untriaged one

**Why it matters.** This is `PL-XLQ5`'s hazard live rather than historical.
`bin/docket stranded` names the branch and prints

```
recover: git checkout origin/claude/next-version-release-o2zzaf -- docs/items/PL-THPB-tag-v0-4-21-on-the-merge-commit-of-549-the.md
```

and running it replaces `main`'s copy with an **older** one. Measured
2026-09-14:

| | `status` | other fields |
| --- | --- | --- |
| `origin/main` | `done` | `closed: 2026-09-13`, a `verify:` command |
| the branch | `untriaged` | neither |

So the branch carries nothing `main` lacks; what it carries is a stale earlier
revision of a file `main` has since moved on from. The check's own second half
- "a branch carries work the default branch does not hold, having already taken
the rest of it" - is answering on content the base once held rather than on
content the base still needs, which is the distinction `_superseded` draws for
`orphaned` and which this path appears not to make.

`v0.4.21` is tagged on `6cd1a1da` (the `#549` merge), verified against
`git ls-remote --tags origin` on 2026-09-14, so `PL-THPB` is genuinely finished
and `main` is right about it.

**Where.** `subprojects/docket/src/docket/vcs.py`'s orphaned-branch half, and
`.claude/skills/docket/SKILL.md`'s recovery recipe, which tells a reader to run
the `git checkout` without saying to compare the two copies first.

**Two things a fix could be, and they are not the same size.** Comparing the
branch's copy against the base's before offering the recovery line is small and
decidable. Whether the branch should be reported at all once every file it
carries is superseded is the larger question, and it is the one that stops the
ref being re-discovered in every session.

**Until then, the disposition is: do not run the recovery.** The only thing
outstanding on that ref is the remote deletion, which `PL-TFWR` already covers
and which is the project owner's to run.

**Found.** 2026-09-14, verifying the session-start digest's stranded line
before repeating it.

**The named instance no longer reproduces, and the defect does.** Checked
2026-09-14 after `git fetch origin`: `origin/claude/next-version-release-o2zzaf`
is no longer among the refs this checkout holds, so `bin/docket stranded` no
longer offers `PL-THPB`. What it offers today is three items on
`origin/claude/bold-mayer-ij89qm`, which is a live session's branch and
correctly left alone. The instance being gone is luck rather than a fix: nothing
in the command learned to compare the two copies.

**Why it matters.** `stranded` prints a `git checkout <branch> -- <file>` line
and the `docket` skill tells a session to run it. That line overwrites
unconditionally, so where the branch's copy is *older* than the base's - the
item closed on `main` while an unmerged branch still holds the untriaged
version - following the advice reverts a done item to `untriaged` and silently
discards its `closed`, `milestone` and `pr`. The command is confident and
specific, which is what makes it dangerous: `CLAUDE.md` names "gives a wrong
answer silently" as the first of its three compounding-friction tests, and a
destructive recipe presented as a recovery is that test squarely. `PL-XLQ5`
already cost this project the same shape once.

**Done when.** `bin/docket stranded` compares the branch's copy against the
base's before offering a recovery: an item the base already holds in a *newer*
state is not offered, or is offered with the difference named and the checkout
line withheld. `tests/unit/` covers a branch copy that is behind the base.

**Re-pointed by `PL-BHVM`'s design round, 2026-09-19.** Question 3 — is the
ref's copy ahead of the base's. `PL-SH9Q`, `PL-KSCW` and `PL-MBTZ` are one
build, not three: `stranded` keys on whether an item *id* is on the base, and
the predicate it wants is per item file and three-valued — the ref's copy is
**ahead** (report it, with a diff to read), **behind** (never report, never
print a checkout line) or **equal** (silent). Ahead-not-equal is `PL-SH9Q` and
`PL-KSCW`; behind is `PL-MBTZ`. Do them together.

**Grouped as `feature: stranded-ahead-or-behind`** (`PL-JKML`'s duplicate sweep,
2026-09-20). `PL-BHVM`'s design round settled on 2026-09-19 that `PL-SH9Q`,
`PL-KSCW` and `PL-MBTZ` are one build rather than three - one three-valued
per-item-file predicate, where the ref's copy is **ahead** (report it, with a
diff to read), **behind** (never report, never print a checkout line) or
**equal** (silent). That conclusion was written into two of the three briefs as
prose and into the store's only grouping field nowhere, so `bin/docket status`,
`bin/docket feature` and `recommend`'s finish-a-feature preference all read the
three as unrelated work, and they sat in two different features
(`parallel-sessions` and `stranded-item-edits`). They are ranked together by
`PL-BHVM`'s `root-cause-of:` and now grouped together as well; the group closes
when `stranded` makes that comparison.

---

**Done 2026-09-21, with `PL-KSCW`, as one predicate.** `vcs._standing` reads
two copies of one item file and answers `ahead`, `behind` or `equal` from
content alone - no date, no commit count, no ancestry, since this runs against
refs a shallow clone holds no history for. `stranded` and `orphaned` both read
it, so the two halves of the defect close together:

- `orphaned` no longer offers a `git checkout` of a copy the base has closed
  since. `_behind_on_base` is the narrowing `_superseded` cannot make: that
  read is a two-dot diff, so the branch's older `status: untriaged` line is an
  *addition* and the path stays outstanding, which is exactly how `PL-THPB`
  came to be offered.
- `stranded` gained the other direction, which is `PL-KSCW`: an item the base
  holds whose branch copy is **ahead** is reported in a section of its own,
  with a `git diff` to read and no checkout line anywhere in it.

**The three-valued predicate needed more evidence than the design round
assumed**, which is the one place `PL-BHVM`'s ratification flagged as untested
and it was right to. Blob identity alone does not separate ahead from behind:
judged on text alone, 873 of this repository's branch copies read as ahead on
2026-09-21. Three filters in cost order settle it - the ref's blob equal to the
base's (24,829 of 27,009 ref-and-item pairs), a blob the base's history has
held (2,158 more, and correctly rather than merely cheaply, since the base
rewriting its own prose leaves the ref holding lines the base lacks), then the
text of the 15 that survive. Measured cost of the whole read: 0.35 s, against
13.4 s without the blob filter. What it reports today is 7 branch copies
carrying real unmerged prose, among them a ratified project-owner decision on
`PL-DMDF` that reached no other report.

**The closure carve-out is the part most likely to be wrong**, and the number
it rests on is 2 reopenings in 1,377 items across this store's whole history,
both in one commit - replayed over all 889 commits touching `docs/items/` on
`main`. A branch reopening an item the base closed is what it would hide.
