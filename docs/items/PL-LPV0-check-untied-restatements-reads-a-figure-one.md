---
id: PL-LPV0
title: check_untied_restatements reads a figure one line at a time, so a stored value written with its unit on the next line, such as 2.5 and then L, is never asked about
status: untriaged
feature: model-claims-held-by-tests
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/MODEL.md
added: 2026-11-02
---

**Problem.** check_untied_restatements reads a figure one line at a time, so a stored value written with its unit on the next line, such as 2.5 and then L, is never asked about
