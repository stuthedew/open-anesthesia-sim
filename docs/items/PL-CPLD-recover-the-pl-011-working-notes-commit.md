---
id: PL-CPLD
title: Recover the PL-011 WORKING_NOTES commit stranded on origin/claude/next-item-75htc6 after that branch's pull request merged
priority: P2
effort: S
status: dropped
classes: infra
touches: docs/WORKING_NOTES.md
added: 2026-09-05
closed: 2026-09-12
reason: both halves done elsewhere: the numpy note reached main via PL-VSJZ (#360), and origin/claude/next-item-75htc6 no longer exists on the remote, so there is no ref left to clear
not-delegable: What is left is deleting a branch on GitHub, which is not a
  change to this repository, so nothing in the tree can prove it. Every
  in-checkout test of the ref passes vacuously wherever the ref was never
  fetched - which is every fresh clone, CI included - so a command here would
  accept a branch that did none of the work. `git ls-remote` would answer, and
  is a network call this project's tools are contracted not to need.
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

**Half of this landed elsewhere, 2026-09-05.** `PL-VSJZ` (recover the seven
items stranded on abandoned branches, #360, `15f07c6`) took the same file off
the same branch while this item sat untriaged, so the note is on `main` at
`docs/WORKING_NOTES.md` § "Decided: no numpy, and the reason is fit rather
than dependency avoidance". Nothing is lost and the first half of the
**Done when** below is met.

What remains is the ref. `bin/docket stranded` still names
`origin/claude/next-item-75htc6`, because it compares commit reachability
rather than content and `75b248a37` is still an ancestor of nothing on `main`.
The branch now carries no unique work, so deleting it by name is safe in a way
it was not when this item was filed.

**This item has now had two `verify:` commands withdrawn, and the second is
the more instructive.**

The first paired `doc_check` with `grep -q 'no numpy' docs/WORKING_NOTES.md`.
It failed at exit 1 when written and passed at exit 0 the moment #360 merged,
so it stopped discriminating between a finished item and an unstarted one.

The second, `test -z "$(git branch -r --list
'origin/claude/next-item-75htc6')"`, was written to test the half still owed
and *did* fail at exit 1 in the checkout it was written in. It was still
wrong, and `docket check --verify` caught it on #364: a fresh clone never
fetched that ref, so the test finds nothing and passes **vacuously**. It
proved only that the session writing it happened to hold a stale ref. Running
a command and watching it fail is necessary and, here, not sufficient - the
run has to fail for a reason that will still exist in a checkout that is not
this one.

So the field is now `not-delegable:`. The remaining work is a branch deletion
on GitHub, and no command in this tree can observe it; `PL-W9DW` reached the
same answer the same day for a GitHub billing setting.

**Done when.** The note is on `main` — it is — and the stale ref is gone.

**Dropped 2026-09-12**, by the workflow-lane consolidation pass (`PL-6ZQY`).
The premise was checked against the tree by an adversarial reviewer whose
default was to refuse, and it did not survive:

> Both halves of "Done when" are met, neither by this item. The note is on `main`: `docs/WORKING_NOTES.md` § "Decided: no numpy, and the reason is fit rather than dependency avoidance (2026-09-05)", landed by `PL-VSJZ` (#360, `15f07c6`) off the same branch. The stale ref is gone too — `git ls-remote --heads origin 'refs/heads/claude/next-item-75htc6'` returns empty (verified 2026-09-12, 6 heads on the remote, none of them this branch), this checkout holds no matching remote-tracking ref, and `bin/docket stranded` no longer names it. The GitHub-side deletion this item was waiting on (`PL-TFWR`, a session cannot delete a remote branch) has already happened, so there is no work left here and no handover owed to the project owner.

What the file keeps that exists nowhere else, which is why it is dropped rather
than deleted: Nothing, provided the drop is recorded the project's way (file kept, `status: dropped` plus a `reason`) rather than by deleting the file. PL-CPLD's only unique content is commit 75b248a37, the branch name origin/claude/next-item-75htc6, and the two-withdrawn-`verify:`-commands account — all of which survive in the retained file. What the reason AS WRITTEN loses is accuracy, and that has a cost of its own: it would leave a permanent record claiming an outstanding owner action (delete a branch on 

