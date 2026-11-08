---
id: PL-J3TV
title: .claude/hooks/no-prune-guard.sh still prints the pre-PL-K2C8 three-command restart recipe, so the incomplete version survives in the louder of the two places - the message a session reads at the moment it is refused a prune
priority: P2
effort: S
status: done
classes: defect, docs
feature: parallel-sessions
milestone: v0.5.19
touches: .claude/hooks/no-prune-guard.sh
added: 2026-09-21
closed: 2026-09-30
pr: 1238
payoff: a session refused a prune reads the recipe that finishes the job, instead of the one PL-K2C8 found incomplete
verify: grep -qE 'push origin --delete|modes/capture\.md' .claude/hooks/no-prune-guard.sh
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

**The message is one Python string split across source lines, which is a trap
for the fix and was one for this item's first `verify:` command.** The sentence
reads `"To restart a branch whose pull request has already merged, delete just "`
then `"that one ref and rebase the name onto the merged base:\n\n"`, so
`grep` for any phrase spanning the break finds nothing. The first command
recorded here was `! grep -q 'delete just that one ref' ...`, which passed
against the unfixed hook for exactly that reason - caught by
`bin/docket check --verify` on `#830`, not by a reader. The command now asserts
a string the *fix* adds rather than one it removes: either `push origin
--delete`, if the hook carries the four-command block, or `modes/capture.md`,
if it points at the skill as the one place the recipe lives. Both are the
endings this item's **Done when** allows, and neither string is in the file
today.


**Resolution, 2026-09-30 (`#1238`).** Both of the brief's open choices were
taken as obvious calls:

- **The hook keeps its three commands inline rather than pointing at the skill
  file.** Its deny message exists to answer the refused session at that moment
  (the hook's own header), and `tests/unit/test_no_prune_guard.py` pins those
  commands in the prune, section-rename, prune-and-mirror and branch-delete
  reasons, so pointing away would have changed a tested contract to fix a
  message. The drift the brief names is answered by a header note naming the
  skill's copy and asking that the two be kept in step.
- **"delete just that one ref" is gone.** The message now says `git branch -dr`
  clears the ref in this clone and nothing else, and says who deletes the
  branch on the remote as the tree now has it: GitHub at the merge,
  `branch-sweep.yml` daily for a finished `claude/*` branch (`PL-X8SV`, which
  postdates this brief), and the project owner for one the sweep keeps, with
  `git push origin --delete <branch>` on one source line so a grep finds it. A
  session's own push of that is refused (`docs/worker.md` § "Ref operations a
  session cannot perform").

No test was added: the change is message text, the 215 hook tests pass
unchanged, and this item's `verify:` asserts the added string. The skill's
copy of the recipe predates `PL-X8SV` too, and still hands every remote
deletion to the owner; that is `PL-ZZHZ`, filed rather than widened here.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground".

> **And one from the re-judging pass over those same clusters** (2026-09-21). `PL-J3TV` is the live half of `PL-8T3Z`. `PL-PT7M` dropped `PL-8T3Z` under the closed-brief clause of `.claude/rules/citation-drift.md`, because that item asked for the `touches` of a `done` item to be corrected. The finding underneath it is still real. `.claude/hooks/no-prune-guard.sh` still prints the three-command restart recipe that `PL-K2C8` replaced. It prints that recipe at the one moment when a session is certainly about to run it, which is when the hook refuses a prune. It is debt here because it is a `defect`. It is wholly in the workflow lane, since it is a hook message that no reader of the simulator ever sees. It was captured fifteen days after this gate froze. The arithmetic above about the refilling queue is unchanged. `PL-G8TR` is already on this list for the same file and the same message, so whoever takes either item should take both.

<!-- absent: .claude/hooks/no-prune-guard.sh -->

> - PL-J3TV (S) `.claude/hooks/no-prune-guard.sh` still prints the pre-`PL-K2C8` three-command restart recipe, so the incomplete version survives in the louder of the two places

<!-- absent: .claude/hooks/no-prune-guard.sh -->
