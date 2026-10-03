---
id: PL-6P6H
title: tools/doc_check.py's workflow_commands reads a folded run: > block as a literal one, so a command YAML folds onto one line is read as several; no workflow uses > today
status: untriaged
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-10-03
---

**Problem.** tools/doc_check.py's workflow_commands reads a folded run: > block as a literal one, so a command YAML folds onto one line is read as several; no workflow uses > today
