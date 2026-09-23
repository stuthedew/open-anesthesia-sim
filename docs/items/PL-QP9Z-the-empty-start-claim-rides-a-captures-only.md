---
id: PL-QP9Z
title: The empty start claim rides a captures-only first push, so auto-merge lands the capture within minutes, deletes the branch, and erases the claim while the work goes on
status: untriaged
touches: CLAUDE.md
added: 2026-09-23
---

**Problem.** The empty start claim rides a captures-only first push, so auto-merge lands the capture within minutes, deletes the branch, and erases the claim while the work goes on

**Observed 2026-09-23, on the v0.5.7 cut (`PL-KNWP`).** `CLAUDE.md`'s rule
that housekeeping is filed before it is done, the start mode's empty claim
commit, and `PL-WNCT`'s rule that a branch carrying only item files opens its
pull request at its first push and arms auto-merge all fired on one push. The
capture commit and the empty `PL-KNWP: start` commit went up together, and
the branch's diff was item files only, so `#942` opened with auto-merge armed
at 02:06:34Z. It merged at 02:10:28Z, while the cut was still being written.
GitHub deleted the head branch at the merge, and the squash folded the empty
claim into a capture commit, which no guard reads as a claim (`PL-X3WZ`). From
02:10 until the cut was pushed at about 02:19, no pushed ref claimed
`PL-KNWP`, and `bin/docket flight` and `bin/docket show` would have read a
`ready` item that nobody held, while a session was working on it. The work
then needed a branch restart, a lease push refused as `stale info` against
the deleted ref, and a second pull request (`#946`).

This happens to every session that files its own item and starts it straight
away, which the housekeeping rule prescribes whenever the work has no item
yet. The wrong answer is silent: the guards report an item as free while it
is taken.

**Decision needed.** Should a first push that carries the empty start claim
still arm auto-merge? `PL-WNCT`'s rule (project owner, 2026-09-23, ratified)
does not distinguish that case, so ordinary evidence reopens it, and this is
that evidence.

**Recommended: open the pull request at the first push as now, but arm
auto-merge only when no start claim rides it.** `PL-WNCT`'s done-when is that
a capture from a session that ends "reaches `main` or an open pull request
without a later session filing an item to recover it". An open pull request
without auto-merge meets that, and keeps the branch and its claim alive. The
change is one clause in `CLAUDE.md`'s commit-and-push bullet. The cost is that
a session which claims and then dies leaves an open pull request to be merged
by hand, which is the state `PL-WNCT` accepted as done.
