---
id: PL-BHS7
title: docket.shell reads a nested backquote's body from the raw text without first removing the backslash before an inner backquote, dollar or backslash, so the inner command bash runs is missed by shell_words and by the guards' flat reading; latent
status: untriaged
added: 2026-10-10
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

**Generator check.** Not a member of `PL-R417`: the substitution is read
whole within one line; its escapes are not undone.

**Done when.** A backquoted body is read after its escapes are removed, so the
nested command is a substitution of its own; a test pins the form above
against bash.
