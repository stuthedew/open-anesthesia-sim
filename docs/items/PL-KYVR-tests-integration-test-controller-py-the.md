---
id: PL-KYVR
title: tests/integration/test_controller.py: the docstring of WORST_SHARED_COLUMN_DIVERGENCE calls the 1e-13 bound an order of magnitude above the measured 2.8e-15 (it is about 1.5) and eleven orders below the displayed 1e-4 (it is nine) (found by the blind review of #1805, 2026-10-25)
priority: P3
effort: S
status: ready
classes: docs
feature: stale-source-claims
touches: tests/integration/test_controller.py
added: 2026-10-25
payoff: a reader weighing the controller test's tolerance is given its true margin above the measured value and below the displayed precision
verify: ! grep -qF 'eleven orders of magnitude below the 1e-4' tests/integration/test_controller.py && ! grep -qF 'is set an order of magnitude above that' tests/integration/test_controller.py
---

**Problem.** tests/integration/test_controller.py: the docstring of WORST_SHARED_COLUMN_DIVERGENCE calls the 1e-13 bound an order of magnitude above the measured 2.8e-15 (it is about 1.5) and eleven orders below the displayed 1e-4 (it is nine) (found by the blind review of #1805, 2026-10-25)

**Reproduced 2026-10-25.** `grep` on `main` at `b6ff4443` finds lines 3518 and 3519 of `tests/integration/test_controller.py`: the bound "is set an order of magnitude above that" and "eleven orders of magnitude below the 1e-4". 1e-13 over 2.8e-15 is about 36, about 1.5 orders; 1e-4 over 1e-13 is nine orders.

**Why it matters.** The docstring is the reason for the tolerance. A reader who believes it has eleven orders of headroom may loosen it, and a reader who believes it is ten times the measured value may tighten it into a flaky test.

**Done when.** The docstring gives both margins correctly. No test changes behaviour.
