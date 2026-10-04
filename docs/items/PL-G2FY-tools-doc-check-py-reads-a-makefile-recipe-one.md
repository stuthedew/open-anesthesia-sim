---
id: PL-G2FY
title: tools/doc_check.py reads a Makefile recipe one tab-led line at a time, so a recipe command continued by a backslash is declined by gate parity and compared as a fragment by the coverage gate, where make hands the shell the command whole
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-03 triage pass
added: 2026-10-03
closed: 2026-10-04
pr: 1338
payoff: a Makefile recipe line continued with a backslash is compared with CI as the whole command make runs, not as a fragment
verify: grep -q 'def test_recipe_commands_join_a_backslash_continuation' tests/unit/test_doc_check.py
---

**Problem.** tools/doc_check.py reads a Makefile recipe one tab-led line at a time, so a recipe command continued by a backslash is declined by gate parity and compared as a fragment by the coverage gate, where make hands the shell the command whole

**Reproduced 2026-10-03 at triage.** `_recipe_commands` on a recipe whose
`python3 tools/a.py` line ends in a backslash and continues onto a tab-led
`--strict` returns two commands, the first still ending in the backslash, where
make hands the shell one. The `Makefile` holds no continued recipe line today.

**Why it matters.** Latent, and half of it silent: gate parity declines a
continued command with a note, but the coverage gate compares its first
fragment against CI's whole command, so a coverage run split across two lines
reads as differing from CI where it matches, or as matching on its first line
while the continuation differs.

**Done when.** A recipe command continued by a backslash is read as the one
command make hands the shell, by gate parity and the coverage gate alike, and a
test pins the continued case.

[superseded 2026-10-04: a member of `PL-R417`, below] **Generator check.** A
one-off: the Makefile's readers miss make's continuation rule rather than
disagreeing with another spelling of it, so not `PL-KGYT`'s fact. Filed in
`PL-Q9LK`'s closing commit as the sibling its workflow-side fix left, so not a
re-entry.

**Generator check, 2026-10-04.** A member of `PL-R417`: make hands the shell a
recipe line and its backslash continuations as one command (GNU make,
"Splitting Recipe Lines"), so the reader took a physical line for a statement
its format continues - the fact `PL-JCS3` found six readers misreading. The
reading above, that no second spelling disagrees, still holds; it tested a
different fact.

**Worked 2026-10-04, slice 2 of `PL-R417` (`#1338`).** Re-confirmed on
`73673e1e`: still true as written. `_make_lines` is now the one reading of a
Makefile's logical lines, as GNU make 4.3 was run to read them: a recipe line
keeps each backslash-newline and loses each continuation's leading tab, and any
other line is joined into one, a comment included. `_recipe_commands` yields
the command make hands the shell, so gate parity reads its script and mode whole
and the coverage gate compares it whole. The coverage gate keeps `PL-D3M2`'s
strict rule rather than gaining a normalization: the two files split a
continued run alike or not at all. Pinned by
`test_recipe_commands_join_a_backslash_continuation` and the `recipe commands,`,
`coverage gate,` and `gate parity,` cases of `PL-R417`'s guard.
