---
id: PL-2JYP
title: docket's shell lexer compares an unquoted here-document's body with its delimiter one physical line at a time, cuts a ${...} at a newline, and closes a multi-line $( ) at a case pattern's ), so script_lines hands doc_check fragments as commands; latent
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-R417's shell slice, 2026-10-05
added: 2026-10-04
payoff: a workflow step or a shell fence whose here-document, parameter expansion, case substitution or bash compound continues across lines is cut where bash ends its lines, so doc_check judges the commands the script runs and no fragment of one
verify: grep -q 'shell lines, a case pattern does not close its substitution' tests/unit/test_doc_check.py
---

**Problem.** docket's shell lexer compares an unquoted here-document's body with its delimiter one physical line at a time, cuts a ${...} at a newline, and closes a multi-line $( ) at a case pattern's ), so script_lines hands doc_check fragments as commands; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

POSIX XCU § 2.7.4 with § 2.2.3, § 2.3 rule 5 with § 2.6.2, and § 2.6.3 with § 2.9.4.3; bash 5.2.21 and dash agree on each.

- `script_lines` over "cat <<EOF", "a\" , "EOF", "echo inside-body", "EOF", "echo after" yields `echo inside-body` and `EOF` as commands, where both shells read the body to the second `EOF`; through `_make_mentions` a `make` line there names a phantom target.
- "echo ${y:-three" over "four}" yields `four}` as a command; both shells run `echo three four`.
- "x=$(case a in", "  a) echo A;;", "esac)" is cut at the case pattern's `)`, so `esac)` reads as a command.
- bash's `(( ))` and `[[ ]]` carried across lines are cut too; POSIX defines neither, so they count only if bash's grammar is in scope.

`PL-Q9LK`'s forms all still read whole. Latent: no tracked shell host or `sh` fence holds an unquoted here-document with a continued body line, a `${` left open at a line end, or a `$(case`.

**Why it matters.** `docket.shell` is the one reading every docket rule and
`tools/doc_check.py` take of a shell command, and `script_lines` is what
`doc_check` cuts a workflow step's script and a documented shell fence with
(`PL-Q9LK`, `PL-R417`): each piece it hands back is read as a command whose
paths, `make` targets and gate parity the checks then judge. A fragment read
as a command is a phantom the checks judge, and a command swallowed into a body
is one they never see, so a check can report a script sound that it never
read. Latent: no tracked workflow, recipe or fence holds any of the forms.

**Reproduced 2026-10-05, at triage.** On `main` at `c479363e`, under python3
3.11.15, `script_lines` cut each script below where bash 5.2.21 reads on:

- `cat <<EOF`, `a\`, `EOF`, `echo inside-body`, `EOF`, `echo after` into
  `cat <<EOF`, `echo inside-body`, `EOF` and `echo after`, where bash and dash
  0.5.12 both read the body to the second `EOF`;
- `echo ${y:-three` over `four}` into two, `four}` the second, where both shells
  print `three four`;
- `x=$(case a in`, `  a) echo A;;`, `esac)` with the substitution closed at
  `a)`, so `esac)` is a piece of its own, where both shells set `x` to `A`;
- `(( x = 1 +` over ` 2 ))` into two, where bash sets `x` to 3;
- and `[[` over ` a == a ]]` into two, where bash reads one conditional.

**Found at triage: `PL-97CF`'s operator split, in this lexer too.** It reads an
operator from the raw text, as the hooks' splitter does, so `a &\` over `& b`
is `&`, `&`, and `cat <<\` over `-EOF` reads `<<` with the delimiter `-EOF`:
the tab-indented `EOF` then never ends the body, and the rest of the script is
one unreadable piece. Both shells read `&&` and `<<-EOF`. The same fact in the
same reader, so it is this item's.

**`(( ))` and `[[ ]]` are in scope.** The capture left them to whether bash's
grammar is. It is: the module reads bash's rules by its own docstring, and a
workflow's `run:` step runs under bash.

**Done when.** `script_lines` and `shell_words` read, as bash 5.2 does: an
operator a backslash-newline splits as the one operator; an unquoted
here-document's body in logical lines, as `PL-97CF` reads one; a `${...}` to its
closing `}` across lines; a `$( )` holding a `case` to its own `)`, past each
pattern's; and an arithmetic `(( ))` or a conditional `[[ ]]` carried across
lines as one command, a newline inside it whitespace and a `<<` inside
`(( ))` a shift. `PL-R417`'s guard gains a `shell lines, ` case per form, each
failing on today's reader.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
