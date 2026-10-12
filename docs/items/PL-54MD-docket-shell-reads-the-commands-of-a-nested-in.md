---
id: PL-54MD
title: docket.shell reads the commands of a $( ) nested in another in an unquoted here-document's body where the inner here-document's compatibility end and the outer substitution's ) share a line - F)), F) ), F)]) or F) ; p x ) - though bash 5.2.21 runs none of them, failing the expansion or cutting the substitution short; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by its own triage, 2026-10-12
added: 2026-10-12
closed: 2026-10-12
pr: 1460
payoff: a substitution a nested here-document's delimiter line closes inside an unquoted body is read as bash runs it - failed, cut short or run - so no reader of the shared lexer names a command bash never runs there
verify: grep -q 'def test_a_substitution_bash_cuts_short_runs_what_bash_runs' subprojects/docket/tests/test_shell.py && grep -qF 'F) ; p x )' subprojects/docket/tests/test_shell.py
reenters: PL-GJKN
recurrences: 2026-10-12 PL-H710 withdrawn 2026-10-12 PL-H710
---

**Problem.** docket.shell reads the commands of a $( ) nested in another in an unquoted here-document's body where the inner here-document's compatibility end and the outer substitution's ) share a line - F)), F) ), F)]) or F) ; p x ) - though bash 5.2.21 runs none of them, failing the expansion or cutting the substitution short; latent

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

[superseded 2026-10-12: one mechanism behind both forms, under **Route** below]
**Not a recurrence of `PL-GJKN`**, which `docket new` matched on the shared
paths. That one is a `$( )` read directly in the body, which bash fails at the
line and `PL-GJKN` now reads as failing. This is one nested inside it, where
bash honours the compatibility end as at the top level unless the outer `)`
shares the line. Bash's reading there is irregular - the outer command runs in
the `F))` form and not in the other three - so `PL-GJKN` pinned the forms bash
reads alike and left these.

**Generator check.** A re-entry of `PL-GJKN`, closed 2026-10-12, whose fix
should have covered it. The fact misread is where bash 5.2.21's parse for a
body-level `$( )`'s end puts it after a line that ended a here-document inside
it: a character early, wherever that `)` comes from the line bash pushed back -
an external behaviour nothing modelled. `PL-GJKN` modelled its symptom at depth
one, every such line failing the expansion, so it left these forms and read
three direct ones as failing where bash runs `p inner` (below). Not `PL-R417`'s
fact, a physical line taken for a statement. Latent, so an ordinary item.

**Route, measured 2026-10-12** against bash 5.2.21's source (the Ubuntu
archive's `bash_5.2.21.orig.tar.xz`, read only) and runs of it. Bash finds the
end of a `$( )` an unquoted body runs with `xparse_dolparen` (parse.y), whose
`rewind_input_string` takes the offset reading reached less what is unread of
the current line and one more for the newline that line's length leaves out.
A line that ends a here-document early - opening with its delimiter, holding a
`)` - has its rest pushed back with the newline counted in (`shell_ungets`,
from `make_here_document` in make_cmd.c), so where the body-level `$( )`'s `)`
is read from that rest, bash's end comes out a character early, on what
precedes the `)`. Not a `)` - `F) )`, `F)])`, `F) ; p x )`, `F)")`, and
`PL-GJKN`'s `F)` - and bash finds no `)` and the expansion fails. A `)` -
`F))` - and bash takes it for the end, runs the text up to it in a child, and
expands what follows as text: the top-level command and later substitutions
run (`F)) $(p z)` runs `p z`), and the child's text leaves open what that `)`
closed, so it is one syntax error that runs nothing where the `$( )` holds no
newline of its own. With one, bash runs the lines before it (`$(p a` over `p
$(p deep <<F` and `F))` runs `p a`), and an escaped `)` closes nothing, so
both are read as the parse found them - every command bash runs among what is
read. Bash's child also re-parses the text with no compatibility end at its
top level (`parse_and_execute`), so where the `$( )`'s own here-document ended
early it reads that body on - `$(p inner <<F` over `F ')'` and `)` runs `p
inner`, which `PL-GJKN`'s rule read as failing. `PL-H710` holds those
over-reads as `WARNED_DEPARTURES`.

So `_Lexer.push_back` records, on the `$( )` the body runs, the span bash reads
again after each such line inside it - not inside a backquote or a nested
body's expansion, which its parse reads past as text - and `_Lexer.slipped`
reads the end at that `)`: unreadable, which `expanded` reads as the expansion
failing; `_Cut`, which drops the `$( )` and goes on; or the reading as found.
`PL-GJKN`'s depth-one raise in `body` is gone: its forms all fail by the same
rule. `FAILED_EXPANSIONS` gains six forms, `CUT_SHORT` pins nine against bash,
and `test_an_escaped_paren_bash_cuts_at_is_read_as_found` the escape, whose
run hands `p` a byte the comparison cannot decode. An unended body under
`bash -c` fails as a file's does, with no newline after the line too.

**Done when.** None of the nested commands in the four forms is read, as bash
runs none of them, and a test pins the four against bash.
