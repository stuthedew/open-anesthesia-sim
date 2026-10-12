---
id: PL-X1VN
title: docket.shell cuts a clause at the && inside [[ ]] and reads its (, ), ||, < and > as operators, so [[ -n a && -n b ]] && p x is the clauses [[ -n a, -n b ]] and p x to every reader, where bash runs one conditional and p x; latent
priority: P3
effort: M
status: ready
classes: defect
feature: shell-reads-as-bash
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py, .claude/hooks/shell_split.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage pass
added: 2026-10-12
payoff: a conditional reads as the one command bash runs, so no reader is handed a clause headed by a test operator or a redirection that is a string comparison
verify: grep -q 'def test_a_conditional_s_operators_are_its_own_words' subprojects/docket/tests/test_shell.py && ! grep -qF 'id="PL-X1VN' subprojects/docket/tests/test_shell.py
---

**Problem.** docket.shell cuts a clause at the && inside [[ ]] and reads its (, ), ||, \< and > as operators, so [[ -n a && -n b ]] && p x is the clauses [[ -n a, -n b ]] and p x to every reader, where bash runs one conditional and p x; latent

**Found 2026-10-12** while building `PL-C4XY`'s bash comparison in
`subprojects/docket/tests/test_shell.py`: a `[[ ]]` holding `&&` or a
parenthesis gave docket commands bash never ran, so the generator draws a
conditional with neither and the comparison pins today's reading as a known
departure naming this item.

**Reproduced 2026-10-12** against `shell.py` as `main` holds it at `eb520ef4`:

```text
[[ -n a && -n b ]] && p x     bash runs: p x    every_clause(): [[, -n, a  |  -n, b, ]]  |  p, x
[[ ( -n a ) || a < b ]]       bash runs: none   every_clause(): [[, (, -n, a, ), ||, a, <, b, ]]
```

Inside `[[ ]]` bash reads `(`, `)`, `!`, `&&` and `||` as the conditional's
own operators and `<` and `>` as comparisons rather than redirections (Bash
Reference Manual §3.2.5.2 "Conditional Constructs"). `_Grammar` knows a `[[`
is open, which is how a newline inside one ends no line, but the lexer reads
its operators as it reads them anywhere: `&&` cuts the clause and the rest are
operator tokens.

**Reach.** Every reader of `every_clause()` meets a clause headed `-n`, and
`doc_check`'s `_simple_commands` would list `-n b ]]` as a command a workflow
runs; a reader of redirections takes `a < b` for a read from a file `b`.
Latent: on 2026-10-12 no line of a workflow step, tracked `.sh` file or fenced
sample holds one of those operators inside a `[[ ]]`, and `verify:` fields
refuse a `[[` at its unquoted `[`.

**Why it matters.** Every reader of a clause list - docket's verify audit,
`doc_check`'s `_simple_commands` and the Bash guards' `commands` - meets a
clause headed `-n` that bash never runs, and a reader of redirections takes a
string comparison's `<` for a read from a file. While it stands, `PL-C4XY`'s
comparison can draw only a one-term `[[ ]]`.

**Widened at triage, 2026-10-12: a pattern's own parentheses and bars.** Bash
reads the word after an unquoted `=~` with its `(`, `)` and `|` as part of the
word, so `[[ x =~ ^(a|x)$ ]]` is one regular expression, and the word after
`==`, `=` or `!=` with extglob's `@(`, `*(`, `+(`, `?(` and `!(` groups, so
`[[ x == @(a|x) ]]` is one pattern (measured on bash 5.2.21 2026-10-12;
Bash Reference Manual §3.2.5.2 "Conditional Constructs" and §3.5.8.1 "Pattern
Matching"). Docket reads both as operators. They go with this item because
reading `[[ ]]`'s words as the conditional's own is what reads them.

**Not a recurrence of `PL-3Z8B`**, which `docket new` matched on the shared
`touches`: that item is what an arithmetic body is, and this is how a
conditional's operators read. The match is withdrawn because of this
paragraph.

**Generator check.** Found by `PL-C4XY`'s comparison, which is what stops a
departure of this kind reaching `main` from now on; read against `bin/docket
generators --misread` on 2026-10-12, it misreads no recorded fact.

**Route, measured 2026-10-12.** Inside `[[ ]]`, `&&`, `||`, `(`, `)`, `<` and
`>` read as words of the conditional rather than as operators: in
`shell_words` they cut no clause, and in the flat view they are plain
strings, never `Operator`. A group depth refuses what bash 5.2.21 refuses: a
`)` with no group open, a `]]` with one open, and every other operator (`;`,
`|`, `&`, `>>`, `<<`, `<&`, `>|`, `&>`, `<>`, `;;`, `|&`, `<<<`), while a `<(`
process substitution stays one. The word after an unquoted `=~` is read with
`PL-3Z8B`'s matched-pair reader, a `(` opening a pair and `|` part of the
word, and the word after `==`, `=` or `!=` with extglob's `@(`, `*(`, `+(`,
`?(` and `!(` as pairs, as bash's parser reads them under `PST_REGEXP` and
`PST_EXTPAT`. Measured accepted: `[[ -e <(true) ]]`, `[[(a)]]`, `=~ x|y`, `=~
^(a|x)$`, `=~ ( x )`, `== @(a|x)*`, `= @(x)`, `!= !(y)`, `"a"\ @(b)`, and a
newline inside a pair; refused: `[[ ( -n a ]]`, `[[ a ) ]]`, `[[ x == (a) ]]`,
`[[ x == a|b ]]`, `=~ a)b`, `=~ a(b` and `[[ x=~(x) ]]`. Refuted: the
operators as string tokens that `commands` skips, which gives one string two
meanings. `test_a_test_bash_finds_unclosed_is_unreadable` keeps passing, the
generator draws `&&`, `||`, groups, `<`, `>`, `=~` and extglob patterns, and
`.claude/hooks/shell_split.py`'s list of what it does not read loses the
`[[ ]]` operators.

**Done when.** Inside `[[ ]]` an `&&` cuts no clause and `(`, `)`, `||`, `<`
and `>` are read as the conditional's own, a regular expression's or
pattern's groups and bars are part of its word, in both `shell_words` and
`flat_reading`, and the comparison draws them, its known departure rows for
it gone.
