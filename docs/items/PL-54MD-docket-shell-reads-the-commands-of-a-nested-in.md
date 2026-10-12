---
id: PL-54MD
title: docket.shell reads the commands of a $( ) nested in another in an unquoted here-document's body where the inner here-document's compatibility end and the outer substitution's ) share a line - F)), F) ), F)]) or F) ; p x ) - though bash 5.2.21 fails that expansion and runs none of them; latent
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py
added: 2026-10-12
---

**Problem.** docket.shell reads the commands of a $( ) nested in another in an unquoted here-document's body where the inner here-document's compatibility end and the outer substitution's ) share a line - F)), F) ), F)]) or F) ; p x ) - though bash 5.2.21 fails that expansion and runs none of them; latent

**Found 2026-10-12** closing `PL-GJKN`, by the bash comparison in
`subprojects/docket/tests/test_shell.py`, which runs a script through bash with
`p` recording its words and compares the runs with the lexer's reading.

**Reproduced 2026-10-12** on this branch over `main` at `89fe11d0`, against
bash 5.2.21:

```text
p <<E
$(p $(p deep <<F
F))
E
p after
```

Bash warns that the here-document is delimited by end of file, reports an
unexpected end of file looking for the matching `)`, and runs the outer `p`
and `p after`. docket reads `p deep` and the inner `p` as well. With `F) )`,
`F) ; p x )`, or `F)])` closing a `[$( )]` word on that line instead, bash
runs only `p after`, while docket reads `p deep`, the `p x` where there is
one, and both `p`s. The same script outside the here-document runs `p deep`
in bash, and where the outer `)` stands on a later line, bash and docket read
the body alike.

**Why it matters.** Every reader of the shared lexer - docket's audits,
`tools/doc_check.py`, the Bash guards through `.claude/hooks/shell_split.py` -
takes a command bash never runs. Latent: no tracked here-document body holds a
nested `$(` with a `<<` inside it.

**Not a recurrence of `PL-GJKN`**, which `docket new` matched on the shared
paths. That one is a `$( )` read directly in the body, which bash fails at the
line and `PL-GJKN` now reads as failing. This is one nested inside it, where
bash honours the compatibility end as at the top level unless the outer `)`
shares the line. Bash's reading there is irregular - the outer command runs in
the `F))` form and not in the other three - so `PL-GJKN` pinned the forms bash
reads alike and left these.

**Generator check.** The mechanism `PL-GJKN` fixed one level down, under
`PL-R417` (closed, spent). Latent, so an ordinary item.

**Done when.** None of the nested commands in the four forms is read, as bash
runs none of them, and a test pins the four against bash.
