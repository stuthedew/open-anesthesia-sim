---
id: PL-H710
title: docket.shell reads an expanded here-document body's $( ) as the parse bash finds its end with reads it, though bash's child re-parses that text with no compatibility end at its top level and runs only the lines before one a cut leaves open, so after a line ending a body of the $( )'s own, or a cut after a line of its own, docket reads commands bash never runs, never fewer; latent
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py, docs/items/PL-54MD-docket-shell-reads-the-commands-of-a-nested-in.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by its own triage, 2026-10-12
added: 2026-10-12
closed: 2026-10-18
payoff: a here-document body's substitution is read as bash's child runs its text, so no reader of the shared lexer names a command no run makes there
verify: ! grep -qF 'PL-H710' subprojects/docket/tests/test_shell.py
---

**Problem.** docket.shell reads an expanded here-document body's $( ) as the parse bash finds its end with reads it, though bash's child re-parses that text with no compatibility end at its top level and runs only the lines before one a cut leaves open, so after a line ending a body of the $( )'s own, or a cut after a line of its own, docket reads commands bash never runs, never fewer; latent

**Found 2026-10-12** building `PL-54MD`, whose route models the parse bash
5.2.21 finds a body-level `$( )`'s end with and not the run of its text that
follows. Bash runs that text in a child with `parse_and_execute` (subst.c's
`command_substitute`): at its top level no line ends a here-document early,
and it parses and runs one line at a time, stopping at the first syntax
error. Where either matters, docket reads the text as the parse for its end
found it.

**Reproduced 2026-10-12** against bash 5.2.21, each in an unquoted body over
`p after`, with `p` recording its words: `$(p a` over `p $(p deep <<F` and
`F))` runs `p a`, the top `p` and `p after`, and docket reads `p deep` and the
inner `p` too; `$(p inner <<F` over `F ')'` and `)` runs `p inner`, and docket
reads a command `)` too; `$(p inner <<'F'` over `F p y; $(p w))` runs `p
inner`, and docket reads `p y` and `p w` too. Each is a row of
`WARNED_DEPARTURES` in `subprojects/docket/tests/test_shell.py`.

**Why it matters.** docket reads every command bash runs here and some it
does not, so a guard refuses or an audit names a command no run makes -
never the reverse. Latent: no tracked here-document body holds a `$( )` with
a `<<` inside it.

**Not a recurrence of `PL-54MD`**, which `docket new` matched on the shared
paths and this filing withdraws: it is the part of that item's mechanism its
route left, by bash's child rather than its parse.

**Generator check.** A one-off, the residual `PL-54MD` filed: the fact is how
bash's child re-reads a substitution's text, which nothing reads twice here.

**Done when.** Each row is read as bash runs it, the rows are gone from
`WARNED_DEPARTURES`, and a test pins them against bash.
