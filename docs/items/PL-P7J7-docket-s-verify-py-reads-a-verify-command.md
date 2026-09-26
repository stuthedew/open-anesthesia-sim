---
id: PL-P7J7
title: docket's verify.py reads a verify: command through its own quote regexes and shlex - _outside_quotes, _blanked, PIPELINE_END_RE and TRAILING_COMMENT_RE, and reaches_outside_tree's shlex.split - beside checks.py's _shell_words, so a ' inside double quotes blanks a real bin/docket verify and reenters_verify misses it
priority: P2
effort: M
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, docs/items/PL-PVW2-predicates-the-apparatus-asks-repeatedly-which.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; a member of PL-PVW2, docket's reading of a verify: command
added: 2026-09-26
payoff: every rule in docket that reads a verify: command reads it through one quote-aware lexer, so none misses a command behind an apostrophe, a glued pipe or a quoted &&
verify: grep -q 'def test_an_apostrophe_in_double_quotes_hides_no_command' subprojects/docket/tests/test_verify.py
---

**Problem.** docket's verify.py reads a verify: command through its own quote regexes and shlex - _outside_quotes, _blanked, PIPELINE_END_RE and TRAILING_COMMENT_RE, and reaches_outside_tree's shlex.split - beside checks.py's _shell_words, so a ' inside double quotes blanks a real bin/docket verify and reenters_verify misses it

**Found 2026-09-26 triaging `PL-B5VZ`** (checks.py's own readers of a
`verify:` command), by asking where else docket reads one. `verify.py` does,
with spellings of its own: `_outside_quotes` and `_blanked` find quoted spans
with the regexes `'[^']*'` and `"[^"]*"`, single quotes first; `PIPELINE_END_RE`
cuts clauses at `&&`, `||` and `;` in the blanked text; `TRAILING_COMMENT_RE`
strips `#.*$`; and `reaches_outside_tree` splits with
`shlex.split(comments=True)`. `checks.py` calls three of them - `never_fails`,
`reads_check_output` and `reenters_verify` - beside `_shell_words`. Probed on
`4d6f86b9`:

    grep -qF "it's" a.md && bin/docket verify PL-K7QX && grep -qF "it's" b.md
        reenters_verify: False - the single-quote regex runs from one apostrophe
        to the next, across the double quotes and the command between them
    grep -qF 'x' a.md|curl -s https://example.com
        reaches_outside_tree: False - shlex.split keeps `a.md|curl` one word
    grep -qF "x \"y && z\" w" docs/a.md
        command_paths: cuts a clause at the quoted `&&`, so `z` reads as a program

The first is a miss in the unsafe direction: a command that re-enters `docket
verify` goes unrefused. `reaches_outside_tree` documents its misses as the safe
direction, and `command_paths` over-reports by design. The admitted shapes
refuse the first two commands wherever they bind, so those reach the
grandfathered commands; `command_paths` reads admitted commands as well.

[superseded 2026-09-26: triaged below as `PL-PVW2`'s member] **Generator check.** `PL-PVW2`'s fact again - how a shell command splits - and
the question `PL-B5VZ` answered for `checks.py`, asked in the module `checks.py`
imports: a member of that head by its fact, for triage to confirm. Not a
recurrence of `PL-B5VZ`, although `docket new` recorded one there, matching on
the `PL-PVW2` item file both declare: `PL-B5VZ`'s fix is `checks.py`'s own
readers, which these are not. One reading for both means `_shell_words` moves
out of `checks.py` into a module both import, since `checks.py` imports
`verify.py`.

**Reproduced 2026-09-26 against `70818cfc`**, after #1095: the three commands
above answer as they did on `4d6f86b9` - `reenters_verify` False,
`reaches_outside_tree` False, and `command_paths` returns `docs/a.md`, `qF`,
`w`, `x` and `y` but not `z`.

**Generator check, answered.** A member of `PL-PVW2`: its fact - how a shell
command splits - answered a third way inside docket, beside `checks.py`'s
`_shell_words` that `PL-B5VZ` made the one reading for that file. The same
triage keeps docket's reading its own rather than the hooks'
`.claude/hooks/shell_split.py`, for the two reasons `PL-B5VZ` records.

**On the Fix generators project's list** (project owner, 2026-09-26, ratified,
over leaving it off the list).

**Design, 2026-09-26.** Worked out at triage by the thread that stopped for
length before building it; a later session builds it as written or says why not.

- **Where.** `_shell_words`, `_Word`, `_Clause`, `_Reading`, `_OPERATORS`,
  `_PLAIN`, `_GLOB` and `_SHELL_OPERATORS` move from `checks.py` to a new
  `subprojects/docket/src/docket/shell.py`, public there, and both files import
  it. Every refusal message stays word for word, at the character it names now.
- **Command substitution, read as bash reads it** (Bash Reference Manual
  §3.5.4). A `$( )`, quoted or not, and a backquote open a body the same lexer
  reads, over the same string so its spans stay absolute: a `$( )` ends at the
  `)` that closes it, a backquote at the first backquote no backslash escapes.
  The word keeps the substitution's raw text, as a double-quoted one does now,
  and `Reading.substitutions` holds every body at any depth, in order. This is
  what replaces `_outside_quotes` keeping a double-quoted span that carries
  `$(` or a backquote, which `test_capturing_docket_checks_output_raises_the_same_advisory`
  pins (`test -z "$(bin/docket check)"`). An unclosed body is unreadable, as
  bash refuses it. `_Clause` gains its tokens' spans.
- **The five readers**, over the reading and its substitutions:
  `never_fails` is the one clause's words, a trailing `;` dropped, joined and
  looked up in `NEVER_FAILS`; `reenters_verify` is a word `docket` or ending
  `/docket` followed by the word `verify`; `reads_check_output` answers
  "captures" for a `docket check` inside a substitution and "pipes" for a `|`
  or `|&` after one before the next `&&`, `||`, `;` or `&`, so `>|` stays a
  redirection; `command_paths` cuts at those four and the `case` terminators
  from the tokens, takes programs from the words, keeps the loose
  `PATH_TOKEN_RE` scan over each clause's raw span, and reports every
  path-shaped token of an unreadable command, the over-report its docstring
  promises; `reaches_outside_tree` reads every word, in any position as
  `shlex.split` did, and answers False for an unreadable command.
- **Changed answers, each bash's reading:** a quoted `'true'` never fails, a
  quoted `"docket" verify` re-enters, a comment's paths are no longer read.
  Not read, as before: a command run through `sh -c` or `eval`, and `$'...'`,
  which the admitted shapes refuse at its `$`.
- **Checked the way `PL-B5VZ` checked:** every rule in `checks.py` and each of
  the five readers over the store's 1,356 `verify:` commands, before and after,
  with any difference named in the pull request.

**Why it matters.** One reader of a `verify:` command misses a real
`bin/docket verify` behind an apostrophe inside double quotes, the unsafe
direction for a rule that exists to refuse recursion, and two more read a
pipe or a quoted `&&` otherwise than bash. `checks.py` and `verify.py` would
still answer "how does this command split" two ways, which is `PL-PVW2`'s
mechanism, and the next rule over a `verify:` would copy one of them.

**Done when.** `verify.py` keeps no `shlex`, `_outside_quotes`, `_blanked`,
`SINGLE_QUOTED_RE`, `DOUBLE_QUOTED_RE`, `PIPELINE_END_RE`,
`TRAILING_COMMENT_RE`, `DOCKET_VERIFY_RE`, `DOCKET_CHECK_RE` or `WORD_RE`;
`checks.py` and `verify.py` read a command through `shell.py` alone; and
`test_an_apostrophe_in_double_quotes_hides_no_command` in
`subprojects/docket/tests/test_verify.py` holds the three commands above, a
`bin/docket verify` inside `"$( )"`, an unquoted `$( )` and a backquote, with
the existing reader tests unchanged.
