---
id: PL-KS01
title: The session-start digest, list, status and concurrent answer from the working tree's copy of each item while next and show read origin/main's newer copy, so behind origin/main the digest's Top line can name an item next no longer offers
status: untriaged
feature: one-snapshot
added: 2026-09-26
---

**Problem.** The session-start digest, list, status and concurrent answer from the working tree's copy of each item while next and show read origin/main's newer copy, so behind origin/main the digest's Top line can name an item next no longer offers

**Why it matters.** Found closing `PL-Y48N`, which scoped the base's newer copy to `next`, `show` and `claim` (`cli._from_base`, `vcs.base_copies`). The digest's `Top:` and `By lane` lines are `next`'s pick, so a resumed session behind `origin/main` can be pointed at an item `next` would no longer offer. Low harm as it stands: the hook's branch line above the digest already says the branch is behind, and `show` and `claim` now catch a closed item downstream. `cli._from_base` is read-only by construction; applying it to the digest would also move the open counts and the releasable count, which is the decision this item holds.
