---
id: PL-0JDP
title: bin/docket claim refuses a blocked item because a block releases a claim as it is written (PL-3FYK), so a design round on a blocked head - PL-979D on 2026-09-25, blocked by PL-HMZZ since #1027 - cannot follow the claim-before-pull-request rule and runs unclaimed
priority: P3
effort: M
status: needs-decision
classes: defect
feature: claim-record
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claiming.py, subprojects/docket/tests/test_claims.py, .claude/skills/docket/modes/start.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-26 triage pass
added: 2026-09-25
payoff: a design round on an item somebody else blocked can hold a claim, so every in-flight guard sees it and a second session does not triage or start the same item
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

**Done when.** Under A: `bin/docket claim` on an item another branch blocked
writes a claim that `bin/docket flight` shows as live; a block the claiming
branch writes still releases its claim; and the comment on `RELEASING_STATUSES`
records the answer. Under B: `start.md` says a round on a blocked item cannot
claim, and what covers it instead.

**Generator check.** Not a new head. The misread fact is who holds an item now,
which is `PL-MB2W`'s `misread:`. This item was filed 2026-09-25, a day before
that head closed, and never joined its `root-cause-of:`. That head's
`generator:` line pre-registers two residuals, both rounds that forget to claim;
this is a third, a round that cannot. It follows from how the 2026-09-24 answer
was implemented, not from a reader re-deriving the fact.
