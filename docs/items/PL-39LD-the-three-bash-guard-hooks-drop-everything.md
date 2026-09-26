---
id: PL-39LD
title: The three Bash guard hooks drop everything after the first '<<', not only the heredoc body, so a command after the heredoc's terminator line is never checked: a 'make docket 2>&1 | tail -4; echo "exit=$?"' run after a python3 heredoc printed tail's exit=0 unrefused
status: untriaged
feature: one-answer
touches: .claude/hooks/gate-status-guard.sh, .claude/hooks/floor-interpreter-guard.sh, .claude/hooks/no-prune-guard.sh, tests/unit/test_gate_status_guard.py, tests/unit/test_floor_interpreter_guard.py, tests/unit/test_no_prune_guard.py
added: 2026-09-26
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

**Done when.** A heredoc's body - from the line after its introducer to its
terminator line, `<<-` and a quoted delimiter included - is removed, and the
commands after the terminator are read like any others, in all three hooks;
the command above is refused, pinned in each hook's tests. An unterminated
heredoc still fails open.

**Generator check.** Another instance of `PL-PVW2`'s how-a-shell-command-splits
question, with `PL-R5RF` and `PL-63TT`: three hooks each spell the same cut, so
it belongs in the one splitter they import.
