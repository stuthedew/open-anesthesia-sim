---
id: PL-MQH0
title: Apply feature: session-start-cost to PL-JH3T, PL-XD3C, PL-0J9K, PL-MMVF and PL-RC86 once claude/confident-gauss-r3rg8i merges, which is the backfill PL-N638 could not land without five add/add conflicts
priority: P2
effort: S
status: done
classes: infra
feature: session-start-cost
milestone: v0.4.26
touches: docs/items/
added: 2026-09-16
closed: 2026-09-16
pr: 637
verify: make docket && bin/docket feature session-start-cost | grep -cE '^  \[.\] PL-(JH3T|XD3C|0J9K|MMVF|RC86|DMDF) ' | grep -qx 6
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

**`PL-DMDF` is in, which makes six.** The brief left that open; the answer is
yes, on the same test the name was chosen by. It was found while working
`PL-XD3C` - one diagnosis, which is the condition `PL-N638` names - and it is
the largest saving left in `digest`: hoisting `_superseded` out of its per-item
comprehension takes the owner's clone from 593 `diff` calls to 148 and its whole
git-call count from 1,237 to 792. Excluding it would reproduce the failure the
group exists to prevent, one size up - the owner asks when the slow session
start gets fixed, and the biggest single contributor answers as unrelated work.
`PL-7XNX` stays out on its own brief's reading and keeps
`feature: parallel-sessions`.

**Backfilled 2026-09-16**, with `claude/confident-gauss-r3rg8i` merged as
`ff4be61` (`#635`) and its ref gone from the remote, so the five files were on
`main` and the edit was the one line each the brief predicted.
