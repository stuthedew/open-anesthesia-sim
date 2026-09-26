---
id: PL-M2NV
title: no-prune-guard.sh has no shape for git push, so git push --prune origin 'refs/heads/*:refs/heads/*' and git push --mirror origin, which delete every branch on the remote the clone does not hold, other sessions' unmerged branches among them, run unrefused
priority: P2
effort: S
status: done
classes: defect
feature: bash-guard-bound
touches: .claude/hooks/no-prune-guard.sh, tests/unit/test_no_prune_guard.py, docs/items/PL-YFT4-no-prune-guard-sh-refuses-reads-that-prune.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-09-26
pr: 1129
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

**Closed 2026-09-26: what "wherever git reads its options" was read as.**
Every spelling pinned was first run against a scratch bare remote on git
2.43.0, from a clone holding only `main`. Three places: anywhere among the
push's words, since git reads an option after the repository and the refspecs
as well as before them; through the wrappers, redirections and command
positions the guard already reads for a fetch; and the `remote.<name>.mirror`
setting, which git reads as `--mirror` ("the default if the configuration
option `remote.<remote>.mirror` is set", git v2.43.0
`Documentation/git-push.txt`), passed ahead of the command name or written by
`git config`. `git -c remote.origin.mirror=true push origin` deleted the branch
there, so the setting is the same push by another route rather than a spelling
beside it.

Two refusals are deliberate and pinned: `--prune` is refused with any refspec,
though `git push --prune origin main` deleted nothing, because a push naming no
refspec takes one from a config file the hook never reads; and a `--dry-run`
beside either flag is not read. The hook's out-of-reach list gains `git push
--mir`, which mirrors, and the mirror setting that `git remote add --mirror`
and `git clone --mirror` write, which only a push to that new remote or from
that new clone reads. Whether GitHub branch protection or the harness push
proxy would refuse such a push was not checked: the guard does not rely on
either, and the check would be the push itself.

The mirror setting's `config` shape refuses `git config --get
remote.origin.mirror`, a read, for the cause `PL-YFT4` fixes on the prune
setting, so that brief now says the fix is owed on both.
