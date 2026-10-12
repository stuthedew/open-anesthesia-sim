---
id: PL-48ZJ
title: docket.shell keeps a $'...' word's escapes as written, so p $'\x41' is the words p and \x41 to docket and the guard hooks, where bash hands p the word A; latent
status: untriaged
feature: shell-reads-as-bash
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py, docs/items/PL-3Z8B-docket-shell-reads-arithmetic-as-commands-a.md
added: 2026-10-12
---

**Problem.** docket.shell keeps a $'...' word's escapes as written, so p $'\x41' is the words p and \x41 to docket and the guard hooks, where bash hands p the word A; latent

**Found 2026-10-12** while building `PL-C4XY`'s bash comparison in
`subprojects/docket/tests/test_shell.py`: a `$'...'` word holding a backslash
gave docket a different word from bash's, so the generator draws `$'...'`
without one and the comparison pins today's reading as a known departure
naming this item.

**Reproduced 2026-10-12** against `shell.py` as `main` holds it at `eb520ef4`:

```text
p $'\x41'     bash runs: p A      shell_words: p, \x41     flat_reading: p, \x41
p $'a\'b'     bash runs: p a'b    shell_words: p, a\'b     flat_reading: p, a\'b
p $'a\nb'     bash runs: p with a, a newline and b as one word; both views: p, a\nb
```

Bash replaces each backslash escape in a `$'...'` string as the ANSI C
standard specifies (Bash Reference Manual §3.1.2.4 "ANSI-C Quoting"). The
lexer finds where one ends, an escaped apostrophe included, but keeps the
text between as written (`shell.py`'s "its escapes kept as written, which no
reader decodes"), so the word every reader is handed is not the one bash
passes on.

**Reach.** A guard keyed on a word reads `$'\x41'` as `\x41`. Latent: on
2026-10-12 no workflow step, tracked `.sh` file or fenced sample writes a
`$'...'` with a backslash in it, and `verify:` fields refuse a `$'` at its `$`
(`PL-C45K`).

**Not a recurrence of `PL-3Z8B`**, which `docket new` matched on the shared
`touches`: that item is what an arithmetic body is, and this is what one
quoting form's text is. The match is withdrawn because of this paragraph.

**Generator check.** Found by `PL-C4XY`'s comparison, which is what stops a
departure of this kind reaching `main` from now on; read against `bin/docket
generators --misread` on 2026-10-12, it misreads no recorded fact.

**Done when.** A `$'...'` word's text has its escapes replaced as §3.1.2.4
lists them, in both `shell_words` and `flat_reading`, the comparison draws
`$'...'` with escapes in it, and its known departure row for this is gone.
