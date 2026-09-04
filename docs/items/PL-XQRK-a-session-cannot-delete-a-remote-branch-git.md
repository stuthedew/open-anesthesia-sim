---
id: PL-XQRK
title: A session cannot delete a remote branch, so every cleanup pass ends on the owner's desk without saying so up front
priority: P3
effort: S
status: ready
classes: docs, infra
feature: worker-instructions
touches: docs/worker.md
verify: python3 tools/doc_check.py check && grep -q 'cannot delete a remote branch' docs/worker.md
added: 2026-09-04
---

**Problem.** `git push origin --delete <branch>` fails with `HTTP 403` from a
remote session. Measured 2026-09-04 against five branches; the agent proxy
reported `recentRelayFailures: []`, so it is GitHub refusing the ref deletion
rather than the proxy - the session's token carries no `delete_ref` permission.
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
