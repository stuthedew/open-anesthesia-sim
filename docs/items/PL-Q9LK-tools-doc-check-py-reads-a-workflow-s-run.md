---
id: PL-Q9LK
title: tools/doc_check.py reads a workflow's run: script one line at a time through docket's one-line reader, so a heredoc body's lines are read as commands, and a command continued by a backslash or a quote across lines is declined rather than read
status: untriaged
feature: one-answer
added: 2026-09-26
---

**Problem.** tools/doc_check.py reads a workflow's run: script one line at a time through docket's one-line reader, so a heredoc body's lines are read as commands, and a command continued by a backslash or a quote across lines is declined rather than read

**Found 2026-09-26 building `PL-CWBJ`.** `check_workflow_paths` and
`check_gate_parity` read each line `workflow_commands` yields through
`docket.shell.shell_words`, which reads one line. On `39a7a31f` no workflow or
recipe line runs past its end, so nothing is declined; `drift.yml`'s
`python3 - <<'PY'` body is read as lines of commands, as the old pattern read
it, and yields no path. The risk is a later step: a `\`-continued command loses
its path check to a decline, and a heredoc body naming a path is read as a
command that runs it.

**Generator check.** Not `PL-PVW2`'s, in this session's reading: there is one
reading now, not two that disagree, and the gap is the input it covers. The
hooks' `.claude/hooks/shell_split.py` already reads a multi-line command, which
is where triage would look first.
