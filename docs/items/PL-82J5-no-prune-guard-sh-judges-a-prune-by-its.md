---
id: PL-82J5
title: no-prune-guard.sh judges a prune by its spelling and its own table lists 10 irreversible spellings it lets through; a git reference-transaction hook that aborts deletions under refs/remotes/ refused fetch --prune, -c fetch.prune=true, branch -dr, remote remove and update-ref --stdin in a scratch clone, whatever the spelling
priority: P2
effort: M
status: done
classes: defect
feature: guards-keyed-on-the-action
touches: .claude/hooks/git/reference-transaction, .claude/hooks/git/pre-push, .claude/hooks/stop_hook_patch.py, .claude/hooks/hook_input.py, tests/unit/test_git_hooks.py
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
closed: 2026-11-03
pr: 1991
payoff: no spelling of a command can delete a remote-tracking ref that may be the only copy of an item
verify: grep -q 'def test_a_command_that_deletes_a_remote_tracking_ref_is_refused_with_every_ref_kept' tests/unit/test_git_hooks.py
reenters: PL-61FT
---

**Problem.** no-prune-guard.sh judges a prune by its spelling and its own table lists 10 irreversible spellings it lets through; a git reference-transaction hook that aborts deletions under refs/remotes/ refused fetch --prune, -c fetch.prune=true, branch -dr, remote remove and update-ref --stdin in a scratch clone, whatever the spelling

**Why it matters.** A deleted remote-tracking ref can be the only copy of an
item captured on a branch nobody merged, and it cannot be brought back.
`no-prune-guard.sh` reads the command's words, so every spelling its model of
bash and git does not cover deletes refs unchecked, and its own `KNOWN_GAPS`
table lists ten such spellings. The review found that a git
`reference-transaction` hook, which git calls with the refs a command is about
to change, refused every one of them in a scratch clone whatever the spelling.

<!-- absent: no-prune-guard.sh -->

**Done when.** A deletion under `refs/remotes/` is refused by what git is about
to do rather than by how the command was spelled, the hook is installed in
every clone a session works in, and a test runs at least `fetch --prune`, `-c
fetch.prune=true fetch`, `branch -dr`, `remote remove` and `update-ref
--stdin` in a scratch clone and finds each refused.

**Generator check.** A re-entry of `PL-61FT`, whose fact is what a shell
command does when run. Its fix recorded unread spellings as known gaps, and
this item shows the gaps include irreversible deletions. With `PL-9PPJ` and
`PL-SMM1` it is the third instance filed after `PL-61FT` closed, so the head's
fix did not hold. `PL-3986` and `PL-D16Y` misread the neighbouring fact of
which client can perform a guarded action.

**Decided, 2026-11-03: every deletion under `refs/remotes/` is refused, not
only a prune.** `.claude/hooks/git/reference-transaction` refuses a session's
command that would delete any remote-tracking ref. Refusing only a ref that is
the last copy of its commits was weighed and set aside. It needs a reachability
walk inside the hook, and the restart recipe that used `git branch -dr` does
not need the deletion: a push to the branch moves the stale ref, which a test
shows. A `pre-push` hook refuses a push that deletes a branch on the remote.
Git 2.43.0 leaves a `--mirror` push's deletions out of what it tells that
hook, so a mirror push is refused by the remote-tracking refs it would send.
The session-start hook installs both hooks, and each acts only where Claude
Code's `CLAUDECODE` variable is set. `no-prune-guard.sh` and its test are
deleted, because a second reader of what git deletes beside git's own report
is the copy this head removes. The `verify:` names the test in
`tests/unit/test_git_hooks.py`, the file that replaced the commissioned one.
