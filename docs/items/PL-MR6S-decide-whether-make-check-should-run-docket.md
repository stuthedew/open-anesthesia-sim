---
id: PL-MR6S
title: Decide whether make check should run docket check --verify, which CI runs and local does not: 147 commands in 150s against a gate run before every commit, and PL-7VSK is what the gap cost
status: dropped
reason: duplicate of PL-0HPV, filed 2026-09-14, which asks the same question against a current cost measurement
added: 2026-09-15
closed: 2026-09-15
---

**Problem.** Decide whether make check should run docket check --verify, which CI runs and local does not: 147 commands in 150s against a gate run before every commit, and PL-7VSK is what the gap cost

**Dropped 2026-09-15 as a duplicate of `PL-0HPV`**, which was filed a day
earlier and is already `needs-decision` on `main`: *"make check omits the
verify replay on a cost measured before `--verify-base` narrowed it, so a
PR-only failure class is only ever found from CI."*

`PL-0HPV` is the better statement of it, and the difference matters rather
than being a matter of wording. This item argued the cost from 147 commands in
150 s; `PL-0HPV` records that that measurement predates `--verify-base`
narrowing the replay, so the number this item reasoned from - and the
recommendation built on it - rested on a figure already superseded. The
question reaches the owner through `PL-0HPV` with a current one.

