---
id: PL-MQH0
title: Apply feature: session-start-cost to PL-JH3T, PL-XD3C, PL-0J9K, PL-MMVF and PL-RC86 once claude/confident-gauss-r3rg8i merges, which is the backfill PL-N638 could not land without five add/add conflicts
status: untriaged
feature: session-start-cost
added: 2026-09-16
---

**Problem.** Apply feature: session-start-cost to PL-JH3T, PL-XD3C, PL-0J9K, PL-MMVF and PL-RC86 once claude/confident-gauss-r3rg8i merges, which is the backfill PL-N638 could not land without five add/add conflicts

**Why it exists.** `PL-N638` made a diagnosis's items carry one `feature:` and
demonstrated it on the five that prompted the change. The demonstration could
not land with it: those five item files exist on
`claude/confident-gauss-r3rg8i` and on `PL-N638`'s branch with no common
ancestor, so `git merge-tree` reports add/add conflicts on every one.

**Do it after that branch merges**, when the files are on `main` and the edit
is one line each with nothing to conflict with.

**The members**, and why the name is `session-start-cost` rather than
`digest-cost`: `PL-RC86` is the session-start hook's three serial network round
trips and `PL-JH3T` is the whole hook's wall clock, so naming the group for
`digest` would exclude two of its own members - the failure `PL-N638` is about.

- `PL-JH3T` - attribute the hook's 20.7 s median to a stage
- `PL-XD3C` - profile `digest` itself
- `PL-0J9K` - one `git cat-file --batch` for the per-blob `git show` fan-out
- `PL-MMVF` - memoize the runner; 82 of 192 subprocesses are exact duplicates
- `PL-RC86` - the three serial network round trips

`PL-DMDF` was filed on that branch from the same diagnosis (the diff fan-out);
check whether it belongs in the group when doing this. `PL-7XNX` deliberately
does not - its own brief calls it a nought-to-four-call ride-along.

**Done when.** Each of the five carries `feature: session-start-cost`, and
`bin/docket feature session-start-cost` prints a count over five.

