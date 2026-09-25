---
id: PL-0JGZ
title: 'Does a branch change only the queue' has two definitions - claims.in_queue counts ROADMAP.md and WORKING_NOTES.md, arming counts docs/items only - so a ROADMAP.md-only branch passes branch_id_check and shows no unclaimed row while arm holds it
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_claims.py
added: 2026-09-25
---

**Problem.** 'Does a branch change only the queue' has two definitions - claims.in_queue counts ROADMAP.md and WORKING_NOTES.md, arming counts docs/items only - so a ROADMAP.md-only branch passes branch_id_check and shows no unclaimed row while arm holds it

Reproduced: `in_queue` True, `work_under_record` False; `arm` says `hold - ... changes 1 path outside docs/items`. PL-FFR0 moved one predicate into claims.py; this is the next one.

**Why it matters.** Two answers to whether a branch is captures-only decide auto-merge and the CI refusal differently.

**Done when.** One definition in claims.py that arming imports.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
