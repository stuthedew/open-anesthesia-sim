---
id: PL-FRRQ
title: The Yasuda notes in the three agent data files judge the stored tissue:gas coefficients by whether a measured value rounds to them ("rounding to the stored precision explains only two", "2.04 does not round to"); the project owner said on 2026-11-09 'I wouldn't round coefficients', and MODEL.md now gives each difference as a percentage, so the notes should say the same
status: untriaged
feature: model-md-structure
touches: src/anesthesia_sim/data/agents
added: 2026-11-09
---

**Problem.** The Yasuda notes in the three agent data files judge the stored tissue:gas coefficients by whether a measured value rounds to them ("rounding to the stored precision explains only two", "2.04 does not round to"). The project owner said on 2026-11-09 'I wouldn't round coefficients', and `docs/MODEL.md` now gives each difference as a percentage, so the notes should say the same.

**Generator check.** The rounding comparison is a one-off, written on 2026-09-13 when the Yasuda notes were added to the three agent data files. `docs/MODEL.md` was corrected on 2026-11-09 in pull request 2054.
