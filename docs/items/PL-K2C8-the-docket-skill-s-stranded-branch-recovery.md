---
id: PL-K2C8
title: The docket skill's stranded-branch recovery deletes only the local remote-tracking ref, which the next non-prune fetch restores while the branch still exists on the remote
priority: P2
effort: S
status: ready
classes: defect, infra
touches: .claude/skills/docket/SKILL.md, docs/items
added: 2026-09-05
verify: grep -q 'push origin --delete' .claude/skills/docket/SKILL.md
---

**Problem.** `.claude/skills/docket/SKILL.md` § "Mode: capture" gives the
recovery for a branch whose pull request already took part of its work:

```
git branch -dr origin/<branch>
git fetch origin main
git checkout -B <branch> origin/main
```

`git branch -dr` deletes the **local remote-tracking ref** and nothing else.
Where the branch still exists on the remote, the next `git fetch origin`
recreates it under the default refspec `+refs/heads/*:refs/remotes/origin/*`,
so the deletion does not survive the next session - or the next command in the
same session.

**Measured, 2026-09-05.** `origin/claude/next-item-75htc6` is the live
instance. `git ls-remote --heads origin claude/next-item-75htc6` returns
`75b248a37 refs/heads/claude/next-item-75htc6`: the branch is still on GitHub,
so the ref this repository keeps trying to clear is a true reflection of the
remote rather than a stale leftover.

**Why it matters.** A session that runs the recorded three commands, sees the
ref gone from `git branch -r`, and reports the recovery complete has reported
something that stops being true at the next fetch. `bin/docket stranded` then
names the branch again, and the next session repeats the whole recovery -
which is the re-discovery loop `CLAUDE.md`'s housekeeping rule exists to stop,
arriving through the procedure rather than through the absence of one.

It also silently weakens the prohibition beside it. The skill forbids `git
fetch --prune` because a stale ref can be the only surviving copy of an item,
and `.claude/hooks/no-prune-guard.sh` enforces it. That reasoning assumes the
by-name deletion is the safe *equivalent*. It is not equivalent: prune and
`branch -dr` both clear local refs, and neither touches the remote, so the
procedure has no step that finishes the job.

**Where.** `.claude/skills/docket/SKILL.md`, the recovery block in
§ "Mode: capture"; `docs/items/PL-CPLD-*.md`, whose **Approach.** quotes the
same two commands.

**Approach.** Add the remote deletion as an explicit step, and say which of
the two commands does what:

```
git push origin --delete <branch>     # the branch itself
git branch -dr origin/<branch>        # the local remote-tracking ref
```

Deleting the remote branch is destructive and outward-facing, so it is the one
step in this procedure that is not a session's to take unasked - say so, and
leave it to the project owner. Deciding whether that ordering is right, and
whether `stranded` should say which of the two states it is looking at, is
`PL-39B7`'s question rather than this one's.

**Done when.** The skill's recovery block names the remote deletion,
distinguishes it from the local ref deletion, and states that the remote half
is the project owner's to run.
