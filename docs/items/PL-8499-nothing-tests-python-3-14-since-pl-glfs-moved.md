---
id: PL-8499
title: Nothing tests Python 3.14 since PL-GLFS moved the pin to 3.15, yet requires-python still admits 3.14, so a 3.15-only feature would pass every check and fail at import on 3.14: raise the floor to 3.15 with drift.yml's relaxed copy, or test the floor in CI
status: untriaged
added: 2026-11-14
---

**Problem.** Nothing tests Python 3.14 since PL-GLFS moved the pin to 3.15, yet requires-python still admits 3.14, so a 3.15-only feature would pass every check and fail at import on 3.14: raise the floor to 3.15 with drift.yml's relaxed copy, or test the floor in CI
