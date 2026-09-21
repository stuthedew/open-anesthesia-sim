---
id: PL-CZR6
title: bin/docket stranded reported no branch carrying work its own pull request left behind while claude/sharp-lamport-t545rs carried two PL-X5PK commits pushed an hour after #823 squash-merged from it
priority: P2
effort: M
status: ready
classes: defect
feature: stranded-report-fidelity
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-21
payoff: a commit pushed after its own pull request merged is reported, so the read built to catch squash-merge leftovers actually catches them
verify: grep -q 'def test_a_commit_pushed_after_the_merge_is_reported_orphaned' subprojects/docket/tests/test_vcs.py
---

**Problem.** bin/docket stranded reported no branch carrying work its own pull request left behind while claude/sharp-lamport-t545rs carried two PL-X5PK commits pushed an hour after #823 squash-merged from it

**Re-measured 2026-09-21.** `bin/docket stranded` again closed with the line
saying no branch carries work its own pull request left behind, across 16
unmerged branch refs. The branch this item names is gone from the remote now, so
the original instance cannot be replayed; what stands is that the read reports
nothing on a checkout holding 16 unmerged refs, beside `PL-NPWP` recording the
item half of the same command reporting five refs that no longer exist.

**Why it matters.** This is the half of `stranded` built to catch what a squash
merge leaves behind, which is the shape this project's history keeps producing:
the pull request closes, the forge deletes the head branch, and anything pushed
to it after the merge is reachable only from a ref nobody will fetch again. A
reader told nothing is behind has been given the strongest possible claim on the
weakest possible evidence, and no second check anywhere would contradict it.

**Done when.** A commit pushed to a branch after that branch's own pull request
merged is named by the `orphaned` read together with the command that recovers
it, and a test in `subprojects/docket/tests/test_vcs.py` drives that sequence.
