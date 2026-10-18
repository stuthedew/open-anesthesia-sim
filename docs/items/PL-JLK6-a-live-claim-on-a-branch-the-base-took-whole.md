---
id: PL-JLK6
title: A live claim on a branch the base took whole prints 'no commit of its own this checkout can read' in flight, and Holdings.head is empty there so arm gives no --self hint, because Holdings.last leaves taken branches out (found reviewing PL-7XGR)
priority: P3
effort: S
status: done
classes: defect
feature: claim-integrity
touches: subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claims.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-18 triage pass
added: 2026-10-18
closed: 2026-10-18
payoff: a live claim on a branch the base took whole names its head commit in flight, and arm gives its --self hint there
verify: grep -q 'def test_a_live_claim_on_a_branch_the_base_took_whole_names_its_head' subprojects/docket/tests/test_claims.py
reenters: PL-927J
---

**Problem.** A live claim on a branch the base took whole prints 'no commit of its own this checkout can read' in flight, and Holdings.head is empty there so arm gives no --self hint, because Holdings.last leaves taken branches out (found reviewing PL-7XGR)

**Why it matters.** `bin/docket flight` tells a session what another branch is
doing, and `bin/docket arm` tells it how to check its own work. On a branch
whose only content another pull request landed, a live claim prints "no commit
of its own this checkout can read", which reads as an unreadable branch rather
than a taken one. `arm` then gives no `--self` hint, because `Holdings.head` is
empty there. Nothing is lost, but both lines mislead the reader about the
branch.

**Found 2026-10-18** by the review of `PL-7XGR` (#1588). `PL-7XGR` keeps such a
claim live, but `Holdings.last` still leaves taken branches out, so the claim's
head commit is never read.

**Done when.** A live claim on a branch the base took whole names that branch's
head commit in `bin/docket flight`, and `Holdings.head` is set for it, so `arm`
gives its `--self` hint. A test in `subprojects/docket/tests/test_claims.py`
pins it.

**Generator check.** An instance of `PL-927J`'s fact, "whether the base already
holds or has superseded a branch commit's change", filed after that head
closed: `Holdings.last` reads "taken" as "nothing of its own". So
`reenters: PL-927J` is set.
