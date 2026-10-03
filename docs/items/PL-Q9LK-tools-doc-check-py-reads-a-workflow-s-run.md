---
id: PL-Q9LK
title: tools/doc_check.py reads a workflow's run: script one line at a time through docket's one-line reader, so a heredoc body's lines are read as commands, and a command continued by a backslash or a quote across lines is declined rather than read
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py, subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-10-03
pr: 1304
payoff: a workflow step whose command is continued across lines or feeds a heredoc keeps its path check, and a heredoc body naming a path is not read as a command that runs it
verify: grep -q 'def test_workflow_commands_reads_a_script_as_bash_does' tests/unit/test_doc_check.py
recurrences: 2026-10-03 PL-Z8RS, 2026-10-03 PL-G2FY, 2026-10-03 PL-6P6H
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

[superseded 2026-09-26: re-read at triage, below] **Generator check.** Not `PL-PVW2`'s, in this session's reading: there is one
reading now, not two that disagree, and the gap is the input it covers. The
hooks' `.claude/hooks/shell_split.py` already reads a multi-line command, which
is where triage would look first.

**Reproduced 2026-09-26** on `origin/main` (`6efd8c41`): for a `run: |` step
holding `python3 - <<'PY'`, one body line and `PY`, then `python3
tools/doc_check.py \` continued onto `check`, `workflow_commands` yields five
commands - the heredoc's body line and its delimiter as commands of their own,
and the continued command as two.

**Why it matters.** Latent today, since no workflow line runs past its end.
The first continued command loses its path check to a decline, and the first
heredoc body naming a path is read as a command that runs it: a check passing
while its guarantee is void, with nothing to say so.

**Done when.** `workflow_commands` removes a heredoc's body and delimiter and
joins a backslash-continued command into one, as bash reads them, pinned in
`tests/unit/test_doc_check.py`.

**Generator check, at triage 2026-09-26.** An instance of `PL-PVW2`'s fact
filed after the head closed, in the commit that closed it (`02413b5b`): two
spellings of how a shell command splits disagree on a multi-line script. The
hooks' `.claude/hooks/shell_split.py` removes heredoc bodies and joins
continuations, and docket's `shell.py`, which `doc_check` reads through, takes
one line; the filing session saw one reading where there are two. Not
`PL-61FT`'s, since `doc_check` decides no command's effect.

**Worked 2026-10-03.** Re-confirmed on `1d9e406a` before any code: still
true as written, `drift.yml`'s body lines 158-175 were each yielded as a
command. The fix keeps one reading rather than adding a third. Docket's
`shell.py` lexer now reads a newline as bash does - a backslash-newline is
removed outside single quotes, an unquoted newline ends a command, a comment
ends at its line, and the body of each `<<` or `<<-` is skipped to its
delimiter (`<<-` joined the operator table, which the hooks' already had) -
and `shell.script_lines` cuts a script where bash ends a line, each piece
spelled as written. `workflow_commands` hands it the step's script as YAML
hands it to bash, less the block's own indentation, so `x\` over an indented
`y` stays two words. Pieces keep their spelling because cutting a body out
inside a `$( )` would leave its `<<` to swallow the next line on re-reading.
One departure from bash, pinned: a body its delimiter never ends is
unreadable rather than read to the end, since the likelier cause is a `<<`
misread inside `(( ))`. Every pinned shape was run through bash 5.2.21.
Found and filed, feature `one-answer`: `PL-G2FY` (Makefile recipes are still
read a line at a time), `PL-6P6H` (a folded `run: >` block is read as a
literal one) and `PL-P72R` (nothing checks that docket's and the hooks'
operator tables agree).
