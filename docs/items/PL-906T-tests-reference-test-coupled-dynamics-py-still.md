---
id: PL-906T
title: tests/reference/test_coupled_dynamics.py still copies dated measurements that docs/VERIFICATION.md § 'Independent-solution test' also records (the oracle-step tables, the peak instants, the retired constants' figures); keep one record and point the other at it
status: untriaged
feature: prose-quality
touches: tests/reference/test_coupled_dynamics.py
added: 2026-11-22
---

**Problem.** tests/reference/test_coupled_dynamics.py still copies dated measurements that docs/VERIFICATION.md § 'Independent-solution test' also records (the oracle-step tables, the peak instants, the retired constants' figures); keep one record and point the other at it

**Found by** the session that closed `PL-TV7Q`, 2026-11-22. That item removed the measured margins of the two rounding limits and pointed the module at `docs/VERIFICATION.md` § "The tests and the figures behind the comparison". It kept the dated measurements that are the reason for a chosen value other than a limit: the oracle-step tables above `ORACLE_STEP_S`, the peak instants above `ENVELOPE_HORIZON_S` and in `_worst_error_over_phases`, the sevoflurane residuals at three step lengths above `SHIPPED_STEP_S`, and the figures of the retired splitting bound. `docs/VERIFICATION.md` records several of the same figures, so the two copies can drift apart.

**Done when.** Each of those figures has one home, and the other place points at it. An edit to an existing line under `tests/reference/` waits for the project owner's read.
