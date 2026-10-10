---
id: PL-M3M4
title: doc_check's _shell_commands re-reads each script_lines piece on its own, so a case arm carried across lines reads its pattern as a command, and a pipe or redirection after a multi-line subshell's closing parenthesis is read as belonging to the last inner line alone; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/shell.py, tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
payoff: a case construct in a CI step reads as the commands its arms run, so a pattern or the case line is never taken for a script the merge gate runs
verify: grep -qF '"workflow commands, a case construct runs only the commands in its arms"' tests/unit/test_doc_check.py
---

**Problem.** doc_check's _shell_commands re-reads each script_lines piece on its own, so a case arm carried across lines reads its pattern as a command, and a pipe or redirection after a multi-line subshell's closing parenthesis is read as belonging to the last inner line alone; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), from
`docket.shell.script_lines` into `tools/doc_check.py`. `script_lines` cuts a
script where a compound command's inner newlines separate its commands, which is
right (POSIX § 2.9.4). `_shell_commands`, reached through `workflow_commands`,
then lexes each piece with no context from the lines around it, but a case
pattern's `)`, and a pipe or redirection after a compound command's closing
word, belong to the compound (§ 2.9.2).

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against bash 5.2.21:

```text
case "$1" in
  check) make check ;;
  *) exit 1 ;;
esac

( make check
  echo done ) | tee log
```

The arm's line read as two commands, `check` and `make check`, and the next as
`*` and `exit 1`; the subshell's last line attributed the pipe to `echo done`
alone, and its first line read as unpiped. bash reads `check` as the arm's
pattern and `make check` as the one command it runs, and pipes the whole
subshell, `make check` included, to `tee`. Latent: no tracked workflow,
Makefile, shell script or Markdown file holds a top-level `case` or a compound
command whose closing line carries a pipe or a redirection.

**Reproduced 2026-10-10 at triage** on this branch at `b6b9c382`, whose readers are `main`'s at `fe2e5132`: `_shell_commands` over the
pieces `workflow_commands` cut from the `case` read six commands - `case $1 in`,
`check`, `make check`, `*`, `exit 1` and `esac` - where bash runs `make check`
or `exit 1`. The piped subshell read as `make check`, `echo done` and `tee
log`, which is what one pass over the whole script reads too:
`_shell_commands` hands back each simple command's words and nothing of the
pipe between them, so the attribution the brief describes reaches no reader of
it. A guard case for it would pass on today's reader, so the case arm alone is
pinned.

**Why it matters.** `check_gate_parity` reads the scripts each CI step runs
through `_shell_commands`, so a `case`'s subject, its patterns and its `esac`
read as commands are scripts the merge gate is taken to run, and a pattern
spelling a gate's script would count as CI running it.

**Generator check.** A member of `PL-R417`: a reader takes a fragment of a
compound command for a whole command. `docket.shell`'s own whole-script pass
already reads case patterns; the context is lost in the re-read.

**Done when.** `_shell_commands` takes its commands from one pass of
`docket.shell` over the whole script, or keeps the compound's context across its
pieces, pinned by a `workflow commands, ` case in `PL-R417`'s guard for the case
arm, failing on today's reader; the piped subshell's commands are the same
either way, as measured at triage.
