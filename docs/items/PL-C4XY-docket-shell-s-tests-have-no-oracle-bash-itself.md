---
id: PL-C4XY
title: docket.shell's tests have no oracle: bash itself could check the lexer's reading of generated commands
priority: P3
effort: M
status: done
classes: test
feature: reader-checks
touches: subprojects/docket/tests/test_shell.py
added: 2026-10-10
closed: 2026-10-12
pr: 1444
payoff: a shell form the lexer misreads fails the pull request that first writes it, instead of waiting for an auditor's sweep after it merges
verify: grep -q 'def test_the_lexer_reads_generated_commands_as_bash_does' subprojects/docket/tests/test_shell.py
---

**Problem.** `docket.shell` is the one shared reader with no reference in
its tests, since no shell library reads both views as bash does (`PL-JNYL`).
Bash itself can be the oracle: the review had `declare -f` print bash's parse
of `PL-0CJC`'s form. Generated commands, compared through that, would find a
lexer defect on the pull request that first writes the form, as the Markdown
and front-matter references do for theirs.

**Found 2026-10-10** by the parsing review in `PL-R417`'s closing sweep thread
(link 23). The owner chose to have `PL-R417`'s last batch add the review's two
differential tests in CI, and this follow-up to be filed as an ordinary item.

**Reproduced 2026-10-11** on `main` at `16a20a4f`: the premise holds.
`subprojects/docket/tests/test_shell.py` carries 11 hand-written cases, each
"run through bash 5.2.21 first", and runs no shell; `tests/unit/test_shell_reader.py`
starts a subprocess only to measure the guards' import cost. The two references
`PL-R417` added are `tests/unit/test_inline_reference.py` (markdown-it-py) and
`subprojects/docket/tests/test_frontmatter_reference.py` (PyYAML); nothing
compares the shell lexer with bash.

**Why it matters.** `PL-0CJC`, `PL-BHS7` and `PL-GJKN` were each found by an
auditor's sweep after the code holding them had merged, two of them in
`#1390`'s rewrite. The Markdown and front-matter readers now fail the pull
request that first writes a form they misread; the shell lexer, which docket's
audits and every Bash guard share, is the one shared reader still waiting on a
sweep.

**Generator check.** Not a member of `PL-R417`: a guard that would make its
members fail loudly, not a reader that misreads where a statement ends. Read
against `bin/docket generators --misread` on 2026-10-11: it misreads no fact;
it is work the owner asked for in `PL-R417`'s answer of 2026-10-10.

**Done when.** A test compares `docket.shell`'s reading of generated commands
with bash's own, or the comparison is shown not to reach the forms the lexer
reads.
