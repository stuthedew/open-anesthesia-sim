---
id: PL-H14W
title: A claimed captures-only pull request opens at the first push as an ordinary mergeable one titled for the work, so #978 was merged six minutes in while the v0.5.9 cut was being written, erasing the start claim with the branch and leaving a subject on main that names a cut it does not contain
status: untriaged
added: 2026-09-24
---

**Problem.** A claimed captures-only pull request opens at the first push as an ordinary mergeable one titled for the work, so #978 was merged six minutes in while the v0.5.9 cut was being written, erasing the start claim with the branch and leaving a subject on main that names a cut it does not contain

**What happened, 2026-09-24.** The v0.5.9 cut's session filed `PL-R498`, then
pushed its capture and the empty `PL-R498: start` claim together. `CLAUDE.md`'s
commit-and-push bullet says a branch carrying only item files opens its pull
request at that first push and that a claim leaves it unarmed, so `#978` opened
at 00:36:59Z, not a draft, titled "PL-R498: cut v0.5.9 from the 27 items
finished since v0.5.8". It merged at 00:43:14Z under the project owner's
account, with the cut still uncommitted in the session's checkout. The session
armed nothing and no workflow arms auto-merge, so it was merged by hand or
armed from the owner's side. GitHub deleted the branch. The squash folded the
claim into `8428844c`, whose subject names a cut it does not contain, and
`main`'s copy of the item read `ready` with no pushed ref claiming it until
the session re-claimed it at 00:45:51Z on a branch restarted from `main`.

This is `PL-QP9Z`'s outcome through a different merger. `PL-QP9Z`, `PL-1MCK`
and `PL-KWCY` each closed a way auto-merge could land a claimed captures-only
branch, and none of them reaches a person merging an open, green, non-draft
pull request whose title reads as the finished work. Remedies to weigh, none
decided: open such a pull request as a draft while a claim rides it and mark it
ready when the claimed item closes, which GitHub then refuses to merge before;
open none while a claim rides the branch; or title it as the capture it is.
Whether this is a member of the who-holds-an-item head, `PL-MB2W`, whose design
round was running on 2026-09-24, is that round's call.
