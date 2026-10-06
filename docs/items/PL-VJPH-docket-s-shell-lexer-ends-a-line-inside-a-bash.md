---
id: PL-VJPH
title: docket's shell lexer ends a line inside a bash process substitution or a compound array assignment carried across lines, so script_lines hands doc_check the substitution's tail and each array element as commands where bash 5.2 runs one command; latent
status: untriaged
feature: one-answer
added: 2026-10-06
---

**Problem.** docket's shell lexer ends a line inside a bash process substitution or a compound array assignment carried across lines, so script_lines hands doc_check the substitution's tail and each array element as commands where bash 5.2 runs one command; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`docket.shell`, the shared shell reader. `_Lexer.read` records a line break at a
newline unless a substitution has raised its nesting, which only `$(` and a
backquote do. A process substitution, `<(` or `>(` (Bash Reference Manual
§ 3.5.6), and a compound array assignment, `name=(` (§ 6.7), are read as plain
operators with no nesting, though each holds newlines and its command goes on
after the closing parenthesis. The module names bash as its reference; dash
refuses both forms.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against bash 5.2.21:

```text
echo <(echo a
) tools/doc_check.py

files=(
  tools/doc_check.py
  tools/dead_ends.py
)
echo "${files[@]}"
```

`script_lines` cut the first script into `echo <(echo a` and `)
tools/doc_check.py`, and `doc_check._shell_commands` read the second piece as a
command running `tools/doc_check.py`; it cut the second into `files=(`, each
element and `)`, so each array element read as a command. `bash -x` shows one
command each, `echo /dev/fd/63 tools/doc_check.py` and `files=(tools/doc_check.py
tools/dead_ends.py)`. Latent: no tracked file leaves `<(`, `>(` or `name=(` open
at a line end.

**Generator check.** A member of `PL-R417`: the one shell reader ends a
statement at a newline bash carries it past. The hooks' `shell_split` is the
other copy (`PL-JNYL`), whose gaps its own policy records rather than files.

**Done when.** `_Lexer` counts `<(`, `>(` and an assignment's `(` as nesting, as
it counts `$(`, pinned by a `shell lines, ` case in `PL-R417`'s guard for each
form, failing on today's reader.

**Decided 2026-10-06.** Fixed once, in the shell reader `PL-JNYL` merges from
the hooks' and docket's two, which opens `PL-R417`'s shell batch (project
owner, 2026-10-06, ratified, over fixing each shell reader in place).
