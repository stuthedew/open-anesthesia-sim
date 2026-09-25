---
id: PL-PNJF
title: pr_body_check.py --compare reports 27 squash bodies that say something other than their pull request, and nothing can record the pull request's body for them: --recover writes only for an empty body, and a recovery file's header says the commit landed empty
status: untriaged
feature: pr-body-integrity
touches: tools/pr_body_check.py, tests/unit/test_pr_body_check.py, docs/pr-bodies
added: 2026-09-24
---

**Problem.** pr_body_check.py --compare reports 27 squash bodies that say something other than their pull request, and nothing can record the pull request's body for them: --recover writes only for an empty body, and a recovery file's header says the commit landed empty

**Found by `PL-Y1W0`, 2026-09-24.** `--compare` names the 27, and they stay
reported: `recovered()` counts only a `docs/pr-bodies/<N>.md` file, and
`recover()` writes one only for a commit `missing()` returns, which is an
empty body. So the only way to clear one is by hand, with a file whose header
(`write_recovery`) says the squash "landed with an empty message body", which
is untrue for all 27.

Which body is the record is not the same question for every shape. For six,
the pull request was edited after auto-merge was armed, so its body is the
later reasoning. For `#466` and `#522`, the body carries a note added after
the merge, and the squash is what was true at merge time. For shapes like
`#744`, the merge sent a short message of its own. That is why this is an item
and not a flag on `--recover`. `PL-73G8` is already changing the header's
provenance claim in the same function, so land that first or decide the two
together.
