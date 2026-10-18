---
id: PL-0JDP
title: bin/docket claim refuses a blocked item because a block releases a claim as it is written (PL-3FYK), so a design round on a blocked head - PL-979D on 2026-09-25, blocked by PL-HMZZ since #1027 - cannot follow the claim-before-pull-request rule and runs unclaimed
priority: P3
effort: M
status: done
classes: defect
feature: claim-record
milestone: v0.5.29
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claiming.py, subprojects/docket/tests/test_claims.py, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-26 triage pass
added: 2026-09-25
closed: 2026-10-18
pr: 1588
payoff: a design round on an item somebody else blocked can hold a claim, so every in-flight guard sees it and a second session does not triage or start the same item
verify: grep -q 'def test_claim_accepts_an_item_blocked_before_the_branch_touched_it' subprojects/docket/tests/test_claiming.py && grep -q 'def test_a_claim_on_an_item_already_blocked_on_the_base_is_held' subprojects/docket/tests/test_claims.py && grep -qF 'PL-0JDP' subprojects/docket/src/docket/claims.py
---

**Problem.** bin/docket claim refuses a blocked item because a block releases a claim as it is written (PL-3FYK), so a design round on a blocked head - PL-979D on 2026-09-25, which PL-HMZZ held from #1027 until it closed in #1056 on 2026-09-26 - cannot follow the claim-before-pull-request rule and runs unclaimed

Read 2026-09-26 against `origin/main` (`17c9f3ed`). Before writing a claim,
`claiming.py` refuses any id whose `HEAD` copy is in `RELEASING_STATUSES`: "is
`blocked` in HEAD's copy, which releases a claim as soon as it is written; set
its status first". `claims.py` put `blocked` in that tuple on the project
owner's answer in `PL-3FYK` (2026-09-24, ratified, over `PL-KWCY`'s rule of
holding a claim until the item is `done` or `dropped`). The question that answer
took asked whether a claim should be released "when the branch's own copy of its
item moves to `blocked`". The shipped test is whether that copy *is* `blocked`,
which also catches a block the branch inherited from the base.

**Why it matters.** A claim is the one record every in-flight reader consults
(`PL-MB2W`). A round that cannot write one is invisible to `next`, `flight`,
`show` and triage alike, so a second session can triage or start the same item:
the `PL-N1JK` collision, found only at the merge. The recorded reason for the
rule is that "a session that blocks its own item has stopped working it". A
design round on an item somebody else blocked is still working it, and the rule
releases that round too. Running a design ahead of its blocker's build is the
Projects trial's own order (`PL-NZC0`: design threads first), so the case will
come up again.

**Decision needed.** Should a claim hold on an item that was already `blocked`
before the claiming branch touched it? This changes a ratified answer, so it is
put back to the owner (`CLAUDE.md`), even though option A is closer to the
question as it was asked.

- **A: only a block the branch writes releases its claim.** `claim` accepts an
  item whose base copy is already `blocked`. A session that blocks its own item
  still releases, so the recorded reason stands. Cost: `claims.holdings`, the
  reader every in-flight guard uses, must also read the base's copy of the item.
- **B: keep the rule and document it.** A round on a blocked item stays
  unclaimed. `.claude/skills/docket/modes/start.md` says such a round cannot
  claim, and what covers it instead. No code, and the gap stays.

**Recommended: A.** It is what the 2026-09-24 question asked, and it keeps that
answer's reason whole. B costs nothing now, but it leaves the record every guard
reads blind to a kind of work the trial schedules on purpose.

**Answered 2026-09-26: A** (project owner, 2026-09-26, ratified, over B, which
kept the refusal and said in `start.md` that such a round cannot claim).

**Done when.** `bin/docket claim` on an item another branch blocked writes a
claim that `bin/docket flight` shows as live; a block the claiming branch writes
still releases its claim, which
`test_the_branch_s_own_copy_reaching_a_releasing_status_releases_the_claim`
holds today; and the comment on `RELEASING_STATUSES` and the README's "A claim
ends in one of five ways" paragraph record the answer.

**Generator check.** Not a new head. The misread fact is who holds an item now,
which is `PL-MB2W`'s `misread:`. This item was filed 2026-09-25, a day before
that head closed, and never joined its `root-cause-of:`. That head's
`generator:` line pre-registers two residuals, both rounds that forget to claim;
this is a third, a round that cannot. It follows from how the 2026-09-24 answer
was implemented, not from a reader re-deriving the fact.

**Worked, 2026-10-18, on answer A.** `claims.releases(status, on_base)` is the
one rule both readers ask. A `blocked` copy releases a claim only where the
base's copy is not blocked, so only a block the branch wrote counts. Closed
statuses release as before. `claiming._branch` reads the base's copy beside
`HEAD`'s and refuses only on that rule. `holdings` passes the base's status in.

`test_a_blocked_claim_with_no_disposition_behind_it_leaves_the_branch_live` lost
its `blocked_on_base` case, which asserted the behaviour this item reverses: a
claim on an item the base had already blocked read as released by status. The
new `test_a_claim_on_an_item_already_blocked_on_the_base_is_held` states the
reverse. `test_a_claim_that_could_not_hold_is_refused_before_anything_is_written`
now blocks the item on the branch itself, since a block from the base is no
longer refused. `arming.py`'s module docstring still says a block releases a
claim, citing `claims.RELEASING_STATUSES`. It is still true of a block the
branch writes, and it was left alone because an edit there holds a pull
request for the owner's read.
