---
id: PL-3Z8B
title: docket.shell reads arithmetic as commands: a $(( )) expansion's body is a clause of Reading.substitutions and a (( )) command's expression a subshell's, so p $(( 1 + 2 )) and (( 1 + 2 )) && p x hand every reader a command 1 + 2 where bash runs none; latent
status: untriaged
feature: shell-reads-as-bash
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py, docs/items/PL-GJKN-docket-shell-s-lexer-applies-the-command.md
added: 2026-10-12
recurrences: 2026-10-12 PL-X1VN withdrawn 2026-10-12 PL-X1VN, 2026-10-12 PL-48ZJ withdrawn 2026-10-12 PL-48ZJ
---

**Problem.** docket.shell reads arithmetic as commands: a $(( )) expansion's body is a clause of Reading.substitutions and a (( )) command's expression a subshell's, so p $(( 1 + 2 )) and (( 1 + 2 )) && p x hand every reader a command 1 + 2 where bash runs none; latent

**Found 2026-10-12** while building `PL-C4XY`'s bash comparison in
`subprojects/docket/tests/test_shell.py`: generated with an arithmetic
expansion, the scripts gave docket a command bash never ran, so the generator
leaves the form out and the comparison pins today's reading as a known
departure naming this item.

**Reproduced 2026-10-12** on `main` at `98673556`:

```text
p $(( 1 + 2 ))       bash runs: p 3      every_clause(): [p, $(( 1 + 2 ))]  [(, 1, +, 2, )]
x=$((y + 1)); p x    bash runs: p x      every_clause(): [x=$((y + 1)), ;, p, x]  [(, y, +, 1, )]
(( 1 + 2 )) && p x   bash runs: p x      every_clause(): [(, (, 1, +, 2, ), )]  [p, x]
```

`_Lexer.substitution` reads a `$((` bash reads as arithmetic as `(( ))` is
read, which is right for where it ends, and then hands its body to
`substitution_body`, which records it in `bodies` beside the command
substitutions. An arithmetic expansion runs no command (Bash Reference Manual
§3.5.5 "Arithmetic Expansion"), though a substitution inside one does, so
`$(( $(p x) + 1 ))` runs `p x`.

The arithmetic command is the same mistake in a different place, found by the
same comparison after this item was filed: `(( 1 + 2 ))` runs no command
either (§3.2.5.2 "Conditional Constructs"), and `_Grammar` knows one is open,
which is how a newline inside it is a space, but its `((` and `))` are read as
two subshell parentheses each, with the expression between them a command.

**Reach.** Every reader of `Reading.substitutions` or `every_clause()`, and the
hooks' `FlatReading.substituted`: `doc_check`'s `_simple_commands` would list
`y + 1` as a command a workflow runs, and every reader of a clause's head
meets `(` where a `((` opens. Latent: on 2026-10-12 no workflow step, tracked
`.sh` file or fenced shell sample holds a `$((` or an arithmetic command, and
`verify:` fields refuse one at its unquoted `$` or `(`.

**Not a recurrence of `PL-GJKN`**, which `docket new` matched on the shared
`touches`: that item is where a here-document inside an expanded body ends,
and this is what an arithmetic body is. The match is withdrawn because of this
paragraph.

**Generator check.** Found by `PL-C4XY`'s comparison, which is what stops a
departure of this kind reaching `main` from now on; read against `bin/docket
generators --misread` on 2026-10-12, it misreads no recorded fact.

**Done when.** An arithmetic expansion's body is no clause of `every_clause()`
and holds no list of `FlatReading.substituted`, an arithmetic command's `((`
and `))` open and close no subshell, a command substitution inside either
still is one, and the comparison's known departure rows for them are gone.
