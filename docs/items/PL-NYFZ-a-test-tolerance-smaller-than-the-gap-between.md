---
id: PL-NYFZ
title: A test tolerance smaller than the gap between neighbouring floating-point numbers at the compared value turns an approximate check into an exact one without saying so (Error Prone's FloatingPointAssertionWithinEpsilon flags this in Java); nothing here checks for it in the simulator's tests (found while researching PL-TN0G)
status: untriaged
feature: dead-test-limits
added: 2026-11-03
---

**Problem.** A test tolerance smaller than the gap between neighbouring floating-point numbers at the compared value turns an approximate check into an exact one without saying so (Error Prone's FloatingPointAssertionWithinEpsilon flags this in Java); nothing here checks for it in the simulator's tests (found while researching PL-TN0G)
