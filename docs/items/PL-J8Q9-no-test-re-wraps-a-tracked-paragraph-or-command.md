---
id: PL-J8Q9
title: No test re-wraps a tracked paragraph or command and holds every check's answer unchanged, the metamorphic form of PL-R417's misread
status: untriaged
feature: reader-checks
added: 2026-10-10
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

**Generator check.** Not a member of `PL-R417`: a guard that would make its
members fail loudly, not a reader that misreads where a statement ends.

**Done when.** A test re-wraps tracked paragraphs and re-splits commands, and
holds every check's answer unchanged, or the yield measured as above says it
is not worth its code.
