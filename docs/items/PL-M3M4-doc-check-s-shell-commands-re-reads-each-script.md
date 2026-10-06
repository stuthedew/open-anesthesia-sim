---
id: PL-M3M4
title: doc_check's _shell_commands re-reads each script_lines piece on its own, so a case arm carried across lines reads its pattern as a command, and a pipe or redirection after a multi-line subshell's closing parenthesis is read as belonging to the last inner line alone; latent
status: untriaged
feature: one-answer
added: 2026-10-06
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

**Generator check.** A member of `PL-R417`: a reader takes a fragment of a
compound command for a whole command. `docket.shell`'s own whole-script pass
already reads case patterns; the context is lost in the re-read.

**Done when.** `_shell_commands` takes its commands from one pass of
`docket.shell` over the whole script, or keeps the compound's context across its
pieces, pinned by a `workflow commands, ` case in `PL-R417`'s guard for the case
arm and the piped subshell, failing on today's reader.
