---
id: PL-52SV
title: The coordinator's summary lists no pull request that waits on the owner's read with no Owner-ask recorded, which PL-X4MD's approved step 3 asked for; bin/docket flight could name each such branch, which needs arm --owner-ask to answer for a branch other than the checked-out one
priority: P2
effort: M
status: done
classes: feature
feature: owner-ask-by-state
milestone: v0.6.15
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, .claude/skills/docket/modes/coordinator.md
added: 2026-11-04
closed: 2026-11-04
pr: 2013
payoff: the coordinator sees a thread waiting on the owner with no question recorded before that thread messages the owner, not after
verify: grep -q 'def test_flight_names_a_pull_request_waiting_on_the_owner_with_no_question' subprojects/docket/tests/test_cli.py
---

**Problem.** The coordinator's summary lists no pull request that waits on the owner's read with no Owner-ask recorded, which PL-X4MD's approved step 3 asked for; bin/docket flight could name each such branch, which needs arm --owner-ask to answer for a branch other than the checked-out one

**Why it matters.** A thread can sit for hours on a pull request that waits on the owner's read without ever recording the question the owner is to answer. The owner-ask guard adds a line saying no question is recorded only once the thread messages the owner, which is too late to catch the gap. The coordinator runs `bin/docket flight` before it starts or reports on threads, so a row there is the earliest place the gap can be seen.

**Done when.** `bin/docket flight` names each open pull request whose branch waits on the owner's read with no `Owner-ask:` recorded since its newest change, on a line of its own. It reads that from the same owner-ask answer that `bin/docket arm --owner-ask` gives, asked for the remote's copy of each branch, so the checked-out branch does not matter. A branch whose question is recorded, or which does not wait on the owner, gets no such line. A test builds both kinds of branch and finds the line only on the one with no question.

**Generator check.** None. This is step 3 of `PL-X4MD`'s approved design, left unbuilt there, and adds no head of its own.
