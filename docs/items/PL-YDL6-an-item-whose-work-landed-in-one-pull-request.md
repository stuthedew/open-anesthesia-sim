---
id: PL-YDL6
title: An item whose work landed in one pull request but whose status done was written in a later one recovers the later number, which carries the closure but none of the work
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.4.15
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-04
closed: 2026-09-12
pr: 504
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_closure_split_from_its_work_records_no_pull_request' subprojects/docket/tests/test_vcs.py
---

**Problem.** `_number_closing` recovers a pull request by finding the commit
that wrote `status: done` into the item. Where the work and the closure landed
in *different* pull requests, that is the pull request carrying the closure and
none of the code - so `pr:` records a change whose diff does not contain the
work the item describes.

**Why it matters.** The split is not hypothetical: `docs/items/` and the code
are edited by different sessions on different branches, and the skill's own
close-out rule exists because of it - "Do not split the closure out to get the
number earlier", added after a merge landed between two pushes and left `main`
carrying the fix while the queue still called the item open (`PL-D2GW`, then
`PL-P5S0`). That rule reduces how often the split happens; it cannot prevent
it, and `docket record` writes the recovered number without a human reading it.
As with `PL-S5LB`, a wrong `pr:` is worse than an absent one, because `commit:`
was retired (`PL-T63T`) and `pr:` is the only surviving link to the work.

**Where.** `subprojects/docket/src/docket/vcs.py`, `_number_closing` and the
`cmd_record` path that consumes it; `subprojects/docket/tests/test_vcs.py`.

**Done when.** Where the closure and the work landed in different pull
requests, the recovery either names the one carrying the work or declines and
says why, rather than silently recording the closure's number. A test in
`test_vcs.py` fixes the case. Declining is an acceptable answer - `PL-99Y4`
already established that a provenance question the checkout cannot answer is
reported rather than guessed.

**Measured while fixing `PL-S5LB`, 2026-09-06: three items, and the recorded
value is the right one in all three.** Auditing every closed item's recorded
`pr` against what `_number_closing` recovers from real history, 249 of the 252
it can answer agree. The three that disagree are this shape, each off by one:

| Item | Recorded `pr` | What the walk recovers |
| --- | --- | --- |
| `PL-3CBS` | 128 | 129 |
| `PL-64LS` | 108 | 109 |
| `PL-D2GW` | 134 | 135 |

`#128` did `PL-3CBS`'s work and left the item at `status: ready`; the triage
pass merged as `#129` is what wrote `status: done`. So the store already holds
the better answer and needs no repair - what needs deciding is only what the
walk should do when the field is *missing*, which is this item.

That also bounds the problem: three items, all predating the same-commit
closure rule (`PL-D2GW`, `PL-P5S0`), and none of them reachable through the
subject scan, which `PL-GW37` made the first reading. Declining is a defensible
answer here, per the `Done when` above.


**Decided while closing, 2026-09-12: it declines rather than recovering the
work's pull request**, which is the second of the two answers this item's **Done
when.** allowed. Nothing in `vcs.py` knows which files an item's work was - that
is the item's own `touches`, which is store knowledge and would be read from the
branch rather than from the base - so naming the pull request that carried the
work cannot be done from here without guessing. `PL-99Y4` already settled the
posture for exactly that: a provenance question the checkout cannot answer is
reported rather than invented.

`_annotates_only` is the discriminator, which is the same rule that tells
recording an item from working on it everywhere else in the module: a closure
commit carrying its work touches something outside the queue. The `verify:`
command was renamed with the test to match the answer taken; the old name
described the option that was not.
