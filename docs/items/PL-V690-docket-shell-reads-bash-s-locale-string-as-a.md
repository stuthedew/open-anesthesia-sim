---
id: PL-V690
title: docket.shell reads bash's $"..." locale string as a literal $ before a double-quoted string, so p $"git" push is the words p, $git and push to docket and the guard hooks, where bash runs p with git and push; latent
status: untriaged
feature: shell-reads-as-bash
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py, docs/items/PL-GJKN-docket-shell-s-lexer-applies-the-command.md
added: 2026-10-12
---

**Problem.** docket.shell reads bash's $"..." locale string as a literal $ before a double-quoted string, so p $"git" push is the words p, $git and push to docket and the guard hooks, where bash runs p with git and push; latent

**Found 2026-10-12** while building `PL-C4XY`'s bash comparison in
`subprojects/docket/tests/test_shell.py`: a `$"..."` word gave docket a
different word from bash's, so the generator leaves the form out and the
comparison pins today's reading as a known departure naming this item.

**Reproduced 2026-10-12** on `main` at `98673556`:

```text
p $"loc"         bash runs: p loc         shell_words: p, $loc        flat_reading: p, $loc
p $"git" push    bash runs: p git push    shell_words: p, $git, push  flat_reading: p, $git, push
```

Bash translates a double-quoted string a `$` leads by the current locale, and
where the locale is C or POSIX or holds no translation "the dollar sign is
ignored" (Bash Reference Manual §3.1.2.5 "Locale-Specific Translation"). The
lexer keeps the `$` as a literal character and reads the double quotes after
it, so the word's text names a parameter expansion bash never performs, in
docket's view and in the hooks'.

**Reach.** A guard keyed on a command's head reads `$"git" push` as `$git
push`. Latent: on 2026-10-12 no workflow step, tracked `.sh` file or fenced
shell sample writes one, the only `$"` in the tree being inside Python regexes
in two hooks' quoted here-document bodies, and `verify:` fields refuse one at
its unquoted `$`.

**Not a recurrence of `PL-GJKN`**, which `docket new` matched on the shared
`touches`: that item is where a here-document inside an expanded body ends, and
this is how one quoting form reads. The match is withdrawn because of this
paragraph.

**Generator check.** Found by `PL-C4XY`'s comparison, which is what stops a
departure of this kind reaching `main` from now on; read against `bin/docket
generators --misread` on 2026-10-12, it misreads no recorded fact.

**Done when.** `$"..."` reads as the double-quoted string with its `$` dropped,
as bash reads it in the C locale, in both views, and the comparison's known
departure row for it is gone.
