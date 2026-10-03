---
id: PL-G2FY
title: tools/doc_check.py reads a Makefile recipe one tab-led line at a time, so a recipe command continued by a backslash is declined by gate parity and compared as a fragment by the coverage gate, where make hands the shell the command whole
status: untriaged
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-10-03
---

**Problem.** tools/doc_check.py reads a Makefile recipe one tab-led line at a time, so a recipe command continued by a backslash is declined by gate parity and compared as a fragment by the coverage gate, where make hands the shell the command whole
