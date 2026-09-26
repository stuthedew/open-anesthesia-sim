---
id: PL-39LD
title: The three Bash guard hooks drop everything after the first '<<', not only the heredoc body, so a command after the heredoc's terminator line is never checked: a 'make docket 2>&1 | tail -4; echo "exit=$?"' run after a python3 heredoc printed tail's exit=0 unrefused
priority: P2
effort: S
status: done
classes: defect
feature: one-answer
touches: .claude/hooks/shell_split.py, .claude/hooks/gate-status-guard.sh, .claude/hooks/floor-interpreter-guard.sh, .claude/hooks/no-prune-guard.sh, tests/unit/test_gate_status_guard.py, tests/unit/test_floor_interpreter_guard.py, tests/unit/test_no_prune_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; a member of PL-PVW2, worked with its step 2
added: 2026-09-26
closed: 2026-09-26
payoff: a check run after a heredoc in the same call is read by all three guards, so a lost status, a floor parse or a prune there is refused
verify: grep -q 'def test_only_a_heredoc_body_is_removed' tests/unit/test_gate_status_guard.py && grep -q 'def test_only_a_heredoc_body_is_removed' tests/unit/test_floor_interpreter_guard.py && grep -q 'def test_only_a_heredoc_body_is_removed' tests/unit/test_no_prune_guard.py
---

**Problem.** The three Bash guard hooks drop everything after the first '\<\<', not only the heredoc body, so a command after the heredoc's terminator line is never checked: a 'make docket 2>&1 | tail -4; echo "exit=$?"' run after a python3 heredoc printed tail's exit=0 unrefused

**Found 2026-09-26 while working `PL-1SFZ`, by being caught by it.** The
session ran one Bash call that wrote an item's body through a `python3 -
<<'EOF'` heredoc and then, after the `EOF` line, ran `make docket 2>&1 | tail
-4; echo "exit=$?"` with no `pipefail`. `gate-status-guard.sh` let it through,
and the `exit=0` it printed was `tail`'s. The store happened to be valid - a
rerun with `pipefail` exited 0 - so nothing false was reported, but only
because the session noticed.

Each hook does `command.split("<<", 1)[0]`: `gate-status-guard.sh`,
`floor-interpreter-guard.sh` and `no-prune-guard.sh`. The comment in the first
calls what follows "document content", which holds only up to the line that
terminates the heredoc; the lines after it are commands again. This repository
writes a file through a heredoc and then checks it in the same call routinely,
which is exactly the shape this drops.

**Why it matters.** Everything after the first `<<` is unguarded, and the
command after a heredoc is where this repository puts the check on what the
heredoc wrote: a gate whose status is thrown away there reaches the session as
exit 0, `PL-2JRC`'s failure, and a floor parse or a prune there is never
refused. The cut is not quote-aware either, so a `<<` inside a quoted argument
hides the rest of the command the same way.

**Done when.** A heredoc's body - from the line after its introducer to its
terminator line, `<<-` and a quoted delimiter included - is removed, and the
commands after the terminator are read like any others, in all three hooks;
the command above is refused, pinned in each hook's tests. An unterminated
heredoc still fails open.

**Generator check.** Another instance of `PL-PVW2`'s how-a-shell-command-splits
question, with `PL-R5RF` and `PL-63TT`: three hooks each spell the same cut, so
it belongs in the one splitter they import.
