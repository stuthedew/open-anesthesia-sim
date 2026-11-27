---
id: PL-4NF3
title: Rename learner to user in bin/docket arm's owner-ask text (subprojects/docket/src/docket/arming.py READ_ASK) and in the docket tests that pin it, which PL-PGVL left because a change to those tests holds the pull request for the owner's read
priority: P3
effort: S
status: ready
classes: housekeeping
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_arming.py
added: 2026-11-27
filed-pr: 2328
payoff: a session reads one wording of how to put a question to the owner, in the user's terms
---

**Problem.** Rename learner to user in bin/docket arm's owner-ask text (subprojects/docket/src/docket/arming.py READ_ASK) and in the docket tests that pin it, which PL-PGVL left because a change to those tests holds the pull request for the owner's read

**Why it matters.** The project owner asked on 2026-11-27 that the person using the simulator be called "the user" everywhere (`PL-PGVL`). `bin/docket arm` still tells a session to word an owner question "in clinical or learner terms" and to say "what a learner sees", while rule 10 of `.claude/rules/instruction-writing.md` and `docs/maintainer.md` now say "in clinical terms, as a user would put it". So a session reading both gets two wordings of one rule.

**Done when.** `READ_ASK` and the comment above it in `subprojects/docket/src/docket/arming.py` match rule 10's wording, and `subprojects/docket/tests/test_cli.py` and `subprojects/docket/tests/test_arming.py` use "user". Choose a phrase for the question that does not contain "what a user sees", because `test_arm_read_ask_asks_in_learner_terms_with_screenshots` checks that its phrases appear in order and "what a learner sees" comes later in the text. The pull request holds for the owner's read because it edits tests that pin the gate's answers. The Owner-ask is that the gate refuses and accepts exactly what it did before, so only its wording changes.

**Generator check.** One-off: the remainder of `PL-PGVL`.
