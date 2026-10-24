---
id: PL-YHWH
title: core/parameters.py restates three rules that other core modules already own: the perfusion fractions summing to 1 (patient._require_fractions_sum_to_one), MAC within the vaporizer maximum, written twice (validation.require_within_vaporizer_maximum), and run_definition.py checks spacing_s positive and finite by hand instead of require_positive_finite
priority: P2
effort: S
status: ready
classes: defect
feature: one-source-of-truth
touches: src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/core/run_definition.py, tests/unit/test_parameters.py, tests/unit/test_run_definition.py
added: 2026-10-19
payoff: a parameter file and a running patient are held to the same perfusion, vaporizer and spacing rules, from one copy of each
verify: grep -q 'require_positive_finite' src/anesthesia_sim/core/run_definition.py
---

**Problem.** core/parameters.py restates three rules that other core modules already own: the perfusion fractions summing to 1 (patient._require_fractions_sum_to_one), MAC within the vaporizer maximum, written twice (validation.require_within_vaporizer_maximum), and run_definition.py checks spacing_s positive and finite by hand instead of require_positive_finite

**Why it matters.** Each of these rules has a home: `patient._require_fractions_sum_to_one`, `validation.require_within_vaporizer_maximum` and `validation.require_positive_finite`. A copy beside the home can drift from it. If the tolerance or the message changes in one place, a parameter file and a running patient are then held to different rules. These are input checks on model parameters, which the safety-critical standard requires to be explicit and consistent.

**Done when.** `core/parameters.py` calls the two existing helpers instead of restating the perfusion-sum and vaporizer-maximum rules. `core/run_definition.py` calls `require_positive_finite` for `spacing_s`. Each refusal keeps its current trigger, and a test pins each one.

**Checked 2026-10-24.** `core/run_definition.py` checks `not isfinite(spacing_s) or spacing_s <= 0.0` by hand and does not import `require_positive_finite`. `core/parameters.py` raises its own "is above the vaporizer maximum" message.
