---
id: PL-1Q3S
title: A merged PR leaves a stale tracking ref, so the stop hook demands a push that would recreate a dead branch
priority: P2
effort: S
status: ready
classes: infra, session-cost
feature: dev-tooling
touches: CLAUDE.md, docs/worker.md
added: 2026-08-30
not-delegable: the hook itself is `~/.claude/stop-hook-git-check.sh`, outside the repository and outside any session's reach. Only the repo-side habit can be fixed here, and confirming the hook then passes means ending a session, which no check can run beforehand.
---

**Problem.** GitHub deletes the head branch when a pull request merges, but a
session's *local* remote-tracking ref for it survives until something prunes.
`~/.claude/stop-hook-git-check.sh` picks its comparison point with

    if git rev-parse "origin/$current_branch" >/dev/null 2>&1; then
      upstream="origin/$current_branch"

which tests whether the ref *resolves locally*, not whether the branch still
exists on the remote. So after a merge it keeps comparing against the deleted
branch's last-pushed tip, and every commit that has landed on `main` since
counts as unpushed.

Observed 2026-08-30: after PR #85 merged and the branch was restarted from
`main`, the hook reported "There are 23 unpushed commit(s)". The branch was
identical to `origin/main`, with a clean tree and nothing of its own. All 23
were already on `main`.

**Why it matters.** The instruction is not merely noise - obeying it is worse
than ignoring it. Pushing recreates a branch identical to `main`, with no
content and no pull request, which is precisely the clutter `CLAUDE.md`'s
"commit as you go; ask before the first push" rule exists to prevent, and which
a concurrent session then has to reason about. A session that trusts the hook
does the wrong thing; one that does not trust it spends a turn proving the hook
wrong. This fires after *every* merged pull request, which in this project is
several per session.

It also compounds with the session-start digest, which correctly says the
branch "is 23 behind origin/main with nothing of its own" and tells the session
to restart it from `main`. Following that advice is what leaves the stale ref
pointing at the old tip, so the two mechanisms disagree about the same branch
in the same session.

**Where.** The hook is `~/.claude/stop-hook-git-check.sh`, outside the
repository and not editable from a session. What is fixable here is the habit:
`CLAUDE.md`'s push rule, or `docs/worker.md`, should say to run
`git fetch --prune` when restarting a branch whose pull request has merged.

**Fix.** `git fetch --prune origin` drops the stale ref. The hook then finds no
`origin/<branch>`, falls back to `origin/HEAD`, and - where that does not
resolve either, as in this container - its `|| unpushed=0` guard passes
cleanly. Verified in this session: before the prune the ref pointed at
`8fae027`, the pre-merge tip; after it, the ref was gone, the tree was clean
and `HEAD` equalled `origin/main`.

**Upstream half, recorded but not actionable here.** The hook's real defect is
testing local resolvability rather than remote existence. `git rev-list
"$upstream..HEAD"` against a deleted branch's tip can only ever overcount. That
belongs upstream in Claude Code, not in this repository, and is recorded here
only so the next session that meets the message recognizes it instead of
re-diagnosing it.

**Done when.** The rule to prune when restarting a merged branch is written
where a session will read it before it pushes, and the reason - that obeying
the hook would recreate a dead branch - is stated alongside it, so a session
does not "helpfully" push anyway.
