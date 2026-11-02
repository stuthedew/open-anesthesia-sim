---
id: PL-VXM0
title: test_step_refinement_converges asserts a 0.5% relative / 1e-8 absolute tolerance that its own 1e-14 gap assertion makes redundant: any gap failing the first exceeds 1e-8 and so fails the second. Decide whether to keep the 0.5% check as the fallback a fork with an approximate method would use (and say so in the test) or remove it, and whether docs/MODEL.md's requirement to document a 'release comparison tolerance' still has a purpose
status: untriaged
added: 2026-11-02
---

**Problem.** test_step_refinement_converges asserts a 0.5% relative / 1e-8 absolute tolerance that its own 1e-14 gap assertion makes redundant: any gap failing the first exceeds 1e-8 and so fails the second. Decide whether to keep the 0.5% check as the fallback a fork with an approximate method would use (and say so in the test) or remove it, and whether docs/MODEL.md's requirement to document a 'release comparison tolerance' still has a purpose
