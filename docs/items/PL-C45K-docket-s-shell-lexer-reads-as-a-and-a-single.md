---
id: PL-C45K
title: docket's shell lexer reads $'...' as a $ and a single-quoted string, so script_lines takes everything after a $'...' holding an escaped quote for one unreadable piece, where bash reads on and the hooks' shell_split reads it as bash does; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: .claude/hooks/shell_split.py, .claude/hooks/floor-interpreter-guard.sh, .claude/hooks/gate-status-guard.sh, .claude/hooks/no-prune-guard.sh, .claude/hooks/push-check-guard.sh, subprojects/docket/src/docket/shell.py, subprojects/docket/src/docket/__init__.py, subprojects/docket/tests/test_shell.py, tests/unit/test_shell_reader.py, tests/unit/test_doc_check.py, tests/unit/test_floor_interpreter_guard.py, tests/unit/test_no_prune_guard.py, tests/unit/test_push_check_guard.py, docs/ARCHITECTURE.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-05 triage pass
added: 2026-10-05
closed: 2026-10-10
pr: 1390
payoff: a workflow step or a documented command holding $'...' with an escaped quote can no longer hide every command after it from the checks that read what CI runs
verify: grep -q 'def test_an_ansi_c_quoted_string_ends_at_the_quote_bash_ends_it_at' subprojects/docket/tests/test_shell.py
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

**Reproduced 2026-10-05 at triage** on `main` at `b67dace8`: `script_lines`
over `"echo $'a\\'b'\necho next\n"` (run as `PYTHONPATH=subprojects/docket/src
python3 -c ...`) returned the whole script as one piece at offset 0, where
bash 5.2.21 running the same two lines printed `a'b` and `next`, and the hooks'
`shell_split.segments` read two commands.

**Why it matters.** `script_lines` is how `tools/doc_check.py` reads the
commands a workflow's `run:` steps and a Markdown fence execute
(`workflow_commands`, `_make_mentions`), so a `$'...'` holding an escaped quote
would hide every command after it from those checks without a word. Nothing in
the tree holds one today, which is why it is latent; the first one written
would switch the checks off for the rest of its script.

**Generator check.** An instance of `PL-KGYT`'s fact, which spelling of a
repeated predicate is the answer when tools, hooks and docket each spell it,
filed after that head closed on 2026-10-01: the hooks' lexer spells bash's
ANSI-C quoting (`_ansi_c_end`) and docket's spells it wrong. It joins
`PL-74T0`'s cluster 1 (`PL-P72R`, `PL-Z8RS`, `PL-HNXS`), which already counts
the three post-close instances the triage rule reads as a fix that did not
hold, and whose head `PL-74T0` is to record or refuse; the two lexers it names
are `PL-JNYL`'s, whose merge would make it impossible. Not a member of
`PL-R417`: the misread is where a quote ends on one line, not a statement
continued across lines.

**Folded into `PL-R417`'s shell batch** (project owner, 2026-10-10, ratified,
over leaving it out of the batch as the Order did). `PL-JNYL`'s merged reader
reads `$'...'` as the hooks' reader did, so the defect goes with the merge and
its test lands with it. Bash 5.2.21 keeps a backslash-newline inside one:
`x=$'a\` over `b'` holds `a`, a backslash, a newline and `b` (measured
2026-10-10).

**Done when.** `script_lines` reads a `$'...'` to the `'` that closes it, a
backslash escaping the next character, so `echo $'a\'b'` over `echo next` is
two pieces; `joined_text` keeps a backslash-newline inside one, as bash does;
`shell_words` still refuses it at its `$`; and a test in
`subprojects/docket/tests/test_shell.py` pins each.

**Built 2026-10-10 (`#1390`).** Fixed in the merged reader: `script_lines`
reads a `$'...'` to the quote that closes it, a backslash escaping the next
character, so `echo $'a\'b'` over `echo next` is two pieces where `main`'s
docket reader returned the rest of the script as one unreadable piece;
`joined_text` keeps a backslash-newline inside one, as bash does; and
`shell_words` still refuses it at its `$`.
`test_an_ansi_c_quoted_string_ends_at_the_quote_bash_ends_it_at` pins all
three.
