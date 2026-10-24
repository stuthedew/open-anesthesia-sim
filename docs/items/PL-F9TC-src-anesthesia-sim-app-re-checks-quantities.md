---
id: PL-F9TC
title: src/anesthesia_sim/app/ re-checks quantities that core already owns: formatting.py checks mac_percent > 0 five times, playback.py checks tick_interval_s by hand instead of require_positive_finite, chart_time_base.py restates half the case-instant range twice, and simulation_view.py restates the 1-to-MAX_DISPLAYED_RUNS run count that RunCount holds
status: untriaged
feature: one-source-of-truth
added: 2026-10-19
---

**Problem.** src/anesthesia_sim/app/ re-checks quantities that core already owns: formatting.py checks mac_percent > 0 five times, playback.py checks tick_interval_s by hand instead of require_positive_finite, chart_time_base.py restates half the case-instant range twice, and simulation_view.py restates the 1-to-MAX_DISPLAYED_RUNS run count that RunCount holds
