---
id: PL-BHS7
title: docket.shell reads a nested backquote's body from the raw text without first removing the backslash before an inner backquote, dollar or backslash, so the inner command bash runs is missed by shell_words and by the guards' flat reading; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1436
payoff: a command nested in backquotes is read as the substitution bash runs, so a guard or a docket audit sees the inner command instead of escaped words
verify: grep -q 'def test_a_nested_backquote_is_read_after_its_escapes_are_removed' subprojects/docket/tests/test_shell.py
---

**Problem.** docket.shell reads a nested backquote's body from the raw text without first removing the backslash before an inner backquote, dollar or backslash, so the inner command bash runs is missed by shell_words and by the guards' flat reading; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
docket's shared readers. Inside backquotes, a
backslash before a backquote, dollar or backslash is removed before the body is
read as a command (POSIX XCU § 2.6.3), which is how backquotes nest.

```text
x=`p \`p bq\``
```

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against bash 5.2.21, which runs the inner `p bq`: `shell.backquote`
gives the substitution body as the words `p`, a backquote-led `p` and `bq`
with a trailing backquote, and reads no inner command. The hooks read the same
body through `flat_reading`. Latent: no tracked script nests backquotes.

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`: `shell_words` still gives
the body as `p`, a backquote-led `p` and `bq` with a trailing backquote, and
`flat_reading` substitutes those three words; bash 5.2.21, with `p` a function
echoing its arguments, sets `x` to `p:p:bq`, so the inner `p bq` runs.

**Why it matters.** A guard reading a nested backquote's inner command as
plain words never sees a gate or a pruning `git` placed there, and docket's own
readers of the same shared lexer take the same wrong words. Latent, and the
cheaper for it: `$( )` is the spelling sessions write, so the fix lands before
anything depends on the misreading.

**Generator check.** Not a member of `PL-R417`: the substitution is read
whole within one line; its escapes are not undone. Read against `bin/docket
generators --misread` on 2026-10-11: the fact is how bash undoes a backquoted
body's escapes before reading it, which no head's `misread:` states;
`PL-61FT`'s (what a shell command runs) is the nearest, and is a guard's model
of a command rather than the shared lexer's quoting rule. A one-off.

**Done when.** A backquoted body is read after its escapes are removed, so the
nested command is a substitution of its own; a test pins the form above
against bash.
