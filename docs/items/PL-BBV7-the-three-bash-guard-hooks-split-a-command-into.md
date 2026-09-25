---
id: PL-BBV7
title: The three Bash guard hooks split a command into programs three ways, so the floor-interpreter guard lets 'cd /x&&python3 src/a.py', 'true;python3 -m compileall src/' and '(python3 src/a.py)' through while denying the same commands with spaces
status: untriaged
feature: one-answer
touches: .claude/hooks/floor-interpreter-guard.sh, .claude/hooks/gate-status-guard.sh, .claude/hooks/no-prune-guard.sh
added: 2026-09-25
---

**Problem.** The three Bash guard hooks split a command into programs three ways, so the floor-interpreter guard lets 'cd /x&&python3 src/a.py', 'true;python3 -m compileall src/' and '(python3 src/a.py)' through while denying the same commands with spaces

Reproduced against `floor-interpreter-guard.sh` (plain `shlex.split`), `gate-status-guard.sh` (`punctuation_chars`) and `no-prune-guard.sh` (regex). PL-GVFC covers the false-refusal direction; this is the missed-refusal direction and `(` grouping.

**Why it matters.** A guard that a missing space defeats.

**Done when.** One splitter shared by the three hooks; a test holds each reproduction.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn` (PL-P0FP).
