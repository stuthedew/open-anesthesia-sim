---
id: PL-PXZ3
title: left_behind_check reports a commit whose identical patch already landed through another pull request: its first finding, 52c6d698 on claude/recurrence-signal-feature-3hnynt, matches 98de88c8 in #794 by git patch-id, so the reader had to prove the branch stale by hand
status: untriaged
added: 2026-09-23
---

**Problem.** left_behind_check reports a commit whose identical patch already landed through another pull request: its first finding, 52c6d698 on claude/recurrence-signal-feature-3hnynt, matches 98de88c8 in #794 by git patch-id, so the reader had to prove the branch stale by hand

**Found 2026-09-23** on the session-start digest's first `left-behind:` line.
`git show 52c6d698 | git patch-id --stable` equals the patch-id of `98de88c8`
in `refs/pull/794/head`, and #794 squash-merged as `9fe0ee33` (PL-DGP0,
`pr: 794`). The check's own output already says it cannot tell this case
("if the change landed through another pull request, the branch is stale"),
so this is a precision gap in an existing check rather than a wrong answer:
it could compare a left-behind commit's patch-id against other pull requests'
heads before reporting it. Held as a capture under the `PL-6Q9L` pause unless
it is read as a defect in what exists.
