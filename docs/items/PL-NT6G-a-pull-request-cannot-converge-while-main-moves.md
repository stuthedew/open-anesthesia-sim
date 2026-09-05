---
id: PL-NT6G
title: A pull request cannot converge while main moves, because auto-merge updates the branch only once
priority: P2
effort: S
status: needs-decision
classes: infra
feature: parallel-sessions
touches: .github/workflows/quality.yml
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

**Decision needed.** Which of the four below governs how a pull request here
reaches a green, up-to-date head while `main` keeps moving - and it is a
question about the repository's settings, so nobody but the project owner can
answer it. The recommendation from this brief is 3, the merge queue: it is the
mechanism GitHub built for this shape, and 1 and 2 both scale with the number of
concurrent sessions, which is the thing that has been growing.

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

**Option 3 is not available to this repository, checked 2026-09-05.** GitHub's
merge queue runs in public repositories owned by an organization, and in
private repositories only for organizations on GitHub Enterprise Cloud. This
repository is owned by a **user account** (`"type": "User"` on the repository's
owner, read from the API) and is **private** (`"visibility": "private"`), so
neither route applies. The recommendation this brief carried - "3, the merge
queue: it is the mechanism GitHub built for this shape" - cannot be acted on
without moving the repository to an organization on that plan, which is a
larger decision than the stall it would fix.

Source: GitHub Docs, *Managing a merge queue*
(https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue).
Read via search results rather than fetched directly - `docs.github.com` is
blocked by this container's egress proxy - so confirm the plan wording before
acting if the answer turns on it.

**So the live field is 1, 2 and 4**, and 4 has an argument the brief did not
give it. "Require branches to be up to date before merging" buys the guarantee
that `main` was green *with the change applied*. That guarantee is already
weaker here than it looks: `quality.yml` runs on `pull_request`, which tests
the **merge result** rather than the branch head, so every pull request is
already checked against the base it would land on at the moment it was pushed.
What the setting adds is that the base has not moved *since*. Against that,
`PL-NT6G` records #342 losing three rounds and eight hours to it, at a full CI
run each.

Still `needs-decision`, and still the project owner's alone: dropping it trades
a real guarantee for throughput, and the 100%-coverage gate on the scientific
core is what makes that trade worth thinking about rather than obvious.

**Two cheaper mitigations exist either way**, neither of which needs a setting
changed. GitHub's *Update branch* button on a stalled pull request is one
click and one CI run, which is option 2 without waiting for a human to be
looking; and this container's `git merge origin/main` is what sessions already
do. Both were used on this branch today.
