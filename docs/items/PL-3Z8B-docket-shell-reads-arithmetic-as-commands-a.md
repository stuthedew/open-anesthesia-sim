---
id: PL-3Z8B
title: docket.shell reads arithmetic as commands: a $(( )) expansion's body is a clause of Reading.substitutions and a (( )) command's expression a subshell's, so p $(( 1 + 2 )) and (( 1 + 2 )) && p x hand every reader a command 1 + 2 where bash runs none; latent
priority: P3
effort: M
status: done
classes: defect
feature: shell-reads-as-bash
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py, .claude/hooks/shell_split.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage pass
added: 2026-10-12
closed: 2026-10-12
pr: 1449
payoff: an arithmetic expression is never handed to docket, doc_check or the Bash guards as a command, while a substitution inside one still is
verify: grep -q 'def test_arithmetic_is_one_word_that_runs_no_command' subprojects/docket/tests/test_shell.py && ! grep -qF 'id="PL-3Z8B' subprojects/docket/tests/test_shell.py
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

**Why it matters.** `docket.shell` is the one reader that docket's verify
audit, `tools/doc_check.py`'s workflow readers and the Bash guards share
(`PL-JNYL`), so an arithmetic expression read as a command misleads all of
them at once: `doc_check` would check `y + 1` as a command a workflow runs,
and every reader of a clause's head meets `(` where bash opens one arithmetic
command. While it stands, `PL-C4XY`'s comparison cannot draw arithmetic at
all.

**Widened at triage, 2026-10-12: the arithmetic `for`.** `for ((i = 0; i < 1;
i++)); do p $i; done` runs `p 0` under bash 5.2.21, and docket reads `i` and
`i++` as commands (measured 2026-10-12): the same arithmetic expression read
as a command list, in the form Bash Reference Manual §3.2.5.1 "Looping
Constructs" gives. It goes with this item because the reading that takes
`(( ))` whole takes `for ((` whole.

**Not a recurrence of `PL-GJKN`**, which `docket new` matched on the shared
`touches`: that item is where a here-document inside an expanded body ends,
and this is what an arithmetic body is. The match is withdrawn because of this
paragraph.

**Generator check.** Found by `PL-C4XY`'s comparison, which is what stops a
departure of this kind reaching `main` from now on; read against `bin/docket
generators --misread` on 2026-10-12, it misreads no recorded fact.

**Route, measured 2026-10-12.** One matched-pair reader, modelled on
`_Lexer.parameter`, reads an arithmetic body as bash 5.2's
`parse_matched_pair` does: it counts parentheses, steps over quotes,
backslash escapes and `$'...'`, reads each `$` expansion and backquote it
meets through `_Lexer.substitution`, so `$(( $(p x) + 1 ))` still runs `p x`,
takes `#`, a newline and `<<` as plain characters, and is unreadable where
nothing closes it. Then:

- A `$((` that `_arithmetic` finds arithmetic stays part of its word, as
  written, with no body clause and no list of `FlatReading.substituted` of its
  own; only a `$(` that is not arithmetic is read inline for the hooks.
- A `((` at a command's head, and after `for` there, is one word, as written,
  not `quoted`, so it stays apart from `'((1))'`, refused as a command name,
  and a plain string in the flat view. `_Grammar.arithmetic` and the
  `arithmetic` parameters go, since a newline inside is inside the word. The
  head after the closing `))` stays as `PL-9NMR` describes it.
- Refuted: `((` and `))` as operator tokens, which leave the expression a
  command, and `quoted=True`, which reads the word as `'((1))'`.

Bash 5.2.21 measured: `(( $(p y) ))` runs `p y` and exits 1, so the generator
keeps a drawn arithmetic command's status zero; a backquoted substitution
expanding to nothing inside `$(( 1 + ... ))` leaves `+` with no operand, a
syntax error, so the generator draws substitutions in arithmetic only where
the expression stays valid; `$(( 16#ff ))` is 255. The generator draws
`$(( ))`, `(( ))` and `for (( ))`, and `_handed` reads a `((`-led command as it
reads `for` and `[[`. `PL-X1VN` reuses the matched-pair reader, so this lands
first.

**Done when.** An arithmetic expansion's body is no clause of `every_clause()`
and holds no list of `FlatReading.substituted`, an arithmetic command's `((`
and `))` open and close no subshell, an arithmetic `for`'s expressions are no
commands, a command substitution inside any of them still is one, and the
comparison draws all three, its known departure rows for them gone.
