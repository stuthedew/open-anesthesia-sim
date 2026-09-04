---
id: PL-TFWR
title: "A session cannot delete a remote branch: the git proxy drops the deletion ref, so every branch cleanup has to be handed to the project owner"
status: untriaged
added: 2026-09-04
---

**Problem.** `git push origin --delete <branch>` and `git push origin :<branch>`
both fail from an agent session in this environment. Measured 2026-09-04 while
closing `PL-JX2T`:

```
$ git push origin --delete Review_articles
send-pack: unexpected disconnect while reading sideband packet
fatal: the remote end hung up unexpectedly
Everything up-to-date
```

Not a permissions problem — the same session had just pushed a branch and
opened a pull request against the same remote — and not the proxy being
unhealthy: `curl "$HTTPS_PROXY/__agentproxy/status"` reported `enabled: true`
with an empty `recentRelayFailures`. The deletion ref appears to be dropped on
the way through, after which git reports `Everything up-to-date` because there
is nothing left in the push. The GitHub MCP server offers `create_branch` and
`list_branches` but no branch deletion, so there is no second route either.

**Why it matters.** Two of this repository's own workflows assume branches can
be cleaned up. `CLAUDE.md`'s stale-ref rule prescribes `git branch -dr` for the
*local* ref and is silent on the remote one, which is the half that actually
strands work; `bin/docket stranded` recovers an item off a dead branch but
cannot remove the branch afterwards. And the failure is quiet in the worst way:
exit status 0, with `Everything up-to-date` as the last line, so a session that
does not read the two lines above it will report the branch deleted when it is
still there.

That is the part worth fixing whatever else is decided — a session must not be
able to believe it deleted a branch it did not.

**Where.** `CLAUDE.md`'s branch-hygiene bullet and `.claude/skills/docket/SKILL.md`
are where the expectation is set. Whether anything deterministic belongs here is
open: a check would have to reach the network, which every tool in `tools/`
deliberately avoids.

**The common case is already covered, which is what makes this narrow.** GitHub's
automatic head-branch deletion on merge is evidently on for this repository:
`claude/unfiled-housekeeping-item-id-a36q1s` was gone from `git ls-remote --heads
origin` immediately after each of #296 and #298 merged, with no session having
touched the remote ref. So every branch that reaches a merged pull request cleans
itself up. What is left is the branch that never had one — `Review_articles` is
the case in point, and `PL-1Q3S`'s never-pushed and abandoned refs are the rest
of the family.

**Two things worth doing, and they are independent.** Say in the instructions
that remote deletion is the owner's action, with the steps to hand over rather
than the intent: the repository's branches page, or `git push origin --delete
<branch>` from their own machine, or `gh api -X DELETE
repos/{owner}/{repo}/git/refs/heads/{branch}`. And make the silent failure
loud — a session that attempts the push must re-read `git ls-remote` before
reporting anything, because exit status 0 and `Everything up-to-date` are what
it gets when nothing happened.

**Done when.** A session that needs a remote branch deleted knows it cannot do
it, does not report success when the push silently no-ops, and hands the owner
steps rather than intent.
