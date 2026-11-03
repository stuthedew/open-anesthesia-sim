---
id: PL-R4M6
title: arming.arm is 297 lines, and PL-3D2F threaded its owner-ask fast path through it as five if owner_ask checks; split it into stages that the full answer and the fast path each compose
status: untriaged
feature: guard-code-structure
added: 2026-11-03
---

**Problem.** arming.arm is 297 lines, and PL-3D2F threaded its owner-ask fast path through it as five if owner_ask checks; split it into stages that the full answer and the fast path each compose
