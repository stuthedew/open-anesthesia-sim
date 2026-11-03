---
id: PL-B5K1
title: The five shell guards hand the payload to Python through an environment variable, so any Bash command over about 128 KiB fails exec with E2BIG and passes every guard: a 140,000-character heredoc before git fetch --prune is let through
priority: P2
effort: S
status: ready
classes: defect
feature: guards-say-when-they-cannot-check
touches: .claude/hooks/no-prune-guard.sh, .claude/hooks/floor-interpreter-guard.sh, .claude/hooks/gate-status-guard.sh, .claude/hooks/push-check-guard.sh, .claude/hooks/docket-branch-guard.sh, .claude/hooks/direct-merge-guard.sh, .claude/hooks/hook_input.py, tests/unit/test_no_prune_guard.py, tests/unit/test_floor_interpreter_guard.py, tests/unit/test_gate_status_guard.py, tests/unit/test_push_check_guard.py, tests/unit/test_direct_merge_guard.py
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
payoff: a long heredoc no longer switches off every Bash guard for the command that follows it
verify: grep -q 'def test_a_call_longer_than_an_environment_variable_holds_is_still_judged' tests/unit/test_gate_status_guard.py && ! grep -qF 'PAYLOAD="$payload"' .claude/hooks/no-prune-guard.sh
---

**Problem.** The five shell guards hand the payload to Python through an environment variable, so any Bash command over about 128 KiB fails exec with E2BIG and passes every guard: a 140,000-character heredoc before git fetch --prune is let through

**Reproduced 2026-11-03.** A heredoc of 140,000 characters followed by `git
fetch --prune`, handed to `no-prune-guard.sh`, exited 0 with no output. The
same `git fetch --prune` alone is refused. The guard puts the payload in an
environment variable for `python3 -c`, and Linux refuses an `exec` whose single
argument or variable passes 128 KiB (`MAX_ARG_STRLEN`), so Python never starts.

**Why it matters.** A long command is ordinary when a session writes a file
through a heredoc, and the guard that protects irreversible ref deletions then
passes whatever follows it.

**Done when.** Every guard reads the payload from standard input or a file
rather than the environment, and a test hands each Bash guard a command over
128 KiB ending in a call it refuses, and finds the refusal.

**Generator check.** A member of `PL-9KSJ`: the guard let through a call it
never read, and said nothing.

**Progress, 2026-11-03 (#1990).** The floor-interpreter, gate-status,
push-check and direct-merge guards now read the payload on standard input,
through `hook_input.run`. Each has a test that hands it a call of 140,000
characters ending in one it refuses, and finds the refusal. Run against the
old scripts, the floor and gate guards let that call through with no output.
`docket-branch-guard.sh` already pipes the payload to Python on standard
input; its one environment variable carries the note it prints, which stays
short.

What is left is `no-prune-guard.sh`, which still sets `PAYLOAD="$payload"`.
`PL-1ZZ0` (#1991) moves its check into git hooks and deletes the script and
`tests/unit/test_no_prune_guard.py`, so this item closes once that merges. The
`verify:` line was rewritten to name the new gate-guard test, because the test
file it named goes with the script.
