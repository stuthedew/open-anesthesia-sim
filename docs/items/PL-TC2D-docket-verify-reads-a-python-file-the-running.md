---
id: PL-TC2D
title: docket verify reads a Python file the running interpreter cannot parse one physical line at a time for both integrity checks, so a docstring line opening assert is charged as a removed assertion and a deleted assertion folds against a matching docstring line; the fallback is PL-4W2L's ratified choice
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests
added: 2026-10-04
recurrences: 2026-10-04 PL-MR8Z withdrawn 2026-10-04 PL-R417
---

**Problem.** docket verify reads a Python file the running interpreter cannot parse one physical line at a time for both integrity checks, so a docstring line opening assert is charged as a removed assertion and a deleted assertion folds against a matching docstring line; the fallback is PL-4W2L's ratified choice

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

Python Language Reference § 2.1. `bin/docket` runs the bare `python3`, 3.11 here and in CI's bare-checkout job, and two tracked files are syntax 3.11 cannot parse: `src/anesthesia_sim/app_metadata.py`:92 (PEP 758) and `src/anesthesia_sim/app/bookmarks.py`:451 (PEP 695). A file like that is read with `is_assertion_line` and named on the page, which `PL-4W2L` § "Decision: the assertion check" chose (project owner, 2026-09-22, ratified, over (ii) and (iii)) on the count "32 of the commits read at least one file line by line, and none of them changed the verdict". `PL-CFWP` (`#1353`) gave the suppression check the same fallback, to keep the two integrity checks alike.

- With `def first[T](x: T)` above it, a commit loosening `assert (` / `result == 2` / `)` and rewording a docstring line that opens `assert` FAILs on the docstring line and misses the loosened assertion.
- Deleting `    assert x == 1` and adding the same text as a docstring line PASSes, the fold cancelling the statement against a string's fragment.
- Live in waiting: `app_metadata.py`:106 is a docstring line of `build_identifier` opening `assert`, in a file 3.11 cannot parse, so an edit to that docstring would FAIL.

The page names the file and the parse error, not the continued form, and the fold case is a cost the ratified count did not carry, which is ordinary evidence to reopen it.

**Decision for the project owner: keep the line fallback, or read such a file's logical lines through `tokenize` first. Recommended: `tokenize` first.** Every syntax 3.11 cannot parse here adds grammar rather than tokens, so 3.11's `tokenize` reads both files whole (checked: 34 and 170 logical lines, and `app_metadata.py`'s docstring line is one string token), a docstring is never code and a bracketed `assert` is one statement, which settles all three cases above; a file the tokenizer itself refuses is still read line by line and named. What it costs: a 3.12 f-string nesting its own quote mis-tokenizes on 3.11 without an error (PEP 701), so a blanked span can differ from the real one in such a line - the fallback's own failure moved, not removed - which is why the page should keep naming the file either way.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
