---
id: PL-XQRK
title: A session cannot delete a remote branch, so every cleanup pass ends on the owner's desk without saying so up front
priority: P3
effort: S
status: done
classes: docs, infra
feature: worker-instructions
touches: docs/worker.md
verify: python3 tools/doc_check.py check && grep -q 'cannot delete a remote branch' docs/worker.md
added: 2026-09-04
closed: 2026-09-19
---

**Problem.** `git push origin --delete <branch>` fails with `HTTP 403` from a
remote session. Measured 2026-09-04 against five branches; the agent proxy
reported `recentRelayFailures: []`. **The mechanism this item originally
inferred from that - GitHub refusing the ref deletion on a token carrying no
`delete_ref` permission, rather than the proxy - is struck, 2026-09-19, under
`PL-3V6C`**, and the note at the end says why. The `HTTP 403` above is what was
observed.
The GitHub MCP server offers `create_branch` and `list_branches` and **no**
delete-branch tool, so there is no second route either.

**Why it matters.** Branch cleanup looks like ordinary housekeeping a session
can finish, and it is not. The recovery half - reading what a branch uniquely
carries and landing it on `main` so nothing is lost - *is* a session's work and
is the part that actually matters, since a tracking ref can be the only copy of
a captured item (`PL-1Q3S`, `PL-PF8H`). The deletion half never is. A session
that discovers this at the end has already told the owner it was cleaning up,
and the correction arrives after the fact.

The local half is different and does work: `git branch -dr origin/<branch>`
drops a stale tracking ref without touching the remote, which is what clears the
stop hook's false "unpushed work" alarm.

**Where.** `docs/worker.md`, near whatever `PL-0XMD` lands about what a remote
session can and cannot reach - the same family of finding.

**Approach.** One line saying a session cannot delete a remote branch, that the
recovery is still its job, and that the deletion list goes to the owner as
pasteable commands. Do not turn this into a mechanism: there is nothing to build
and the permission is not the project's to change.

**Done when.** `docs/worker.md` says a session cannot delete a remote branch, so
a cleanup pass hands over a list instead of reporting a job finished.

**Done 2026-09-19 under `PL-4Q9B`** (record clone trust and the permitted ref
operations). `docs/worker.md` § "Ref operations a session cannot perform"
carries the line, and carries it for tag pushes too, so the two operations a
session cannot perform are stated in one place rather than one each.

Two things were taken from `PL-TFWR` (the same finding, now dropped) rather
than left with it: that a session must re-read `git ls-remote` before reporting
either operation done, because exit status 0 and `Everything up-to-date` are
what it gets when nothing happened; and that there is no second route, the
GitHub MCP server offering no deletion tool.

Per `PL-3V6C`, the block states no cause.

**The cause this brief asserts is not established.** "It is GitHub refusing the
ref deletion rather than the proxy - the session's token carries no
`delete_ref` permission" is an inference from an empty `recentRelayFailures`,
and that field does not carry it: a request declined on policy is not a relay
failure, so an empty list is equally consistent with the proxy declining the
deletion, and the container's own `/root/.ccr/README.md` lists 403 among the
proxy's own outcomes. `PL-TFWR` measured the same operation on the same day and
recorded the opposite - a ref dropped in transit, ending on `Everything
up-to-date` - and a push cannot both be silently swallowed and be refused with
a status code. At most one is what this project meets and nothing has
established which.

What this item measured, and what `docs/worker.md` now carries, is the
*symptom*: the deletion does not happen, and a cleanup pass therefore ends on
the owner's desk. That was always the part the item was for, and it is
unaffected.
