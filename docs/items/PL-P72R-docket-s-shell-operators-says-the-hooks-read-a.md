---
id: PL-P72R
title: docket's shell.OPERATORS says the hooks read a command by the same table as .claude/hooks/shell_split.py's, and nothing checks it: the two differed by <<- until PL-Q9LK
priority: P3
effort: S
status: ready
classes: test
feature: one-answer
touches: subprojects/docket/src/docket/shell.py, .claude/hooks/shell_split.py, tests/unit/test_shell_reader.py
added: 2026-10-03
payoff: the hooks and docket cannot drift apart on how a command splits without a test failing
verify: grep -q 'def test_the_hooks_read_the_one_operators_table' tests/unit/test_shell_reader.py
---

**Problem.** docket's shell.OPERATORS says the hooks read a command by the same table as .claude/hooks/shell_split.py's, and nothing checks it: the two differed by \<\<- until PL-Q9LK

**Checked 2026-10-03 at triage.** The two tables agree today: docket's
`shell.OPERATORS` and `.claude/hooks/shell_split.py`'s `OPERATORS` hold the
same operators, compared as sets. No test names `OPERATORS` in
`subprojects/docket/tests/` or `tests/unit/`, so the docstring's claim that the
hooks read a command by the same table is held by nothing, and it has been
false once already, by `<<-`, until `PL-Q9LK`.

**Why it matters.** A guard hook and docket that split one command differently
answer differently about what it runs: the hook refuses or passes on one
reading while docket's checks read another. The next operator added to one
table and not the other drifts with no failure anywhere.

**Done when.** A test fails when the two tables differ, or one table is the
only spelling and the other side reads it.

**Generator check.** An instance of `PL-KGYT`'s fact, filed after that head
closed on 2026-10-01: two spellings of one table, held to each other by
nothing. With `PL-Z8RS` it is the second such instance since KGYT closed, one
short of the three the triage rule reads as a fix that did not hold; `PL-74T0`
records or refuses that as its cluster 1.
