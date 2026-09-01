---
id: PL-Z8SV
title: Pushing no longer waits for the owner - only the pull request does
priority: P2
effort: S
status: done
classes: docs, infra
feature: planning-cadence
milestone: v0.2.8
touches: CLAUDE.md
added: 2026-08-30
closed: 2026-08-30
commit: 8a97540
pr: 89
verify: grep -q 'open a pull request only when asked' CLAUDE.md
---

**Problem.** `CLAUDE.md` said "Commit as you go; ask before the first push",
which cost a round trip on every session that produced anything. The reason
given was that "a branch pushed during a discussion that never lands is clutter
a concurrent session has to reason about" - but the clutter that rule prevents
is a stale *branch*, and a web session's branch is created by the harness before
the session starts. Pushing to it adds no branch that was not already there.

**Why it matters.** The rule charged a full turn - the whole context resent -
for a permission that protects nothing, on the most common action a working
session takes. It also left work in an ephemeral container while waiting for
the answer, which is the failure the same bullet warns about two sentences
earlier.

**Where.** `CLAUDE.md`, the queue rules.

**Worked.** Replaced in the session the owner asked for it (2026-08-30).
Committing and pushing are now both continuous; what still waits for the owner
is the pull request, which is the act that asks for attention and proposes a
merge. The capture exception the old bullet carried is no longer needed - it
existed only to let captures escape the hold.

**Done when.** Met: `CLAUDE.md` says to push freely and to open a pull request
only when asked, and no other file states the superseded rule (checked:
`docs/worker.md` and the `docket` skill mention neither).
