---
id: PL-95BJ
title: A push that deletes a remote branch with git's hooks switched off passes .claude/hooks/push_check_guard.py: push_targets asks skips_hooks only of a push that sends commits, and --no-verify skips the pre-push hook that refuses the deletion
priority: P2
effort: S
status: ready
classes: defect
touches: .claude/hooks/push_check_guard.py, tests/unit/test_push_check_guard.py
deferred-from: v0.7.0 - a new problem, not present at the freeze (817a4d88): the guard's question about skipped hooks, and the pre-push refusal of a deletion it protects, arrived after it
added: 2026-11-10
payoff: no spelling of a push can delete a remote branch from a session, so the only copy of an unmerged item or commit cannot be lost that way
verify: grep -q 'def test_a_deleting_push_that_skips_git_hooks_is_refused' tests/unit/test_push_check_guard.py
reenters: PL-1ZZ0
---

**Problem.** A push that deletes a remote branch with git's hooks switched off passes .claude/hooks/push_check_guard.py: push_targets asks skips_hooks only of a push that sends commits, and --no-verify skips the pre-push hook that refuses the deletion

**Checked 2026-11-10, by reading the code and not by running the push:** in `.claude/hooks/push_check_guard.py`, `sends` returns False for a push that carries `--delete`, `-d`, `--dry-run` or a `:<branch>` refspec. `push_targets` asks `skips_hooks(words)` only inside `elif is_git(words) and sends(words):`. So `git push --no-verify origin --delete <branch>` reaches neither question, and the guard prints no refusal. `.claude/hooks/git/pre-push` is what refuses a session's push that deletes a remote branch (`PL-1ZZ0`), and `--no-verify` skips it.

**Why it matters.** A deleted remote branch can hold the only copy of an item or of unmerged work. Two guards stand in front of that, and one spelling passes both.

**Done when.** `push_targets` asks whether a push skips git's hooks of every push, including one that sends nothing. A test in `tests/unit/test_push_check_guard.py` gives the guard a deleting push with `--no-verify` and with `-c core.hooksPath=`, and each is refused.

**Generator check.** An instance of `PL-1ZZ0`'s fact (which action a request performs, whatever its spelling, client or text field), filed after that head closed on 2026-11-03. Its verdict says each irreversible action is checked where git performs it; this spelling switches that check off.
