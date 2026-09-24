---
id: PL-H14W
title: A claimed captures-only pull request opens at the first push as an ordinary mergeable one titled for the work, so #978 was merged six minutes in while the v0.5.9 cut was being written, erasing the start claim with the branch and leaving a subject on main that names a cut it does not contain
priority: P2
effort: S
status: needs-decision
classes: defect
feature: parallel-sessions
touches: CLAUDE.md, docs/maintainer.md, .claude/skills/docket/modes/start.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-24 triage pass
added: 2026-09-24
payoff: a claimed capture's pull request cannot be merged by hand while its claimed work is unfinished
---

**Problem.** A claimed captures-only pull request opens at the first push as an ordinary mergeable one titled for the work, so #978 was merged six minutes in while the v0.5.9 cut was being written, erasing the start claim with the branch and leaving a subject on main that names a cut it does not contain

**What happened, 2026-09-24.** The v0.5.9 cut's session filed `PL-R498`, then
pushed its capture and the empty `PL-R498: start` claim together. `CLAUDE.md`'s
commit-and-push bullet says a branch carrying only item files opens its pull
request at that first push and that a claim leaves it unarmed, so `#978` opened
at 00:36:59Z, not a draft, titled "PL-R498: cut v0.5.9 from the 27 items
finished since v0.5.8". It merged at 00:43:14Z under the project owner's
account, with the cut still uncommitted in the session's checkout. The session
armed nothing and no workflow arms auto-merge, so it was merged by hand or
armed from the owner's side. GitHub deleted the branch. The squash folded the
claim into `8428844c`, whose subject names a cut it does not contain, and
`main`'s copy of the item read `ready` with no pushed ref claiming it until
the session re-claimed it at 00:45:51Z on a branch restarted from `main`.

This is `PL-QP9Z`'s outcome through a different merger. `PL-QP9Z`, `PL-1MCK`
and `PL-KWCY` each closed a way auto-merge could land a claimed captures-only
branch, and none of them reaches a person merging an open, green, non-draft
pull request whose title reads as the finished work. Remedies to weigh, none
decided: open such a pull request as a draft while a claim rides it and mark it
ready when the claimed item closes, which GitHub then refuses to merge before;
open none while a claim rides the branch; or title it as the capture it is.
Whether this is a member of the who-holds-an-item head, `PL-MB2W`, whose design
round was running on 2026-09-24, is that round's call.

**Premise re-checked at triage, 2026-09-24.** No code opens a pull request or
arms auto-merge; both are written rules in prose.

- `CLAUDE.md`'s commit-and-push bullet is the rule for sessions.
- `docs/maintainer.md` tells the owner to merge when the page offers "Squash
  and merge". It makes no exception for a pull request left unarmed because a
  claim rides it.
- `claiming._publish` prints "Disarm auto-merge if it is armed, then push".
  It cannot stop a merge by hand.

`#978` was not a draft and had no auto-merge. The owner merged it six minutes
after it opened.

**Why it matters.** The merge erases the claim with the branch. It also puts a
subject on `main` naming work the commit does not contain. So the item reads
as unheld while its session is still working it. `PL-QP9Z`, `PL-1MCK` and
`PL-KWCY` closed this outcome for auto-merge; `#978` reached it through the
other merger.

**Decision needed.** There are three remedies for a captures-only pull request
that a claim rides:

1. Open it as a draft, and mark it ready when the claimed item closes or is
   blocked.
2. Open no pull request while a claim rides.
3. Title it as the capture it is.

Any of them reopens a ratified rule, `CLAUDE.md`'s "A branch carrying only item
files opens its pull request at its first push" (project owner, 2026-09-23,
ratified), on the ordinary evidence of `#978`. It also changes
`docs/maintainer.md`, the owner's own merge procedure. So the answer is the
owner's.

**Recommended: the draft.**

- **It prevents the merge rather than warning against it.** GitHub will not
  merge a draft pull request (GitHub Docs, "About pull requests" § "Draft pull
  requests"; not re-read this session).
- **The capture stays visible as a pull request.** That visibility is what the
  ratified rule bought.
- **A session can do both halves.** The GitHub tools these sessions use take
  `draft` on create and `draft: false` on update (checked 2026-09-24).
- **The other two are weaker.** Opening none loses the visibility. A capture
  title only works if the merger reads it, and `#978`'s title already went
  unread.

The cost is one clause in `CLAUDE.md`'s bullet, one in `docs/maintainer.md`,
and one step in `.claude/skills/docket/modes/start.md`.

**Done when.** The chosen remedy is written into `CLAUDE.md`,
`docs/maintainer.md` and the start mode, so that a claimed captures-only pull
request cannot be merged by hand before its claim closes.

**Generator check.** The merger misread who held the item. The pull request's
title and state said the work was finished while a claim rode it. That is
`PL-MB2W`'s fact. `PL-MB2W` is still open and `live`, and it already lists
`PL-QP9Z`, `PL-1MCK` and `PL-KWCY`, so this reads as a new member. It is not
added to `PL-MB2W`'s `root-cause-of:` in this pass, because that file is in the
path of the two sessions now building its blockers.
