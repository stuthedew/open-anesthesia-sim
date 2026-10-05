---
id: PL-M4M0
title: RunView._handle_reset wraps SimulationController.reset() in nothing, so the SimulationConfigurationError that equation_settings() raises at Reset when the tissue flows are stale (a CardiacOutput written onto patient.cardiac_output_l_min past set_cardiac_output, the type-only write guard PL-LBQY chose) escapes the slot after pause() and _state.reset(), leaving a half-reset run paused with no failure recorded, the readout showing a cardiac output the model never ran at and case_restarted never emitted; at step time the same stale record is presented as a SimulationNumericalError in L/s where every readout shows L/min (found reviewing PL-LBQY)
status: untriaged
added: 2026-10-05
---

**Problem.** RunView._handle_reset wraps SimulationController.reset() in nothing, so the SimulationConfigurationError that equation_settings() raises at Reset when the tissue flows are stale (a CardiacOutput written onto patient.cardiac_output_l_min past set_cardiac_output, the type-only write guard PL-LBQY chose) escapes the slot after pause() and _state.reset(), leaving a half-reset run paused with no failure recorded, the readout showing a cardiac output the model never ran at and case_restarted never emitted; at step time the same stale record is presented as a SimulationNumericalError in L/s where every readout shows L/min (found reviewing PL-LBQY)
