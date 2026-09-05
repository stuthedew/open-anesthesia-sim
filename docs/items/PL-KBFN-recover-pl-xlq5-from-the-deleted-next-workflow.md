---
id: PL-KBFN
title: Recover PL-XLQ5 from the deleted next-workflow-item-c2b07p branch, whose only surviving copy is a stale origin ref
status: dropped
reason: the premise was false - the branch merged as #325 three minutes before this item's recovery commit, so nothing was ever stranded and the recovery was a duplicate that carried the pre-triage copy
added: 2026-09-05
closed: 2026-09-05
classes: infra
touches: docs/items
verify: git cat-file -e origin/main:docs/items/PL-XLQ5-the-orphaned-report-counts-a-branch-s.md
---

**What this item claimed.** That `PL-XLQ5` (the orphaned report counts a
branch's superseded intermediate blob as work the squash left behind) survived
only on this checkout's stale `origin/claude/next-workflow-item-c2b07p` ref,
because `bin/docket stranded` named that branch and `git ls-remote origin` no
longer listed it — `PL-HKF4`'s scenario, one prune from permanent loss.

**Why that was wrong.** A branch deleted from the remote has *two* possible
histories, and only one of them is a hole: nobody merged it, or it merged and
the merge deleted it. This was the second. `claude/next-workflow-item-c2b07p`
merged as **#325** at 2026-09-05 01:13:48 UTC, landing `PL-XLQ5` and the three
`pr:` records on `main`; this item's recovery commit is 01:16:47 UTC, three
minutes later. The absent remote ref was the merge's own cleanup, read as loss.

`bin/docket stranded` was right against the ref it held and stale by two
minutes: this checkout's `origin/main` was fetched at 01:05, before #325
merged. The check that would have settled it in one command was never run —
fetch `main`, then ask whether the item is on it. `PL-39B7` (make `docket
stranded` distinguish a merged-and-deleted branch from an abandoned one) is
that gap.

**What it cost, and what it did not.** Nothing landed, because the branch
carrying it was never merged. Two duplications inside this branch, both now
resolved:

- The recovered `PL-XLQ5` was the **pre-triage** copy — `status: untriaged`,
  with no `priority`, `effort`, `classes`, `feature`, `touches` or `verify` —
  while #325 landed the triaged one. Merging this branch without noticing would
  have silently reverted that item's triage. The `origin/main` merge on this
  branch resolves the add/add conflict in `main`'s favour.
- `bin/docket record`'s three `pr:` writes (322, 323, 324) duplicated #325's,
  byte-identical, so they merge as the same change and cost nothing.

**Kept rather than deleted** because the misreading is the useful part: the
inference "the remote branch is gone, therefore its work is lost" is wrong
half the time, and `PL-39B7` exists to make a command answer it instead of a
session guessing.
