---
id: PL-F67Q
title: tests/reference/test_coupled_dynamics.py: test_the_disagreement_does_not_shrink_with_the_step drives only three of the five gate trajectories at 0.05 s and 0.025 s, so the 5.89e-14 that EXACT_STEP_ORACLE_TOLERANCE is set against is a maximum over three; the held envelope corner, not driven there, reaches 5.46e-14 for desflurane at 0.025 s, within 8% of it, and three ventilator starts in a row reach 2.46e-14 at 0.1 s against 1.39e-14 for one (measured 2026-10-25 for PL-S86L)
status: untriaged
added: 2026-10-25
---

**Problem.** tests/reference/test_coupled_dynamics.py: test_the_disagreement_does_not_shrink_with_the_step drives only three of the five gate trajectories at 0.05 s and 0.025 s, so the 5.89e-14 that EXACT_STEP_ORACLE_TOLERANCE is set against is a maximum over three; the held envelope corner, not driven there, reaches 5.46e-14 for desflurane at 0.025 s, within 8% of it, and three ventilator starts in a row reach 2.46e-14 at 0.1 s against 1.39e-14 for one (measured 2026-10-25 for PL-S86L)
