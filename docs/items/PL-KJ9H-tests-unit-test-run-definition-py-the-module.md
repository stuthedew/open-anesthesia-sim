---
id: PL-KJ9H
title: tests/unit/test_run_definition.py: the module docstring calls 1.8e-14 eleven orders of magnitude below 1e-4 (it is about ten), and the comment above FORK_OFF_KEYFRAME_DIVERGENCE_CEILING says one hour past a fork at 655.3 s though the run ends at 3600 s (found in the PL-FDMJ prose pass, 2026-10-25)
priority: P3
effort: S
status: done
classes: docs
feature: stale-source-claims
touches: tests/unit/test_run_definition.py
added: 2026-10-25
closed: 2026-10-25
pr: 1812
payoff: a reader weighing the fork test's tolerance against the displayed precision is given the true margin
verify: ! grep -qF 'eleven orders of magnitude below 1e-4' tests/unit/test_run_definition.py && ! grep -qF 'one hour past a fork at 655.3 s' tests/unit/test_run_definition.py
---

**Problem.** tests/unit/test_run_definition.py: the module docstring calls 1.8e-14 eleven orders of magnitude below 1e-4 (it is about ten), and the comment above FORK_OFF_KEYFRAME_DIVERGENCE_CEILING says one hour past a fork at 655.3 s though the run ends at 3600 s (found in the PL-FDMJ prose pass, 2026-10-25)

**Reproduced 2026-10-25.** `grep` on `main` at `b6ff4443` finds line 18 ("eleven orders of magnitude below 1e-4") and line 1670 ("one hour past a fork at 655.3 s"). One hour after 655.3 s is 4255.3 s, past a 3600 s run.

**Why it matters.** These comments state how far below the displayed precision a test's tolerance sits. A wrong margin tells a reader that a tolerance can be loosened safely, or that a divergence is measured at a time the run never reaches.

**Done when.** The module docstring gives the margin as about ten orders of magnitude, and the comment states the time at which the divergence is measured within the run. No test changes behaviour.
