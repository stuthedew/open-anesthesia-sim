---
id: PL-PNGQ
title: str.isdigit() accepts superscript and other Unicode digits that int() then refuses with ValueError, and about 15 apparatus sites read a whole number as isdigit() then int() (arming.py behind and count, vcs.py counts, doc_check's stated count): one reader of an ASCII whole number would read them alike (found building PL-N4FP)
priority: P3
effort: M
status: ready
classes: defect
feature: one-source-of-truth
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/, tools/, subprojects/docket/tests/, tests/unit/
added: 2026-10-24
payoff: a count read from git or GitHub is parsed by one function that refuses a non-ASCII digit, instead of fifteen hand copies that crash on one
verify: grep -rqE 'def test_[a-z_]*superscript' subprojects/docket/tests tests/unit
reenters: PL-N4FP
---

**Problem.** str.isdigit() accepts superscript and other Unicode digits that int() then refuses with ValueError, and about 15 apparatus sites read a whole number as isdigit() then int() (arming.py behind and count, vcs.py counts, doc_check's stated count): one reader of an ASCII whole number would read them alike (found building PL-N4FP)

**Why it matters.** `isdigit()` returns `True` for `'²'`, and then `int('²')` raises `ValueError`. Where a site reads a count with `isdigit()` and then `int()`, a stray Unicode digit crashes the command instead of being treated as "not a number". The realistic inputs are git output and GitHub API fields, which are ASCII, so a crash is unlikely. The larger cost is that about 15 sites each spell the same reading by hand. That breaks `CLAUDE.md`'s one-source-of-truth rule, and so this item is classed `defect`.

**Reproduced 2026-10-24.** `python3 -c "print('²'.isdigit()); int('²')"` prints `True` and then raises `ValueError: invalid literal for int() with base 10: '²'`. `grep -rn "isdigit()" subprojects/docket/src tools .claude` finds 17 lines.

**Done when.** One function reads an ASCII whole number. It returns the number, or a refusal, for any string. Each `isdigit()`-then-`int()` site under `subprojects/docket/src/docket/` and `tools/` calls it, and a test pins that a superscript digit is refused rather than raised. Whether `tools/fact_home_check.py` should refuse the next hand copy is decided while working the item.

**Generator check.** The fact that was misread is which spelling of a repeated predicate is the answer. `PL-N4FP` states that fact in its `misread:` and closed on 2026-10-24, and this item was found while building it. So this is an instance of a head's fact filed at the head's close, and it is recorded as `reenters: PL-N4FP`.
