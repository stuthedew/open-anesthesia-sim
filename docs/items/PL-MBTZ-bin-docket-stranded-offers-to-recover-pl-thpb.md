---
id: PL-MBTZ
title: bin/docket stranded offers to recover PL-THPB from origin/claude/next-version-release-o2zzaf, where the branch's copy is older than main's: the recover line would overwrite a done item with an untriaged one
status: untriaged
added: 2026-09-14
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
