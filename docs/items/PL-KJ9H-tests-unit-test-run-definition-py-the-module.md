---
id: PL-KJ9H
title: tests/unit/test_run_definition.py: the module docstring calls 1.8e-14 eleven orders of magnitude below 1e-4 (it is about ten), and the comment above FORK_OFF_KEYFRAME_DIVERGENCE_CEILING says one hour past a fork at 655.3 s though the run ends at 3600 s (found in the PL-FDMJ prose pass, 2026-10-25)
status: untriaged
feature: stale-source-claims
added: 2026-10-25
---

**Problem.** tests/unit/test_run_definition.py: the module docstring calls 1.8e-14 eleven orders of magnitude below 1e-4 (it is about ten), and the comment above FORK_OFF_KEYFRAME_DIVERGENCE_CEILING says one hour past a fork at 655.3 s though the run ends at 3600 s (found in the PL-FDMJ prose pass, 2026-10-25)
