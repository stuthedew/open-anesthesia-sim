---
id: PL-QP9Z
title: The empty start claim rides a captures-only first push, so auto-merge lands the capture within minutes, deletes the branch, and erases the claim while the work goes on
priority: P2
effort: S
status: done
classes: defect
touches: CLAUDE.md
added: 2026-09-23
closed: 2026-09-23
payoff: a session that files its own item and claims it keeps its claim on a pushed branch while it works, instead of every in-flight guard reading the item as free for the minutes after its capture auto-merges
verify: grep -q "A start claim riding that push" CLAUDE.md
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

**Decided 2026-09-23: yes** (project owner, 2026-09-23, ratified, over arming
auto-merge whatever rode the first push). `CLAUDE.md`'s commit-and-push bullet
now says a start claim riding a captures-only branch's first push leaves its
pull request unarmed, and that the first push carrying anything else - a start
claim included - disarms auto-merge. A branch whose captures were pushed and
armed before the session picked an item up is the second case: the claim push
carries no file, so it would not otherwise have read as "anything else". The
pull request still opens at the first push, which meets `PL-WNCT`'s done-when.

Resident cost: 201 characters net, after `which cost 21 recovery items` was
cut from `PL-WNCT`'s parenthetical to pay for part of it, since that count is in
`PL-WNCT`'s own brief. The rest cannot move: the arming rule is stated only in
this bullet, and the exception has to be read at the same push. Built under the
new-mechanism pause as a defect in a rule that exists, and at the owner's
request, which lifts the pause for it (`PL-6Q9L`).
