---
id: PL-VS4V
title: No record says why the perfusion-fraction allowance is 1e-12 or the cardiac-output allowance is one part in 10**9: core/rounding.py states both values, what each is measured against and how far above rounding each sits, but git log -S traces them only to v0.1.0 (875ba085) and to the matrix-exponential change (d8deea50), neither of which gives a reason
status: untriaged
feature: numbers-outside-their-valid-range
added: 2026-11-11
---

**Problem.** No record says why the perfusion-fraction allowance is 1e-12 or the cardiac-output allowance is one part in 10**9: core/rounding.py states both values, what each is measured against and how far above rounding each sits, but git log -S traces them only to v0.1.0 (875ba085) and to the matrix-exponential change (d8deea50), neither of which gives a reason
