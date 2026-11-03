---
id: PL-82J5
title: no-prune-guard.sh judges a prune by its spelling and its own table lists 10 irreversible spellings it lets through; a git reference-transaction hook that aborts deletions under refs/remotes/ refused fetch --prune, -c fetch.prune=true, branch -dr, remote remove and update-ref --stdin in a scratch clone, whatever the spelling
priority: P2
effort: M
status: ready
classes: defect
feature: guards-keyed-on-the-action
touches: .claude/hooks/no-prune-guard.sh, .claude/hooks/stop_hook_patch.py, tests/unit/test_no_prune_guard.py
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
payoff: no spelling of a command can delete a remote-tracking ref that may be the only copy of an item
verify: grep -q 'def test_reference_transaction_refuses_remote_ref_deletions' tests/unit/test_no_prune_guard.py
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
