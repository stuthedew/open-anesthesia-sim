---
id: PL-J3TV
title: .claude/hooks/no-prune-guard.sh still prints the pre-PL-K2C8 three-command restart recipe, so the incomplete version survives in the louder of the two places - the message a session reads at the moment it is refused a prune
priority: P2
effort: S
status: ready
classes: defect, docs
feature: parallel-sessions
touches: .claude/hooks/no-prune-guard.sh
added: 2026-09-21
payoff: a session refused a prune reads the recipe that finishes the job, instead of the one PL-K2C8 found incomplete
verify: ! grep -q "delete just that one ref" .claude/hooks/no-prune-guard.sh
---

**Problem.** .claude/hooks/no-prune-guard.sh still prints the pre-PL-K2C8 three-command restart recipe, so the incomplete version survives in the louder of the two places - the message a session reads at the moment it is refused a prune

**Why it matters.** `PL-K2C8` established that `git branch -dr` clears this
clone's remote-tracking ref and nothing else, so where the branch still exists
on the remote the next `git fetch origin` recreates it: the deletion does not
survive the next fetch, `bin/docket stranded` names the branch again, and the
next session repeats the whole recovery. It fixed the skill
(`.claude/skills/docket/modes/capture.md`, which now leads with
`git push origin --delete "$BRANCH"` and says that command is the project
owner's) and closed 2026-09-13 in v0.4.21. The hook was never touched.

The hook is the louder of the two places. `.claude/skills/docket/modes/capture.md`
is read by a session that has chosen to read it; `.claude/hooks/no-prune-guard.sh`
prints its message *into the transcript* at the moment a session is refused a
prune - the one moment the recovery is certainly about to be run. So the
incomplete recipe survives exactly where it is most likely to be followed, and
the complete one sits in the file nobody opened.

**Where.** `.claude/hooks/no-prune-guard.sh`, the `reason` string: "To restart a
branch whose pull request has already merged, delete just that one ref and
rebase the name onto the merged base", followed by `git branch -dr
origin/<branch>`, `git fetch origin main`, `git checkout -B <branch>
origin/main`. Compare with `.claude/skills/docket/modes/capture.md`'s four-command
block and the paragraph under it.

**Two things to decide while fixing it**, neither large: whether the hook
repeats the four commands or points at the skill file (a second copy is a
second thing to drift - `PL-K2C8`'s own fix drifted *because* there were two),
and whether the hook's phrase "delete just that one ref" survives at all, since
it is the sentence that reads as if `branch -dr` finished the job.

**Done when.** A session refused a prune is not told to run a recipe the project
has already found incomplete: the hook's message either carries the remote
deletion with the note that it is the project owner's to run, or names the skill
file as the one place the recipe lives - and nothing in `.claude/hooks/` still
describes `git branch -dr` as deleting the branch.

**Where it came from.** `PL-PT7M`'s re-judging pass, 2026-09-21. This is the
live half of `PL-8T3Z`, which was dropped: that item asked for `PL-K2C8`'s
`touches` and `Where` to be corrected, and `PL-K2C8` is `done`, so
`.claude/rules/citation-drift.md`'s closed-brief clause refuses the deliverable
as written. The finding underneath it - that the hook carries the same
incomplete recipe - is in a live file and is not refused by anything, so it is
re-filed here under a title that names it.

**`PL-G8TR` is the other open finding against this file, and the two want
landing together.** It says the guard is evaded by the form its own message
recommends - `git branch -dr` driven from a generated list computes and deletes
exactly the set `--prune` would. That is a defect in what the hook *refuses*;
this is a defect in what it *prints*. Both are in the `reason` string's advice,
one session opening the file can settle both, and fixing either alone leaves a
message that is half right. `PL-G8TR` also declares
`tests/unit/test_no_prune_guard.py`, which is where a test for this belongs
too.

