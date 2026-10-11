---
id: PL-GJKN
title: docket.shell's lexer applies the command-substitution here-document end - a line opening with the delimiter and holding a closing parenthesis - inside an unquoted here-document's expanded body, where bash 5.2 does not end the nested body there, so docket reads a command bash never runs; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
payoff: a substitution inside an unquoted here-document body is read as bash reads it, so no reader of the shared lexer names a command bash never runs
verify: grep -q 'def test_a_heredoc_in_an_expanded_heredoc_body_ends_only_at_its_delimiter' subprojects/docket/tests/test_shell.py
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

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`: `shell_words` still reads
`echo inner <<F` as a substitution body and `flat_reading` still substitutes
`echo inner << F ; )`; bash 5.2.21 still warns that the here-document is
delimited by end of file, reports the unexpected end of file looking for `)`,
and prints only `after`.

**Why it matters.** docket reads a command bash never runs, and every reader
of the shared lexer - docket's audits, `tools/doc_check.py`, the Bash guards
through `.claude/hooks/shell_split.py` - takes that reading. The module's own
docstring promises the opposite, that a substitution the delimiter line cuts
fails and nothing it began is kept, so the code and its stated contract
disagree in the reader everything else trusts.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. The code is new
in `#1390`. Re-read 2026-10-11: latent, so an ordinary item under that closed,
spent head; found live, it would reopen it.

**Done when.** Inside an expanded here-document body a nested here-document
ends only at its delimiter line, and a substitution bash cannot close there is
read as bash reads it; a test pins the form above against bash.
