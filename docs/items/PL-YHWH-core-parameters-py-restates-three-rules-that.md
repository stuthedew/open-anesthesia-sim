---
id: PL-YHWH
title: core/parameters.py restates three rules that other core modules already own: the perfusion fractions summing to 1 (patient._require_fractions_sum_to_one), MAC within the vaporizer maximum, written twice (validation.require_within_vaporizer_maximum), and run_definition.py checks spacing_s positive and finite by hand instead of require_positive_finite
status: untriaged
feature: one-source-of-truth
added: 2026-10-19
---

**Problem.** core/parameters.py restates three rules that other core modules already own: the perfusion fractions summing to 1 (patient._require_fractions_sum_to_one), MAC within the vaporizer maximum, written twice (validation.require_within_vaporizer_maximum), and run_definition.py checks spacing_s positive and finite by hand instead of require_positive_finite
