---
id: PL-NZ0R
title: The mutation-copy CI job runs the tests in mutmut's copy without mutmut's own pytest plugin, so a fault in that plugin stops every mutation run while the job passes, as PL-LR03's did for a day
status: untriaged
added: 2026-11-28
filed-pr: 2346
---

**Problem.** The mutation-copy CI job runs the tests in mutmut's copy without mutmut's own pytest plugin, so a fault in that plugin stops every mutation run while the job passes, as PL-LR03's did for a day
