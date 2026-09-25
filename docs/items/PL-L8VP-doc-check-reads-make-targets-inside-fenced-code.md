---
id: PL-L8VP
title: doc_check reads make targets inside fenced code blocks, so a shell comment '# make sure the virtualenv' or make's own 'No rule to make target' output fails make check; fences contribute 5 real mentions of 112
status: untriaged
feature: exact-gates
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-25
---

**Problem.** doc_check reads make targets inside fenced code blocks, so a shell comment '# make sure the virtualenv' or make's own 'No rule to make target' output fails make check; fences contribute 5 real mentions of 112

Reproduced both. 107 make targets are checked in code spans, all real; 5 in fences, all real. Scanning fences buys 5 checked mentions and brings two false-refusal classes.

**Why it matters.** Same class as PL-YSMV: a gate refusing correct content.

**Done when.** Fenced blocks are not scanned for make targets, or only lines that begin with `make `; a test holds both reproductions through a clean run.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
