---
id: PL-PNSV
title: bin/docket new recorded PL-F67Q as a recurrence of PL-S86L on 2026-10-25 because the new title cited PL-S86L and its file, though PL-F67Q is a different defect (finer-step coverage, not a stale claim); a recurrence means the same defect filed again, so a citing capture inflates the count that names promotion candidates
priority: P1
effort: S
status: done
classes: defect
feature: recurrence-signal
milestone: v0.6.9
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_claims.py, subprojects/docket/README.md, docs/items/PL-CR81-projects-threads-in-the-v0-7-0-project-run.md
deferred-from: v0.7.0 - captured after the freeze, at the owner's request in the workflow lane, and built at once; the generator tier ranks it, not the gate
added: 2026-10-25
closed: 2026-10-25
pr: 1835
payoff: A capture made while working an item is no longer counted as that item's defect firing again, so the promotion candidates bin/docket next names rest only on filings by sessions that did not know the item existed
verify: grep -q 'def test_new_records_nothing_on_an_item_this_branch_claims' subprojects/docket/tests/test_cli.py
impairs-generators: docket.cli.cmd_new records a recurrence on the item the filing branch is itself working, through duplicates.near_duplicates' working-tree key, so plan.recurrence_chains counts filings by a session that knew the item existed toward the promotion floor
reenters: PL-0HLS
---

**Problem.** bin/docket new recorded PL-F67Q as a recurrence of PL-S86L on 2026-10-25 because the new title cited PL-S86L and its file, though PL-F67Q is a different defect (finer-step coverage, not a stale claim); a recurrence means the same defect filed again, so a citing capture inflates the count that names promotion candidates

**Reproduced 2026-10-25.** Replaying the filing through `duplicates.near_duplicates` against the store at `8bc204ef^`, with the paths that branch was changing, selects PL-S86L on two shared paths, `docs/MODEL.md` and `tests/reference/test_coupled_dynamics.py`, at a title similarity of 0.167 against the 0.15 floor. `duplicates.anchor` then picks it. The id in the title did not select it, because PL-S86L does not declare its own file. So the cause is the working-tree key (`PL-THLT`). A capture with no `--touches` keys on the paths the branch is changing, and this branch was changing PL-S86L's files because it was working PL-S86L.

**Measured 2026-10-25.** Of the 178 entries recorded in `recurrences:` across the store, 68 name a capture filed by the pull request that carried the matched item's own id, so the capture was made while that item was being worked. Sessions had withdrawn 24 of those 68 by hand (35%), against 18 of the other 110 (16%). A sample of ten of the 44 still standing found seven follow-ups to the item in hand, such as a mitigation, an experiment or a question for the owner, and three further instances of the item's mechanism at another site.

**Why it matters.** `plan.recurring` defines a recurrence as a filing by a session that hit the defect without knowing the item existed. A session working the item knows it exists, so its captures are never that. Once the item closes, `plan.recurrence_chains` counts it as an earlier filing of each capture recorded on it, which moves those captures towards the two recurrences at which `bin/docket next` names a promotion candidate. Today the only standing effect on an open item is PL-CR81, whose one recurrence is PL-876V, a mitigation filed while PL-CR81 was being worked, and it does not reach the floor. The three genuine instances in the sample are not lost by excluding them: the session that finds a second instance of the item it is working knows both, and `CLAUDE.md` gives it `--feature` grouping and `root-cause-of:` to record that.

**Done when.** `bin/docket new` neither prints nor records as a possible earlier filing any item that a `Claim:` trailer on the branch's own commits names. A test in `subprojects/docket/tests/test_cli.py` files a capture on a branch claiming the item it would otherwise match, and shows nothing recorded. PL-CR81's entry for PL-876V is withdrawn, and `subprojects/docket/README.md` § "Capture costs nothing" states the exclusion and why.

**Generator check.** The fact misread is whether an open item already describes the mechanism a new capture names, which is the `misread:` of the head PL-0HLS. PL-0HLS closed on 2026-10-12 after fixing four gaps in the search's key, among them PL-SV0D, where the working-tree key matched on the store directory that every branch changes. This is the same key reading another path the branch changes for its own reasons, the files of the item it is working, so it is recorded as a re-entry of PL-0HLS. It is the first since PL-0HLS closed, so no generator is owed yet.

**Regression test, run 2026-10-25.** With `src/docket/cli.py` and `src/docket/claims.py` as they stood before the fix, `uv run pytest tests/test_cli.py -k records_nothing_on_an_item_this_branch_claims`, run from `subprojects/docket/`, fails with `AssertionError: the item in hand is not offered as an earlier filing`. The unclaimed control in the same test is matched and recorded first, so the failure comes from the claim alone. The test passes with the fix.
