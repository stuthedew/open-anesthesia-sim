---
id: PL-CFWP
title: docket's verify.is_suppression_line reads one diff line at a time, so a pytest.mark.skip split by a backslash or a bracket continuation is not counted as an added suppression; latent
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: a test-disabling marker split across lines is reported as an added suppression, so the check's none holds whatever the layout
verify: grep -qF '"suppressions, ' tests/unit/test_doc_check.py
---

**Problem.** docket's verify.is_suppression_line reads one diff line at a time, so a pytest.mark.skip split by a backslash or a bracket continuation is not counted as an added suppression; latent

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. `@pytest.mark.\` over `    skip(reason='flaky')`, and `@(pytest.mark` over `  .skip(...))`, both valid to `ast.parse`, read [False, False]; one line reads True, so the audit prints "no suppression added: none". `is_assertion_line`'s docstring names its continuation misses; this one's does not. Latent.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, `is_suppression_line` reads `@pytest.mark.\` over `    skip(reason='flaky')`, and `@(pytest.mark` over `  .skip(reason='flaky'))`, as `[False, False]` each, and the same marker on one line as `True`.

**Why it matters.** `no suppression added` is the one check `--self` may never relax, and its `none` is read as a guarantee that no test was disabled. ruff format never splits a dotted name, so neither form comes from formatting and the item stays latent; what it leaves is that guarantee with a hole a hand-written decorator can fall through.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** The check reads each changed Python file's logical lines (Python Language Reference § 2.1, through `tokenize`) before and after each of the item's commits, folded per file as `removed_assertions` folds statements, and matches `SUPPRESSIONS` against the code of each logical line the item added; a file this interpreter cannot parse is read line by line and named, and `suppressions, ...` cases in `CONTINUED_STATEMENTS` pin both splits.
