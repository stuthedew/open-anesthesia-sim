---
id: PL-YDL6
title: An item whose work landed in one pull request but whose status done was written in a later one recovers the later number, which carries the closure but none of the work
status: ready
priority: P2
effort: S
classes: defect, infra
feature: dev-tooling
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_closure_split_from_its_work_recovers_the_work_s_pull_request' subprojects/docket/tests/test_vcs.py
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-04
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
