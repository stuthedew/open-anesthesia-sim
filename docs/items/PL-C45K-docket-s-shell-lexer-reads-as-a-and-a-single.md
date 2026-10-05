---
id: PL-C45K
title: docket's shell lexer reads $'...' as a $ and a single-quoted string, so script_lines takes everything after a $'...' holding an escaped quote for one unreadable piece, where bash reads on and the hooks' shell_split reads it as bash does; latent
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py
added: 2026-10-05
---

**Problem.** docket's shell lexer reads $'...' as a $ and a single-quoted string, so script_lines takes everything after a $'...' holding an escaped quote for one unreadable piece, where bash reads on and the hooks' shell_split reads it as bash does; latent

**Found 2026-10-05 working `PL-2JYP` (`#1377`).** Bash reads `$'...'` as an
ANSI-C quoted string, in which a backslash escapes the next character, an
escaped `'` included (Bash Reference Manual § 3.1.2.4 "ANSI-C Quoting").
docket's lexer reads the `$` as a word character and the rest as a
single-quoted string, which ends at the first `'`. So `script_lines` over
`echo $'a\'b'` and `echo next` returns the whole script as one piece, which
`shell_words` declines, where bash 5.2.21 prints `a'b` and `next`. For a
`verify:` field the reading is right, since the admitted shapes never use a
`$'...'` and refuse it at its `$`; the defect is the cut. The hooks'
`.claude/hooks/shell_split.py` reads `$'...'` as bash does (`_ansi_c_end`).

Latent: no tracked workflow step, `.sh` file or Makefile holds a `$'`
(`git grep`, 2026-10-05; its one match, in `.github/workflows/drift.yml`, is a
Python raw string inside a here-document body).

**Not a recurrence of `PL-2JYP`.** `bin/docket new` matched it there on
`shell.py`. That item is a statement continued across lines; this is a quoting
form misread on one line, so the match is withdrawn on this brief. Not a member
of `PL-R417`, for the same reason.

**Done when.** `script_lines` reads a `$'...'` to the `'` that closes it, a
backslash escaping the next character, so `echo $'a\'b'` over `echo next` is
two pieces; `joined_text` keeps a backslash-newline inside one, as bash does;
`shell_words` still refuses it at its `$`; and a test in
`subprojects/docket/tests/test_shell.py` pins each.
