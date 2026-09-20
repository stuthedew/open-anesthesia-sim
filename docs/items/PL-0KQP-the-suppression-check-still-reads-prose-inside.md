---
id: PL-0KQP
title: The suppression check still reads prose inside a .py file as code, so a comment, a docstring or a test fixture naming xfail REJECTs - which is why this fix's own regression test cannot be audited clean
status: dropped
added: 2026-09-20
closed: 2026-09-20
reason: Duplicate of PL-STC4's remaining half, captured on #783's branch before its author found PL-STC4 or PL-4FD2 - itself a fourth instance of PL-TZ7T (bin/docket new files a duplicate title without noticing). Its unique evidence is folded into PL-STC4: the 6-line measurement from #783's own branch, and that a file-level '# type: ignore' on its own line is a real whole-file mypy directive, so 'the line is a comment' cannot be the predicate.
---

**Problem.** The suppression check still reads prose inside a .py file as code, so a comment, a docstring or a test fixture naming xfail REJECTs - which is why this fix's own regression test cannot be audited clean

**Found 2026-09-20 closing `PL-5MFL` and `PL-BHBZ`**, which narrowed the same
check by *file suffix*. That removed the whole of the prose problem outside
code and none of it inside: `is_suppression_line` now asks whether the file
could carry a suppression, and every line of a `.py` file can.

**What is left.** A suppression token in a `.py` file suppresses nothing when
it sits in a comment, a docstring, or a string literal. The three shapes this
tree actually produces:

- a docstring or comment in `subprojects/docket/src/docket/verify.py` naming
  the tokens it matches, which is unavoidable in the file that defines them;
- a test fixture in `subprojects/docket/tests/test_verify.py` that must write
  a literal suppression into a scratch repository to test the check at all;
- an ordinary code comment anywhere explaining why a suppression was removed.

**Why it is separate from `PL-5MFL`.** `PL-BHBZ`'s own "Done when" requires
that "a `.py` line containing one still fails", so narrowing *within* `.py`
was ruled out by the commission rather than overlooked. It is also a harder
problem: `# type: ignore` on a line of its own at the top of a file is a real
file-wide mypy directive, so "the line is a comment" is not the predicate -
which means this needs a position test (is the token inside a string literal?)
rather than a line test, and `verify.py`'s own `TOKEN_RE` comment warns against
a second idea of Python's grammar growing in that file.

**Why it matters.** It is the same compounding-friction shape the suffix
narrowing just fixed, on the same check `--self` may never relax - a `REJECT`
on correct work trains a reader to skim the block where a real weakening is
printed (`PL-69JZ`, `PL-7XTS`). It is narrower now: it fires only on work that
writes *about* suppressions in code, which is essentially work on this check.
Measured on the branch that closed `PL-5MFL` and `PL-BHBZ`, which is the
REJECT that branch reported rather than an estimate: **6** added `.py` lines,
none of them a suppression - two docstring lines naming `xfail_strict` to
explain the suffix list, three test fixture strings that must write a literal
suppression into a scratch repository, and one assertion pinning the tuple the
check reports.

**Done when.** A decision is recorded on whether the position test is worth
its cost - and if it is, an added `.py` line whose suppression token sits
inside a string literal, a docstring or a comment that is not a file-level
directive is not reported, while a real directive still is.
