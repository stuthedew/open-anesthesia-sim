---
id: PL-XQXK
title: The numeric-paragraph check reads a figure only in the units PROSE_UNITS lists (L/min, L, %, kg, s, MAC and time words), so a paragraph stating px, mL, mmHg or percentage points is no member: decide whether to widen PROSE_UNITS, which widens check_untied_restatements too
status: untriaged
feature: model-claims-held-by-tests
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-11-02
---

**Problem.** The numeric-paragraph check reads a figure only in the units PROSE_UNITS lists (L/min, L, %, kg, s, MAC and time words), so a paragraph stating px, mL, mmHg or percentage points is no member: decide whether to widen PROSE_UNITS, which widens check_untied_restatements too
