---
id: PL-FKH6
title: Four minor check misreads from the 2026-09-25 stress test: dead_ends reads a > quote line after an entry as a continuation, the recommendation marker counts 'lacks a recommendation:' as marked, possessive_section_check refuses quoting a bold lead sentence, and doc_check's line-citation check fires on an item describing a bad citation inline
status: untriaged
feature: exact-gates
touches: tools/dead_ends.py, tools/possessive_section_check.py, subprojects/docket/src/docket/checks.py
added: 2026-09-25
---

**Problem.** Four minor check misreads from the 2026-09-25 stress test: dead_ends reads a > quote line after an entry as a continuation, the recommendation marker counts 'lacks a recommendation:' as marked, possessive_section_check refuses quoting a bold lead sentence, and doc_check's line-citation check fires on an item describing a bad citation inline

Each reproduced once in the fuzz harness. None has cost a session yet that the store records.

**Why it matters.** Low; recorded so the class count is honest.

**Done when.** Each either fixed with a test or dropped with its reason.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
