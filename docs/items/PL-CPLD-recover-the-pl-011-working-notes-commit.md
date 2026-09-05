---
id: PL-CPLD
title: Recover the PL-011 WORKING_NOTES commit stranded on origin/claude/next-item-75htc6 after that branch's pull request merged
status: untriaged
added: 2026-09-05
---
**Problem.** `bin/docket stranded` reports `origin/claude/next-item-75htc6` as
a branch whose pull request already took the rest of its work, leaving commit
`75b248a37` (`PL-011: record why the compaction does not want numpy`,
`docs/WORKING_NOTES.md`) merged by nothing and reported by nothing else.

**Why it matters.** It is a note about `PL-011`'s retention design - why the
compaction does not want numpy - written by the session that had the context,
and `PL-011` is now the first entry v0.4.1 owes (carried out of v0.4.0's
Required scope at the 2026-09-05 cut). Losing it means the next session
re-derives the reasoning or, worse, re-litigates a decision already taken.

**Where.** `docs/WORKING_NOTES.md`; the branch is `origin/claude/next-item-75htc6`.

**Approach.** The skill's recovery for this case, not a push to the merged
branch:

```
git checkout origin/claude/next-item-75htc6 -- docs/WORKING_NOTES.md
git branch -dr origin/claude/next-item-75htc6
```

Then commit the note under this item's id. Delete that one ref **by name** -
never `git fetch --prune`, which `.claude/hooks/no-prune-guard.sh` refuses,
because a stale ref can be the only surviving copy of an item.

**Done when.** The note is on `main` and the stale ref is gone.
