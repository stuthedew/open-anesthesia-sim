---
id: PL-M2NV
title: no-prune-guard.sh has no shape for git push, so git push --prune origin 'refs/heads/*:refs/heads/*' and git push --mirror origin, which delete every branch on the remote the clone does not hold, other sessions' unmerged branches among them, run unrefused
status: untriaged
added: 2026-09-26
---

**Problem.** no-prune-guard.sh has no shape for git push, so git push --prune origin 'refs/heads/*:refs/heads/*' and git push --mirror origin, which delete every branch on the remote the clone does not hold, other sessions' unmerged branches among them, run unrefused

**Found 2026-09-26 while working `PL-R17X`.** On git 2.43.0, against a
scratch remote holding `main` and `other-session-branch`, from a clone holding
only `main`: `git push --prune origin 'refs/heads/*:refs/heads/*'` and `git
push --mirror origin` each deleted `other-session-branch` on the remote, and
`git push --prune origin main` and a bare `git push --prune origin`, an error,
deleted nothing. The guard as `PL-R17X` leaves it passes both.

The guard's own reason - a stale `origin/<branch>` can be the only surviving
copy of an item captured on a branch nobody merged - applies one step worse:
these delete the branch itself on the remote, for every session, rather than a
clone's copy of it. Whether a branch protection rule or the harness's push
proxy refuses such a push before it lands was not checked. Out of `PL-R17X`'s
scope, whose brief names the fetch, pull and remote spellings.
