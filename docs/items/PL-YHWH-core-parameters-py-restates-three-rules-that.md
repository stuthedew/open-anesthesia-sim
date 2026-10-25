---
id: PL-YHWH
title: core/parameters.py restates three rules that other core modules already own: the perfusion fractions summing to 1 (patient._require_fractions_sum_to_one), MAC within the vaporizer maximum, written twice (validation.require_within_vaporizer_maximum), and run_definition.py checks spacing_s positive and finite by hand instead of require_positive_finite
priority: P2
effort: S
status: done
classes: defect
feature: one-source-of-truth
touches: src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/core/patient.py, src/anesthesia_sim/core/run_definition.py, tests/unit/test_parameters.py, tests/unit/test_patient.py, tests/unit/test_run_definition.py
added: 2026-10-19
closed: 2026-10-25
pr: 1772
payoff: a parameter file and a running patient are held to the same perfusion, vaporizer and spacing rules, from one copy of each
verify: grep -q 'require_positive_finite' src/anesthesia_sim/core/run_definition.py
---

**Problem.** core/parameters.py restates three rules that other core modules already own: the perfusion fractions summing to 1 (patient._require_fractions_sum_to_one), MAC within the vaporizer maximum, written twice (validation.require_within_vaporizer_maximum), and run_definition.py checks spacing_s positive and finite by hand instead of require_positive_finite

**Why it matters.** Each of these rules has a home: `patient._require_fractions_sum_to_one`, `validation.require_within_vaporizer_maximum` and `validation.require_positive_finite`. A copy beside the home can drift from it. If the tolerance or the message changes in one place, a parameter file and a running patient are then held to different rules. These are input checks on model parameters, which the safety-critical standard requires to be explicit and consistent.

**Done when.** `core/parameters.py` calls the two existing helpers instead of restating the perfusion-sum and vaporizer-maximum rules. `core/run_definition.py` calls `require_positive_finite` for `spacing_s`. Each refusal keeps its current trigger, and a test pins each one.

**Checked 2026-10-24.** `core/run_definition.py` checks `not isfinite(spacing_s) or spacing_s <= 0.0` by hand and does not import `require_positive_finite`. `core/parameters.py` raises its own "is above the vaporizer maximum" message.

**Built 2026-10-25.** `core/parameters.py` holds `require_perfusion_fractions_sum_to_one` beside `FLOW_FRACTION_TOLERANCE`, and `require_one_mac_deliverable`. The patient file's schema, `AgentParameters`, the agent file's schema and `PatientCompartments` call them, so each rule is written once. A schema validator raises the rule's message as the `ValueError` Pydantic collects. `RunDefinition.evaluate_anchored` checks `spacing_s` with `require_positive_finite`, which also refuses a `bool`.

The MAC rule does not call `validation.require_within_vaporizer_maximum`, which the brief named. That helper's message is written for a dial someone set ("9% requested"), and a blind review found it misleading for an agent's MAC. The two restated copies of the MAC rule are now one function with the MAC-worded message, so the goal is met by a different route.
