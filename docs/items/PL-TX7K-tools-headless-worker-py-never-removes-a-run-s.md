---
id: PL-TX7K
title: tools/headless_worker.py never removes a run's clone: every run, failed or pushed, leaves a full clone and a log in ~/.local/state/open-anesthesia-sim/workers until the owner deletes it by hand. Keep failed runs' clones for diagnosis and remove a clone once its branch is pushed
status: untriaged
feature: api-credit-runs
added: 2026-10-19
---

**Problem.** tools/headless_worker.py never removes a run's clone: every run, failed or pushed, leaves a full clone and a log in ~/.local/state/open-anesthesia-sim/workers until the owner deletes it by hand. Keep failed runs' clones for diagnosis and remove a clone once its branch is pushed
