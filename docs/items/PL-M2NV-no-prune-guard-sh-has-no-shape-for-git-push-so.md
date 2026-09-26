---
id: PL-M2NV
title: no-prune-guard.sh has no shape for git push, so git push --prune origin 'refs/heads/*:refs/heads/*' and git push --mirror origin, which delete every branch on the remote the clone does not hold, other sessions' unmerged branches among them, run unrefused
priority: P2
effort: S
status: ready
classes: defect
feature: bash-guard-bound
touches: .claude/hooks/no-prune-guard.sh, tests/unit/test_no_prune_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
payoff: a session's git push --mirror, or --prune with a wildcard refspec, is refused before it deletes other sessions' unmerged branches on the remote
verify: grep -q 'def test_a_push_that_prunes_the_remote_is_refused' tests/unit/test_no_prune_guard.py
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

**Why it matters.** The one member whose unguarded outcome cannot be undone:
the push deletes other sessions' unmerged branches on the remote, for every
session, where a prune deletes only this clone's copies. Found by probing, not
met. Whether the harness's push proxy or a branch protection rule refuses such
a push was not checked, and the check must not be the push itself.
Reproduced as filed on `origin/main` (`6efd8c41`) at triage, 2026-09-26,
beside `git fetch --prune`, which is refused.

**Done when.** A `git push` carrying `--mirror` or `--prune`, wherever git
reads its options, is refused with the guard's reason, pinned in
`tests/unit/test_no_prune_guard.py`.

**Generator check.** A member of `PL-61FT` (the Bash guards read what a
command does from its spelling): filed by `PL-R17X`'s close, whose fix read
the spellings git's fetch, pull and remote document and not push's. Owed under
any bound `PL-61FT` sets, since its outcome cannot be undone, so it is left
ready.
