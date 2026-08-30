---
id: PL-FY68
title: A session pushes its branch before the discussion has settled, leaving stale remote branches
priority: P2
effort: S
status: done
classes: defect
feature: worker-instructions
milestone: v0.2.7
touches: CLAUDE.md, docs/worker.md
added: 2026-08-30
closed: 2026-08-30
commit: 3078bdb
---

**Problem.** Nothing tells a session when to push. A session that opens as a
discussion pushes as soon as it has anything committed, so a conversation that
ends without work landing leaves a remote branch behind. The project owner
raised this: wait until the discussion is done, and ask before pushing, so that
discussion and design can run in chat without accumulating branches that a
concurrent session then has to reason about.

**The controllable act is the push, not the branch.** A web session's branch is
created by the harness before the session starts - `CLAUDE.md` already notes it
cannot even be renamed - so "wait to create a branch" is not available to the
session. What it controls is whether that branch ever reaches the remote. An
unpushed branch is invisible to other sessions and costs nothing; a pushed one
is clutter until it merges.

**The tension to resolve, not ignore.** Holding the push has a real cost: the
container is ephemeral, and the docket skill already says an uncommitted
thought is one interruption from gone. A rule that simply defers pushing trades
stale branches for lost work, which is the worse of the two.

The split that resolves it is the one `CLAUDE.md` already draws between the
owner's two modes. Capture - a queue item, a finding, anything recorded so it
survives - commits and pushes immediately, because losing an idea is the worst
outcome available and the skill says so outright. Implementation still under
discussion commits locally and holds the push until the shape has settled, then
asks. Committing is never deferred either way; only the push is.

**Where.** `CLAUDE.md`'s session guidance, and `docs/worker.md` if the rule
should differ for a worker session doing already-specified work - a worker has
no discussion to settle, so it probably pushes as it always has.

**Done when.** `CLAUDE.md` says when a session pushes and when it asks first,
distinguishes capture from implementation, and says explicitly that local
commits are not deferred by the rule.
