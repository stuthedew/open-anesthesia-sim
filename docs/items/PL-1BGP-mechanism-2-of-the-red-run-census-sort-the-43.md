---
id: PL-1BGP
title: Mechanism 2 of the red-run census: sort the 43 store-rule red runs (32 scoped verify replay, 11 docket check) by whether the offending item was the branch's own, whether the branch's diff reached its touches, and whether main already held its work at run time, then reopen PL-85NT for main's share or record why not - the question and method are in PL-PLSJ
priority: P2
effort: S
status: done
classes: infra
feature: fewer-red-runs
milestone: v0.5.17
touches: docs/items
added: 2026-09-27
closed: 2026-09-27
pr: 1216
not-delegable: an analysis of CI logs and git history whose evidence is the table in the brief; nothing in the tree can re-derive it
---

**Problem.** `PL-PLSJ`'s census found 43 pull-request runs that were red on a
store rule: 32 on the scoped verify replay and 11 on `docket check`. Whether
they were caused by `main` or by the branch was inferred, not checked. The
answer decides whether `PL-85NT` (repository-level breakage visible to every
session, claimed by none) is reopened.

**Why it matters.** Breakage caused by `main` needs an owner outside any one
branch, which is what `PL-85NT` was about. Breakage caused by the branch is
mechanism 1 again, and belongs to the push guard.

**Done when.** Each run is sorted by the three questions in `PL-PLSJ`, and
`PL-85NT` is reopened for `main`'s share, or this item records why not.

**Sorted 2026-09-27** by a subagent. It read each job's log, fetched each
run's head, and took `main` at run time as the first-parent tip before the run
started. It evaluated every `verify:` clause it could run read-only against
`main` alone and against the merge. Re-merging each available head reproduced
CI's verdict on all 37 item evaluations.

| Split | Branch | `main` | Unclear |
|---|---|---|---|
| All 43 | 40 | 2 | 1 |
| Before 2026-09-23 (35) | 32 | 2 | 1 |
| From 2026-09-23 (8) | 8 | 0 | 0 |
| Scoped verify replay (32) | 31 | 0 | 1 |
| `docket check` (9) | 7 | 2 | 0 |
| `docket check --verify` (2) | 2 | 0 | 0 |

The 34 verify-rule failures, by cause:

- **12 runs.** The branch added an item whose `verify:` already passed.
- **8 runs.** The item was on `main` with no `verify:`, and the branch wrote a
  passing one, `verify: true` twice among them.
- **10 runs.** The branch did an item's work and left the item open. Two of
  these completed members of the generator head `PL-PVW2`, whose `verify:`
  bundles its members' tests.
- **3 runs.** A mix of the three causes above.
- **1 run, unclear.** `PL-N092` was `blocked` on `main`, and the branch's edit
  unblocked it.

No run had a `verify:` that passed on `main` alone with the item open.

The two runs caused by `main` both failed on `PL-YTDN`, closed on `main` with
no recoverable `pr`, and both fell on 2026-09-19. Two more runs, on the
`PL-HMZZ` branch, read `main`'s copies but raised an error that only that
branch's `checks.py` held. Read literally, the totals are 38, 4 and 1. That
changes nothing below.

Seven branch heads no longer exist. For those runs, "own" came from the pull
request's title and "reached" from its squash commit; the `main` side was
checked directly. `main`'s history before about 2026-09-08 was rewritten with
its trees kept, so those runs were matched by tree. The per-run file was
session scratch and is not kept.

**Decided 2026-09-27: `PL-85NT` is not reopened.** `main`'s share is 2 runs,
or 4 on the literal reading. They have one cause: a closure landing without
its `pr`. `tools/pr_record_check.py` (`PL-HMZZ`) has refused that before merge
since 2026-09-26, and none of the 8 runs from 2026-09-23 on was `main`'s.

**The rest is mechanism 1.** `make check` runs
`bin/docket check --verify --verify-base origin/main`, which refuses all 40
branch-caused runs locally, so each was pushed without it. That check took
6.7 s here, against `doc_check`'s 10.5 s. Run in parallel inside the push
guard, it would add no wait to a push.

The cost is a false refusal. The store check reads `origin/main`, so on the
day `main` itself was wrong it would have refused pushes the branch could not
fix: 2 runs in this census, none since 2026-09-23. Whether to add it is
`PL-S1BG`'s question, recommended yes.
