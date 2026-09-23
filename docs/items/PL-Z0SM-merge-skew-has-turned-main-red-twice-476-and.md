---
id: PL-Z0SM
title: Merge skew has turned main red twice - #476 and #477 (PL-33WM), then #930 and #933 on 2026-09-23 - because parallel sessions merge minutes apart on pull requests whose CI ran on a base without the other, so no pull request ever shows the red
status: untriaged
added: 2026-09-23
---

**Problem.** Merge skew has turned main red twice - #476 and #477 (PL-33WM), then #930 and #933 on 2026-09-23 - because parallel sessions merge minutes apart on pull requests whose CI ran on a base without the other, so no pull request ever shows the red

**Found 2026-09-23 while diagnosing `PL-KH3Q`.** The first instance is
`PL-33WM` (#476 added a presence check on a base #477's CI never saw); the
second is `PL-KH3Q` (#930 and #933, nine minutes apart). Two in about 460
pull requests, both while several sessions were merging within the hour.
The remedies this class has - a merge queue, or requiring a branch to be up to
date before it merges - are new workflow mechanisms, so the `PL-6Q9L` pause
holds them, and any of them has to answer `PL-J786` (dropped: a green `checks`
run before any merge) and `PL-WC72` (CI cost of re-running on every base move).
Captured for the count, not proposed: what would change the answer is the
instance rate once the pause lifts.
