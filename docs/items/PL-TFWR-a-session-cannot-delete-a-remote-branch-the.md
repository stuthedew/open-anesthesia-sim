---
id: PL-TFWR
title: "A session cannot delete a remote branch: the push ends on Everything up-to-date having deleted nothing, so every branch cleanup has to be handed to the project owner"
priority: P2
effort: S
status: dropped
classes: infra, docs
feature: dev-tooling
touches: CLAUDE.md, .claude/skills/docket/SKILL.md
added: 2026-09-04
closed: 2026-09-19
reason: Superseded by docs/worker.md's "Ref operations a session cannot perform", written under PL-4Q9B, which states both operations a session cannot perform in one place and carries this item's two distinctive points - re-read git ls-remote before reporting either done, and there is no second route. Its remaining deliverable was a CLAUDE.md line, deliberately not added: CLAUDE.md is resident in every session and the routing ladder puts a document that loads on demand above resident prose for a rule read when a procedure is composed.
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

The same session had just pushed a branch and opened a pull request against the
same remote, and `curl "$HTTPS_PROXY/__agentproxy/status"` reported
`enabled: true` with an empty `recentRelayFailures`. **Those are the
observations; the mechanism this item originally inferred from them - that the
deletion ref is dropped in transit, and that neither credentials nor the proxy
are involved - is struck, 2026-09-19, under `PL-3V6C`.** An empty
`recentRelayFailures` does not exonerate the proxy, because a request declined
on policy is not a relay failure; and `PL-XQRK` measured the same operation the
same day and recorded an HTTP 403, which cannot be true at the same time as a
silent drop. What is established is the symptom in the transcript above: git
reports `Everything up-to-date` and the branch is still there. The GitHub MCP
server offers `create_branch` and `list_branches` but no branch deletion, so
there is no second route either.

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

**Dropped 2026-09-19 under `PL-4Q9B`** (record clone trust and the permitted ref
operations), as superseded rather than as wrong. See `reason:` above.

**The cause this item asserts is not established, and the title carries it
too.** Per `PL-3V6C`: "the deletion ref appears to be dropped on the way
through" is an inference, not a measurement, and the empty
`recentRelayFailures` offered against the proxy does not support it - a request
declined on policy is not a relay failure, and `/root/.ccr/README.md` lists 403
among the proxy's own outcomes. `PL-XQRK` measured the same operation the same
day and recorded an HTTP 403 instead. At most one of the two is what this
project meets, and nothing has established which. What this item measured and
what is safe to carry forward is the *symptom*: the push ends on `Everything
up-to-date` having deleted nothing. That is what `docs/worker.md` now says.
