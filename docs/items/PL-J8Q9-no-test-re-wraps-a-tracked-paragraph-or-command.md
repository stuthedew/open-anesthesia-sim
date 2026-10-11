---
id: PL-J8Q9
title: No test re-wraps a tracked paragraph or command and holds every check's answer unchanged, the metamorphic form of PL-R417's misread
priority: P3
effort: M
status: ready
classes: test
feature: reader-checks
touches: tests/unit/test_doc_check.py
added: 2026-10-10
payoff: A reader that misreads a re-wrapped paragraph or re-split command fails a pull request instead of waiting for a sweep to find it, or the measured yield shows the test is not worth its code
verify: grep -q 'def test_rewrapping_a_tracked_statement_changes_no_checks_answer' tests/unit/test_doc_check.py
---

**Problem.** `PL-R417`'s misread is that a statement a format continues
across lines is read by its first physical line. Nothing tests the property
directly: re-wrapping a tracked paragraph, or re-splitting a shell or Makefile
command between words with backslash-newlines, should change no check's
answer. A metamorphic test of that kind needs no reference implementation.
The review left its yield unmeasured, and proposed keeping it only if at least
5 of link 23's twenty-one latent forms, written into a scratch copy of the
tree, make it fail.

**Found 2026-10-10** by the parsing review in `PL-R417`'s closing sweep thread
(link 23). The owner chose to have `PL-R417`'s last batch add the review's two
differential tests in CI, and this follow-up to be filed as an ordinary item.

**Reproduced 2026-10-11** on main at `16a20a4f`: no test re-wraps tracked text
and compares a check's answers. Searching `tests/unit/` and
`subprojects/docket/tests/` for `metamorphic` or `rewrap` finds only a
docstring in `test_doc_check.py` and `pr_body_check`'s case for a body GitHub
re-wrapped, neither of which re-wraps a tracked file. `PL-R417`'s guard,
`CONTINUED_STATEMENTS`, holds each reader to hand-written continuation forms,
not to the tree re-wrapped.

**Why it matters.** `PL-R417` closed spent on the ground that further members
are found only by sweeping for forms no tracked file holds. A metamorphic test
is that sweep run on every pull request with no reference implementation to
maintain, so a reader that misreads a re-wrapped statement fails CI instead of
waiting for the next sweep. Whether it catches enough to earn its code is the
measurement the problem names, and the item is closed either way.

**Generator check.** Not a member of `PL-R417`: a guard that would make its
members fail loudly, not a reader that misreads where a statement ends.

**Done when.** A test re-wraps tracked paragraphs and re-splits commands, and
holds every check's answer unchanged, or the yield measured as above says it
is not worth its code.
