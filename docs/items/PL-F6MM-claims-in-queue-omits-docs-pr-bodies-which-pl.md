---
id: PL-F6MM
title: claims.in_queue omits docs/pr-bodies/, which PL-979D's pr-title check now makes every pull request carry, so a claimless capture, triage or design-round branch fails branch_id_check once it records its body
priority: P1
effort: S
status: done
classes: defect
feature: claim-record
touches: subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claims.py, tools/branch_id_check.py, tests/unit/test_branch_id_check.py, .claude/hooks/docket-branch-guard.sh
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-26 triage pass
added: 2026-09-26
closed: 2026-09-26
pr: 1077
payoff: a capture, triage or design-round pull request merges without a claim again, and flight's unclaimed row stops counting it as a forgetful session
verify: grep -q 'def test_a_body_record_is_not_work_that_owes_a_claim' subprojects/docket/tests/test_claims.py && grep -qF 'pr-bodies' subprojects/docket/src/docket/claims.py && grep -q 'def test_the_gate_keeps_its_own_copy_of_the_body_records' subprojects/docket/tests/test_claims.py
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

**Started 2026-09-26** on `claude/sleepy-ritchie-ijawxp`, with the capture
recovered from #1066's branch (`27f22b10`), where it could not reach `main` past
the defect it records. Reproduced end to end before the fix: `check_claims`
refused #1066's head and `b0496c7e` and passed `b0496c7e~1`, and `flight` on
`origin/main`'s code printed `unclaimed: origin/claude/youthful-wright-xp76fh`.
With the fix all three pass and the row is gone.

**Built, the same under either answer below.** `claims.RECORDS` beside
`in_queue`, and `claims.queue_records`, the one list `in_queue` counts and
`branch_id_check._queue_named` prints, so the check and its refusal's wording
cannot drift apart again. `test_a_body_record_is_not_work_that_owes_a_claim`
holds `flight`'s side, and
`test_a_body_record_owes_no_claim_and_the_refusal_names_the_records` in
`tests/unit/test_branch_id_check.py` holds CI's, with the refusal naming the
records. `.claude/hooks/docket-branch-guard.sh`'s comment said a capture writes
"only item files", stale since `PL-3CTW`, and rides here.

**Decided on the way: CI does not ask a `--recover` pass for a claim** (session's
call, 2026-09-26, over telling a branch's own record from a recovery). The whole
directory counts, as it does for `arm` and `verify`. Telling the two apart takes
more than the path - each file's header (`recorded:` against `commit:`), or the
base's squash subjects, another spelling of the pull-request number `PL-PVW2`'s
build is consolidating - and would buy a refusal for a pass with almost nothing
left to do. `pr_body_check.recovered()` counts every record, so no pull request
that recorded its body is ever reported lost, and the digest reported two left
on 2026-09-26. `CLAUDE.md`'s housekeeping rule still files and claims such a
pass; only CI's enforcement of it goes, and `in_queue`'s docstring says so.
Reopen it if a claimless recover-only branch turns up.

**Decided: `arming.py` keeps its own copy of the records, pinned equal by a
test** (project owner, 2026-09-26, ratified, over `arming.py` importing
`claims.RECORDS` as the proposed patch had it). Importing would move part of
what arms on green out of the one file the gate holds for a read
(`arming.GATE`, "a change to it could loosen the rule it states"). `claims.py`
sits under `subprojects/docket/`, which arms on green, so a one-line edit to
`claims.RECORDS` - widened to `docs/`, say - would merge unreviewed and from then
on arm any pull request touching `docs/MODEL.md`. Kept in `arming.py`, that
widening still takes an edit the gate holds, and
`test_the_gate_keeps_its_own_copy_of_the_body_records` pins
`claims.RECORDS == arming.RECORDS`, so the two cannot disagree on `main`; it was
seen failing at its assertion with `arming.RECORDS` widened in memory. So the
done-when's "one definition `arming.RECORDS` also reads" is met as two spellings
a test holds equal. Cost: the directory is spelled twice, so changing it is two
edits, and the test names the second. `arming.py` and `verify.py` are untouched,
and `arming.py` left `touches` with the patch that would have edited it. The
one-spelling route that keeps the gate whole, `claims.py` reading
`arming.RECORDS`, needs a function-level import, because `arming.py` already
imports `claims.py`.
