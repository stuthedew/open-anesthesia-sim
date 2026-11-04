---
id: PL-52SV
title: The coordinator's summary lists no pull request that waits on the owner's read with no Owner-ask recorded, which PL-X4MD's approved step 3 asked for; bin/docket flight could name each such branch, which needs arm --owner-ask to answer for a branch other than the checked-out one
priority: P2
effort: M
status: ready
classes: feature
feature: owner-ask-by-state
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py, .claude/skills/docket/modes/coordinator.md
added: 2026-11-04
payoff: a pull request held for the owner with nobody asked is named in the coordinator's summary instead of waiting unseen
verify: grep -q 'def test_flight_marks_a_waiting_pull_request_with_no_recorded_question' subprojects/docket/tests/test_cli.py
---

**Problem.** The coordinator's summary lists no pull request that waits on the owner's read with no Owner-ask recorded, which PL-X4MD's approved step 3 asked for; bin/docket flight could name each such branch, which needs arm --owner-ask to answer for a branch other than the checked-out one

**Found 2026-11-04.** `PL-X4MD`'s approved design had three steps. Step 1's test passed, so step 2 was built, and its Done-when made step 3 conditional on step 1 failing. Step 3 was part of the approved recommendation all the same: "The coordinator's summary lists every pull request that waits on the owner with no recorded question." `.claude/skills/docket/modes/coordinator.md` § "Reporting to the owner" has no such list, and `bin/docket arm --owner-ask` answers only for the checked-out branch.

**Why it matters.** Step 2 attaches a recorded question only to a message that names a waiting pull request. A thread that waits on the owner and never messages them leaves the pull request held with nobody asked, and nothing names it.

**Done when.** `bin/docket flight` marks each branch whose pull request waits on the owner's review and records no `Owner-ask:`, and the coordinator mode's "Where things stand" list names each one. A test in `subprojects/docket/tests/test_cli.py` finds a waiting branch with no recorded question marked, and one with a question not marked.

**Generator check.** One-off: the rest of work the owner approved under `PL-X4MD`. That approval, on 2026-11-03, is what lifts the pause on new workflow mechanisms for it (`PL-6Q9L`).
