---
id: PL-V03Q
title: v0.5.0's gate records no disposition for PL-0S0V and PL-VJZK, both safety+anticipated: the anticipated rule says they are not debt against a gate that precedes the hazard, and that disposition has to be written where doc_check reads it
priority: P2
effort: S
status: dropped
classes: planning
touches: ROADMAP.md
closed: 2026-09-17
reason: Done in the session that filed it. Captured while the missing disposition looked like a doc_check advisory; it is enforced by test_this_repository_records_a_disposition_for_every_open_debt_item, so `make check` failed and the disposition was written in the same commit as the triage that created the debt. The test's own docstring says triage is where a disposition belongs, so this was never separable work.
feature: preferences-store
added: 2026-09-17
---

**Problem.** v0.5.0's gate records no disposition for PL-0S0V and PL-VJZK, both safety+anticipated: the anticipated rule says they are not debt against a gate that precedes the hazard, and that disposition has to be written where doc_check reads it
