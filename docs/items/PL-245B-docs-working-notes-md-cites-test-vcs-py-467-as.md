---
id: PL-245B
title: docs/WORKING_NOTES.md cites test_vcs.py:467 as the test asserting _superseded's inverted direction, but that line has never held such a test - PL-Q9Z1's live thread rests on it
status: untriaged
added: 2026-09-19
---

**Problem.** docs/WORKING_NOTES.md cites test_vcs.py:467 as the test asserting _superseded's inverted direction, but that line has never held such a test - PL-Q9Z1's live thread rests on it

**Found in `PL-2BZY`'s close-out sweep, 2026-09-19.** `docs/WORKING_NOTES.md`
line 1838 reads: "`_superseded`'s docstring states the correct direction in
three cases while the code inverts two of them, and `test_vcs.py:467` asserts
the inverted one." The number is the evidence for a claim about which assertion
is wrong, so a reader who follows it and finds an unrelated test cannot tell a
moved line from a claim that was never true.

**It was already wrong when written, not shifted since.** At `e0c1056`, the
commit that added the sentence, `subprojects/docket/tests/test_vcs.py:467` was
`def test_no_git_means_no_claims_about_branches()`; on `origin/main` today it
is `def test_one_blob_the_base_has_never_held_is_not_a_squash_merge()`. Neither
asserts anything about `_superseded`'s direction. So this is not line drift to
be corrected by counting - the test the sentence means has to be found, or the
claim withdrawn.

**Why it matters now.** The paragraph is the standing thread behind `PL-Q9Z1`
(`_superseded` reads a failed `git diff` as the tips agreeing about every
path), which a live session was working on 2026-09-19, and the claim it
supports - that prose demonstrably cannot hold the direction, so the fix must
be a fault-injection test - is the argument for that item's shape. `PL-2BZY`'s
own change to `test_vcs.py` moves the line three further, which is what
surfaced it; nothing about the defect is `PL-2BZY`'s.

**Where.** `docs/WORKING_NOTES.md:1838`, and `_superseded` in
`subprojects/docket/src/docket/vcs.py`.

**Done when.** The sentence names the assertion it means by test function name
rather than by line number - the form `tools/doc_check.py` can check and a
rename cannot silently break - or says plainly that the inverted case has no
test, whichever the code turns out to support.
