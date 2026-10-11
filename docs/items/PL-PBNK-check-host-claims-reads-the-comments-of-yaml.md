---
id: PL-PBNK
title: check_host_claims reads the comments of YAML, TOML and Makefiles, where none of its 31 claims sits, so retiring that reach removes most of PL-W9VC's forms
priority: P3
effort: S
status: ready
classes: refactor
feature: reader-checks
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
payoff: the host-claim check stops reading YAML, TOML and Makefile comments, where none of its claims sits, which removes most of PL-W9VC's misreads instead of needing a comment-preserving reader for each format
verify: grep -q 'def test_a_yaml_toml_or_makefile_comment_is_not_read_for_host_claims' tests/unit/test_doc_check.py
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

**Re-confirmed 2026-10-11** on main at `16a20a4f`, under python3 3.13.16: with
`ISO_DATE_RE` stubbed to match nothing, `_host_claim_texts` and
`_undated_host_claims` over the tree find 31 sentences naming a host beside a
refusal - 20 in Markdown, 6 in Python, 3 in shell comments, 2 in JSON strings
and none in a `.yml`, `.yaml`, `.cff`, `.toml` or Makefile comment.

**Why it matters.** Reading a format's comments a physical line at a time is
what `PL-W9VC` misreads, and doing it properly means a comment-preserving
reader for each of YAML, TOML and make, since PyYAML and `tomllib` discard
comments. That is three readers kept for a reach that has never held a claim,
so retiring it is the cheaper sufficient answer and leaves `PL-W9VC` only its
shell forms. The count is the number that would change the answer: one real
claim in those formats and the reach earns its keep.

**Generator check.** Not a member of `PL-R417`: a guard that would make its
members fail loudly, not a reader that misreads where a statement ends.

**Done when.** `check_host_claims` reads no YAML, TOML or Makefile comment,
or one real claim is found there first, which would answer this item the other
way.
