---
id: PL-7K2C
title: quality.yml runs six to eleven tool checks after the whole-store verify replay, so a replay failure skips contrast, import-boundary, core-vocabulary and glyph checks on that main commit entirely - moving the replay to the end of the job would cost nothing and close the gap
status: untriaged
added: 2026-09-20
---

**Problem.** quality.yml runs six to eleven tool checks after the whole-store verify replay, so a replay failure skips contrast, import-boundary, core-vocabulary and glyph checks on that main commit entirely - moving the replay to the end of the job would cost nothing and close the gap
