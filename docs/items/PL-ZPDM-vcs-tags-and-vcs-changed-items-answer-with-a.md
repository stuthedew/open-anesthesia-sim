---
id: PL-ZPDM
title: vcs.tags and vcs.changed_items answer with a bare frozenset, so a git that does not answer is indistinguishable from a repository with no tags and a branch that changed nothing
status: untriaged
feature: git-silence-channel
added: 2026-09-19
---

**Problem.** vcs.tags and vcs.changed_items answer with a bare frozenset, so a git that does not answer is indistinguishable from a repository with no tags and a branch that changed nothing

**Found building `PL-Q9Z1`'s failure channel, 2026-09-19, and narrowed the same
day.** Every other public read in `subprojects/docket/src/docket/vcs.py` now
wraps its runner in `_Silences` and reports an unanswered call as `declined`.
These two cannot: `frozenset()` is the whole answer, and it is what a silence
and an empty repository both produce.

`subprojects/docket/tests/test_vcs_silence.py` holds them by asserting the
breach - each still loses a finding to a silence, and says nothing - so the gap
is a running test rather than a marker excusing one, and it fails the day this
closes.

**`default_base` was in this item's first title and is not this item.**
`PL-73P0` had already been filed for it by `PL-BHVM`'s own session, with the
wider case: the base is the one input whose wrongness cannot be seen in any
answer downstream of it, because every downstream answer is *about* that base.
That is a stronger argument than this one and it keeps the read.

**Done when** a caller can tell "no tags" from "git would not say", and
`test_vcs_silence.py` moves the two out of `GAPS` and into `SWEPT`.
