---
id: PL-CFWP
title: docket's verify.is_suppression_line reads one diff line at a time, so a pytest.mark.skip split by a backslash or a bracket continuation is not counted as an added suppression; latent
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-04
pr: 1353
payoff: a test-disabling marker split across lines is reported as an added suppression, so the check's none holds whatever the layout
verify: grep -qF '"suppressions, ' tests/unit/test_doc_check.py
---

**Problem.** docket's verify.is_suppression_line reads one diff line at a time, so a pytest.mark.skip split by a backslash or a bracket continuation is not counted as an added suppression; latent

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. `@pytest.mark.\` over `    skip(reason='flaky')`, and `@(pytest.mark` over `  .skip(...))`, both valid to `ast.parse`, read [False, False]; one line reads True, so the audit prints "no suppression added: none". `is_assertion_line`'s docstring names its continuation misses; this one's does not. Latent.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, `is_suppression_line` reads `@pytest.mark.\` over `    skip(reason='flaky')`, and `@(pytest.mark` over `  .skip(reason='flaky'))`, as `[False, False]` each, and the same marker on one line as `True`.

**Why it matters.** `no suppression added` is the one check `--self` may never relax, and its `none` is read as a guarantee that no test was disabled. ruff format never splits a dotted name, so neither form comes from formatting and the item stays latent; what it leaves is that guarantee with a hole a hand-written decorator can fall through.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** The check reads each changed Python file's logical lines (Python Language Reference § 2.1, through `tokenize`) before and after each of the item's commits, folded per file as `removed_assertions` folds statements, and matches `SUPPRESSIONS` against the code of each logical line the item added; a file this interpreter cannot parse is read line by line and named, and `suppressions, ...` cases in `CONTINUED_STATEMENTS` pin both splits.

**Built 2026-10-04 (`#1353`).** The suppression check reads each changed
Python file's logical lines through `read_logical_lines`, which runs `tokenize`
and blanks strings, comments and f- and t-string bodies, so a mark split by a
backslash or inside brackets is one statement and a mark inside a string is
none. `added_suppressions` compares the logical lines before and after, folded
per file by their tokens, so reflowing or re-commenting a mark already there
adds nothing. A file the running interpreter cannot tokenize is read a line at
a time, as before, and the check names it (`SuppressionAudit`). Replayed under
3.11 over `main`'s 680 non-merge commits that change a `.py` or `.pyi` file,
the statement reader finds exactly what the line reader found, `#300`'s `bash`
guard; 32 of those commits name a file 3.11 cannot parse. Four guard cases,
`suppressions, ...`, the two splits failing on main's reader, and three docket
tests. The line fallback's own misreads are `PL-TC2D`.
