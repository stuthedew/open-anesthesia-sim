---
id: PL-TC2D
title: docket verify reads a Python file the running interpreter cannot parse one physical line at a time for both integrity checks, so a docstring line opening assert is charged as a removed assertion and a deleted assertion folds against a matching docstring line; the fallback is PL-4W2L's ratified choice
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/python.py, subprojects/docket/tests, subprojects/docket/README.md, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-R417's Python slice, 2026-10-05
added: 2026-10-04
closed: 2026-10-05
pr: 1374
payoff: an assertion deleted or loosened in a file the bare interpreter cannot parse is charged, and a reworded docstring there is not, so both integrity checks hold on the files docket's python3 cannot parse
verify: grep -qF '"assertions, ' tests/unit/test_doc_check.py && grep -q 'def test_a_file_this_interpreter_cannot_parse_is_read_through_the_tokenizer' subprojects/docket/tests/test_verify.py
recurrences: 2026-10-04 PL-MR8Z withdrawn 2026-10-04 PL-R417
---

**Problem.** docket verify reads a Python file the running interpreter cannot parse one physical line at a time for both integrity checks, so a docstring line opening assert is charged as a removed assertion and a deleted assertion folds against a matching docstring line; the fallback is PL-4W2L's ratified choice

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

Python Language Reference § 2.1. `bin/docket` runs the bare `python3`, 3.11 here and in CI's bare-checkout job, and two tracked files are syntax 3.11 cannot parse: `src/anesthesia_sim/app_metadata.py`:92 (PEP 758) and `src/anesthesia_sim/app/bookmarks.py`:451 (PEP 695). A file like that is read with `is_assertion_line` and named on the page, which `PL-4W2L` § "Decision: the assertion check" chose (project owner, 2026-09-22, ratified, over (ii) and (iii)) on the count "32 of the commits read at least one file line by line, and none of them changed the verdict". `PL-CFWP` (`#1353`) gave the suppression check the same fallback, to keep the two integrity checks alike.

- With `def first[T](x: T)` above it, a commit loosening `assert (` / `result == 2` / `)` and rewording a docstring line that opens `assert` FAILs on the docstring line and misses the loosened assertion.
- Deleting `    assert x == 1` and adding the same text as a docstring line PASSes, the fold cancelling the statement against a string's fragment.
- Live in waiting: `app_metadata.py`:106 is a docstring line of `build_identifier` opening `assert`, in a file 3.11 cannot parse, so an edit to that docstring would FAIL.

The page names the file and the parse error, not the continued form, and the fold case is a cost the ratified count did not carry, which is ordinary evidence to reopen it.

**Decided 2026-10-04: read such a file's logical lines through `tokenize` first** (project owner, 2026-10-04, ratified, over keeping `PL-4W2L`'s line fallback for a file the interpreter cannot parse). The case as it was put: Every syntax 3.11 cannot parse here adds grammar rather than tokens, so 3.11's `tokenize` reads both files whole (checked: 34 and 170 logical lines, and `app_metadata.py`'s docstring line is one string token), a docstring is never code and a bracketed `assert` is one statement, which settles all three cases above; a file the tokenizer itself refuses is still read line by line and named. What it costs: a 3.12 f-string nesting its own quote mis-tokenizes on 3.11 without an error (PEP 701), so a blanked span can differ from the real one in such a line - the fallback's own failure moved, not removed - which is why the page should keep naming the file either way.

**Reproduced 2026-10-05, at triage.** Against `main` at `a8d9b02a`, under 3.14.7, with a tail the parser refuses and the tokenizer reads (`x = = 1`) standing in for newer grammar: the first case FAILs on `1 line(s) in a file read line by line`, charging the docstring line `assert this reads as prose.` and not the loosened `assert (` / `result == 2` / `)`; the second passes with `none`; and `is_assertion_line` reads `app_metadata.py`:106 as an assertion. 3.11.15, 3.12.3, 3.13.14 and 3.14.7 each tokenize `app_metadata.py` and `bookmarks.py` whole, into 34 and 171 logical lines with no error token, where only 3.14 parses the first and only 3.11 fails to parse the second, whose PEP 695 line is now 457.

**Why it matters.** `no existing assertion removed` and `no suppression added` are the checks `--self` may never relax, and on a file the bare interpreter cannot parse the line reading REJECTs correct work on a docstring and ACCEPTs a deleted assertion, a check passing while its guarantee is void. `bin/docket` runs on whatever `python3` is on PATH, so the files it reads that way grow with every newer syntax the project adopts.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** Both checks read a Python file the running interpreter cannot parse through the tokenizer, by docket's one Python reader, and name it on the page as read that way: a docstring is no assertion, a bracketed `assert` is one statement, and a deleted assertion is charged whatever a string gains. A file the tokenizer refuses, an error token included, which 3.11 hands back where 3.12 raises, is still read line by line and named. `CONTINUED_STATEMENTS` gains `assertions, ` cases and a `suppressions, ` case for a file the parser refuses, each failing on today's readers, and `subprojects/docket/tests/test_verify.py` gains `test_a_file_this_interpreter_cannot_parse_is_read_through_the_tokenizer`.
