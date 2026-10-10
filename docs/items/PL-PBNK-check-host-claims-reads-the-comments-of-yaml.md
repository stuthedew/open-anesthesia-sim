---
id: PL-PBNK
title: check_host_claims reads the comments of YAML, TOML and Makefiles, where none of its 31 claims sits, so retiring that reach removes most of PL-W9VC's forms
status: untriaged
feature: reader-checks
added: 2026-10-10
---

**Problem.** `check_host_claims` reads the comments of YAML, TOML and
Makefiles as well as Markdown, Python, JSON strings and shell, and fails on an
undated claim. Of its 31 claims, 20 are in Markdown, 6 in Python, 3 in shell, 2
in JSON and none in YAML, TOML or Makefile comments, by the review's count. The
reach into those three formats is most of what `PL-W9VC` misreads, and no
library hands it that input, since PyYAML and `tomllib` discard comments.

**Found 2026-10-10** by the parsing review in `PL-R417`'s closing sweep thread
(link 23). The owner chose to have `PL-R417`'s last batch add the review's two
differential tests in CI, and this follow-up to be filed as an ordinary item.

**Generator check.** Not a member of `PL-R417`: a guard that would make its
members fail loudly, not a reader that misreads where a statement ends.

**Done when.** `check_host_claims` reads no YAML, TOML or Makefile comment,
or one real claim is found there first, which would answer this item the other
way.
