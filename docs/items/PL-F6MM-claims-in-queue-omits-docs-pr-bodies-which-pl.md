---
id: PL-F6MM
title: claims.in_queue omits docs/pr-bodies/, which PL-979D's pr-title check now makes every pull request carry, so a claimless capture, triage or design-round branch fails branch_id_check once it records its body
priority: P1
effort: S
status: ready
classes: defect
feature: claim-record
touches: subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_claims.py, tools/branch_id_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-26 triage pass
added: 2026-09-26
payoff: a capture, triage or design-round pull request merges without a claim again, and flight's unclaimed row stops counting it as a forgetful session
verify: grep -q 'def test_a_body_record_is_not_work_that_owes_a_claim' subprojects/docket/tests/test_claims.py && grep -qF 'pr-bodies' subprojects/docket/src/docket/claims.py
---

**Problem.** claims.in_queue omits docs/pr-bodies/, which PL-979D's pr-title check now makes every pull request carry, so a claimless capture, triage or design-round branch fails branch_id_check once it records its body

**Found 2026-09-26 on #1066, a triage pass.** `checks` failed at
`tools/branch_id_check.py` ("this branch claims nothing") on `b0496c7e`. The
branch's only commit outside `docs/items/` is `docs/pr-bodies/1066.md`, which
`tools/pr_body_check.py --record` wrote because `pr-title`'s required job now
fails without it (`PL-979D`, #1068). Reproduced locally the same day:
`check_claims` refuses at `HEAD` and refuses nothing at `HEAD~1`, which is the
same branch without the record.

**Why it matters.** On a claimless branch that changes only the queue and has
a body, the two required checks cannot both pass. `pr-title` fails without the
record, and `checks` fails with it. So every capture, triage pass or design
round that does not claim is blocked from merging, although `in_queue`'s own
docstring says such a branch owes no claim. `flight`'s `unclaimed:` row asks
the same `claims_nothing`, so it also counts each such branch as a forgetful
session, into `PL-MB2W`'s pre-registered 1-in-20 threshold.

**Done when.** `claims.in_queue` admits the body records, from the one
definition `arming.RECORDS` also reads, and `_queue_named` in
`tools/branch_id_check.py` names them. A test holds a branch whose only commit
outside the queue is its own body record as owing no claim. One thing to decide
on the way: admitting the whole directory also stops asking a claim of a
`--recover` pass, which is housekeeping that `CLAUDE.md` says is claimed.
Proposed patch: move `RECORDS = "docs/pr-bodies/"` into `claims.py` beside
`in_queue`, add `or path.startswith(RECORDS)` to its return, and have `arming.py`
import it rather than spell it again.

**Generator check.** A candidate instance of `PL-PVW2`'s fact, which spelling
of a repeated predicate is the answer. "Which paths a queue workflow writes" is
spelled in `arming.py` (`RECORDS`), in `verify`'s sanction and in
`claims.in_queue`, and `PL-979D`'s build moved the first two. It is not written
into `PL-PVW2`'s `root-cause-of:` here, since that head's thread is the
Projects trial's Stream A.
