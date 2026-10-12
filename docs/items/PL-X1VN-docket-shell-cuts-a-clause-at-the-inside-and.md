---
id: PL-X1VN
title: docket.shell cuts a clause at the && inside [[ ]] and reads its (, ), ||, < and > as operators, so [[ -n a && -n b ]] && p x is the clauses [[ -n a, -n b ]] and p x to every reader, where bash runs one conditional and p x; latent
status: untriaged
feature: shell-reads-as-bash
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py, docs/items/PL-3Z8B-docket-shell-reads-arithmetic-as-commands-a.md
added: 2026-10-12
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

**Not a recurrence of `PL-3Z8B`**, which `docket new` matched on the shared
`touches`: that item is what an arithmetic body is, and this is how a
conditional's operators read. The match is withdrawn because of this
paragraph.

**Generator check.** Found by `PL-C4XY`'s comparison, which is what stops a
departure of this kind reaching `main` from now on; read against `bin/docket
generators --misread` on 2026-10-12, it misreads no recorded fact.

**Done when.** Inside `[[ ]]` an `&&` cuts no clause and `(`, `)`, `||`, `<`
and `>` are read as the conditional's own, in both `shell_words` and
`flat_reading`, and the comparison's known departure row for it is gone.
