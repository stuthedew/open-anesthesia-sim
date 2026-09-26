---
id: PL-P7J7
title: docket's verify.py reads a verify: command through its own quote regexes and shlex - _outside_quotes, _blanked, PIPELINE_END_RE and TRAILING_COMMENT_RE, and reaches_outside_tree's shlex.split - beside checks.py's _shell_words, so a ' inside double quotes blanks a real bin/docket verify and reenters_verify misses it
status: untriaged
feature: one-answer
added: 2026-09-26
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

**Generator check.** `PL-PVW2`'s fact again - how a shell command splits - and
the question `PL-B5VZ` answered for `checks.py`, asked in the module `checks.py`
imports: a member of that head by its fact, for triage to confirm. Not a
recurrence of `PL-B5VZ`, although `docket new` recorded one there, matching on
the `PL-PVW2` item file both declare: `PL-B5VZ`'s fix is `checks.py`'s own
readers, which these are not. One reading for both means `_shell_words` moves
out of `checks.py` into a module both import, since `checks.py` imports
`verify.py`.
