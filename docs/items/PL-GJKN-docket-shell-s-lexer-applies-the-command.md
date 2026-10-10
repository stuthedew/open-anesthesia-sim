---
id: PL-GJKN
title: docket.shell's lexer applies the command-substitution here-document end - a line opening with the delimiter and holding a closing parenthesis - inside an unquoted here-document's expanded body, where bash 5.2 does not end the nested body there, so docket reads a command bash never runs; latent
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** docket.shell's lexer applies the command-substitution here-document end - a line opening with the delimiter and holding a closing parenthesis - inside an unquoted here-document's expanded body, where bash 5.2 does not end the nested body there, so docket reads a command bash never runs; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
docket's shared readers. `_Lexer.expanded`, new in
`#1390` (`PL-P95F`), reads the command substitutions inside an unquoted
here-document's body (POSIX XCU § 2.7.4 expands them) by calling
`read(closes=True)`, which builds a frame that takes a line opening with a
nested here-document's delimiter and holding a `)` for that document's end -
the compatibility end bash honours for a `$( )` at top level. The module's own
docstring says a substitution the delimiter line cuts fails its expansion and
nothing reading it began is kept.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against bash 5.2.21, which warns that the nested here-document is
delimited by end of file, reports an unexpected end of file looking for the
`)`, runs neither `cat` nor `echo inner`, and prints `after`:

```text
cat <<E
$(echo inner <<F
F)
E
echo after
```

`shell_words` reads `echo inner <<F` as a substitution body, and
`flat_reading` substitutes `echo inner << F ; )`; the same `$(echo inner <<F`
over `F)` outside a here-document does run in bash. Latent: no tracked
here-document body holds a `$(` with a `<<` inside it.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. The code is new
in `#1390`.

**Done when.** Inside an expanded here-document body a nested here-document
ends only at its delimiter line, and a substitution bash cannot close there is
read as bash reads it; a test pins the form above against bash.
