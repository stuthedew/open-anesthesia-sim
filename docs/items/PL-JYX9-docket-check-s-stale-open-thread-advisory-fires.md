---
id: PL-JYX9
title: docket check's stale-open-thread advisory fires on every run on docs/WORKING_NOTES.md's desflurane thread, its own documented permanent false fire, so it never changes a decision
status: untriaged
feature: exact-gates
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-25
---

**Problem.** docket check's stale-open-thread advisory fires on every run on docs/WORKING_NOTES.md's desflurane thread, its own documented permanent false fire, so it never changes a decision

Observed on every run of `docket check` in the stress test. `CLAUDE.md`: a check that fires every run without changing a decision is a defect in the check.

**Why it matters.** Every session reads past it, and a real stale thread arriving beside it is read past too.

**Done when.** Either retired, or a thread can be acknowledged with a dated marker the advisory honours; decide which in the item.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
