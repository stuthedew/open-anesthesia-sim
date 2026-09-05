---
id: PL-NT6G
title: A pull request cannot converge while main moves, because auto-merge updates the branch only once
status: untriaged
added: 2026-09-05
---

**Problem.** #342 was opened at 03:20 and had still not merged eight hours
later, having taken three base merges from this session on top of one from
GitHub. The sequence, all against one pull request:

| When | What moved | Who merged it |
| --- | --- | --- |
| 03:26 | branch update after auto-merge was enabled | GitHub |
| 03:29 | #336, #340, #341 | this session |
| 10:42 | #343 | this session |
| ~11:00 | #339 | this session |

GitHub's auto-merge updated the branch **once**, when it was enabled, and
never again. Every later movement of `main` left the pull request at
`mergeable_state: behind`, where it sits indefinitely: auto-merge will not
merge a branch that is behind, and does not re-update it.

**Why it matters.** The loop does not obviously terminate. Each round costs a
merge plus a full CI run - `checks` is around six minutes - and this repository
routinely has five or six sessions pushing at once, so `main` can move again
inside that window. #342 lost three rounds to it. The cost is paid by every
parallel pull request, not by this one, which is what makes it worth a look
rather than an annoyance: it is a property of how work merges here, and the
number of concurrent sessions is the thing that decides it.

Nothing is silently wrong - `behind` is visible, CI is honest, and no incorrect
state can land this way. That is why this is filed rather than raised as
compounding friction under `CLAUDE.md`'s three tests.

**Where.** Repository settings rather than the tree: the branch-protection
rule on `main` requiring branches to be up to date before merging, and whether
GitHub's merge queue should be enabled for the repository.

**The options, none of them decided.** Only the project owner can act on any
of these; they are recorded so the question is not reconstructed next time.

1. **Do nothing.** A session merges `main` each round, as this one did. Works,
   and can lose an unbounded number of rounds when several sessions are
   pushing.
2. **Merge the pull request by hand** when it stalls. One click, and it is what
   ended #342's loop if that is how it closed. Does not scale to a session
   working unattended.
3. **Enable the merge queue** on `main`. This is the mechanism GitHub built for
   exactly this - it batches, tests and merges in order, so a pull request
   stops racing the base. Costs a settings change and a CI run per queued
   entry.
4. **Drop the up-to-date requirement** from the branch-protection rule. Removes
   the stall outright and gives up the guarantee that `main` was green with the
   change applied, which for a repository with a 100%-coverage gate on the
   scientific core is the wrong thing to trade away cheaply.

**Done when.** The queue records which of the four was chosen and why, and if
it is 3 or 4, the repository setting matches.
